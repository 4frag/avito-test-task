FROM python:3.13-slim

RUN apt update && apt install -y --no-install-recommends \
    make
RUN pip install poetry

WORKDIR /app

# Копируем файлы зависимостей и устанавливваем их
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-ansi --no-root

# Создаем non-root пользователя и группу
RUN addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 --gid 1001 appuser

COPY --chown=appuser:appuser . .
USER appuser

# RUN make migrate

# EXPOSE 8080
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]