# TESTER
FROM python:3.12-alpine AS tester

RUN ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime
RUN echo Asia/Seoul > /etc/timezone

WORKDIR /app
COPY src ./src
COPY pyproject.toml poetry.lock README.md ./

RUN pip install poetry
RUN poetry config virtualenvs.in-project true
RUN poetry config virtualenvs.path "./.venv"

RUN poetry install

ENTRYPOINT ["poetry", "run", "pytest", "/app/src/tests", "-v"]


# RUNNER
FROM python:3.12-alpine AS runner

RUN ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime
RUN echo Asia/Seoul > /etc/timezone

WORKDIR /app
COPY --from=tester /app .

RUN pip install poetry
RUN poetry config virtualenvs.in-project true
RUN poetry config virtualenvs.path "./.venv"

RUN poetry install

ENTRYPOINT ["poetry", "run", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]