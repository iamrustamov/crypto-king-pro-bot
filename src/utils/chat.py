import logging
from asyncio import sleep

from attr import dataclass
from openai import AsyncOpenAI
from openai.types.beta import Thread

__all__ = ["Chat", "ChatError", "ChatResponse"]

_logger = logging.getLogger(__name__)


class ChatError(Exception):
    def __init__(self, chat_id: str, message: str) -> None:
        self.chat_id = chat_id
        super().__init__(message)


@dataclass(slots=True, frozen=True)
class ChatResponse:
    thread_id: str
    text: str
    tokens_used: int


class Chat:
    def __init__(self, client: AsyncOpenAI, assistant_id: str):
        self.client = client
        self.assistant_id = assistant_id

    async def create_thread(self) -> Thread:
        return await self.client.beta.threads.create()

    async def ask(self, thread_id: str, message: str) -> ChatResponse:
        try:
            await self.client.beta.threads.messages.create(
                thread_id=thread_id, role="user", content=message
            )
            run = await self.client.beta.threads.runs.create(
                thread_id=thread_id, assistant_id=self.assistant_id
            )
            i = 0
            while (run.status == "queued" or run.status == "in_progress") and i < 60:
                run = await self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id, run_id=run.id
                )
                i += 1
                await sleep(5)
            if run.status == "queued" or run.status == "in_progress":
                text = "Упс, что-то сломалось. Попробуйте еще раз..."
            else:
                messages = await self.client.beta.threads.messages.list(
                    thread_id=thread_id
                )
                text = messages.data[0].content[0].text.value
            return ChatResponse(thread_id, text, run.usage.total_tokens)
        except Exception as e:
            _logger.exception(e)
            return ChatResponse(
                thread_id, text=f"Error: {e}", tokens_used=0
            )  # TODO: count tokens
