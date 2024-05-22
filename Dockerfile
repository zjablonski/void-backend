FROM python:3.12

WORKDIR /app

RUN addgroup --system flask && adduser --system flask

RUN python -m pip install --user pipx \
    && python -m pipx ensurepath --force

RUN . /root/.profile && pipx install poetry

COPY pyproject.toml poetry.lock /app/

RUN . /root/.profile \
    && poetry config virtualenvs.create false \
    && poetry update \
    && poetry install --only main --no-interaction --no-ansi

COPY . /app

RUN chmod +x /app/entrypoint.sh
RUN chown -R flask:flask /app

USER flask
ENTRYPOINT ["/app/entrypoint.sh"]
