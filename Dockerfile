# BUILD
# docker build . --file Dockerfile --tag healthy_antilope
#
# RUN
# docker run --name healthy_antilope -d --restart=always healthy_antilope
# Separate "build" image
FROM python:3.10 as compile-image
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# "Run" image
FROM python:3.10
COPY --from=compile-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY src /app/src
COPY .env /app/.env
ENV PYTHONPATH "${PYTHONPATH}:/app/src"
CMD ["python", "-m", "src"]