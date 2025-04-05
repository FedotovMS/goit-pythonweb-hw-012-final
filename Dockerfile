FROM python:3.13-slim

WORKDIR /app


RUN apt-get update && apt-get install -y \
    gcc g++ libc-dev libffi-dev libssl-dev \
    && pip install poetry \
    && poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml /app/

RUN poetry install --no-dev --no-interaction --no-ansi

COPY . /app/

CMD ["python3", "main.py"]


