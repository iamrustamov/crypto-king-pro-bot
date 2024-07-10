from contextlib import suppress


class Repository:

    def __init__(self):
        self.storage = set()

    async def add(self, key: str) -> None:
        self.storage.add(key)

    async def is_exist(self, key) -> bool:
        return key in self.storage

    async def delete(self, key) -> None:
        with suppress(KeyError):
            self.storage.remove(key)
