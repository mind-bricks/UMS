FROM python:3.5-slim

ENV SECRETS_REPO=

ENV SECRETS_DIR=/secrets

ENV SECRETS_FILE=user_settings.py

EXPOSE 80

COPY . /mdd

WORKDIR /mdd

RUN bash scripts/build-prod

CMD bash scripts/run-prod
