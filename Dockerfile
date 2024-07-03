FROM python:3.11-alpine@sha256:1f2d9c16536c0610cb32a85c679271244e8a344825e4acd8d6a51ea7d564ce71 as base

LABEL org.opencontainers.image.authors="Myles Gray"
LABEL org.opencontainers.image.source='https://github.com/mylesagray/discord-power-bot'
LABEL org.opencontainers.image.url='https://github.com/mylesagray/discord-power-bot'
LABEL org.opencontainers.image.documentation='https://github.com/mylesagray/discord-power-bot'

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

FROM base AS python-deps

# Install pipenv and compilation dependencies
RUN python -m pip install pipenv
RUN apk add libxml2-dev g++ gcc libxslt-dev

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Create and switch to a new user
RUN adduser -S appuser
WORKDIR /home/appuser
USER appuser

# Install application into container
COPY app/ .

CMD ["python", "bot.py"]
