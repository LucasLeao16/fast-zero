FROM python:3.12-slim

ENV POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir poetry

# Instala só as dependências de produção primeiro, para aproveitar o cache
# de camadas: o código pode mudar sem reinstalar tudo.
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --only main --no-root

COPY . .

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
