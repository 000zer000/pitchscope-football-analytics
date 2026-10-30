FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.12.10 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH" PYTHONPATH=/app/backend
COPY backend backend
COPY alembic.ini .
COPY scripts/seed-test.py scripts/seed-test.py
COPY assets assets
COPY data/source-lock.json data/source-lock.json
RUN useradd --create-home app && chown -R app:app /app
USER app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
