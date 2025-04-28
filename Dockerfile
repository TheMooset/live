# syntax=docker.basalam.dev/docker/dockerfile:1.4.2
FROM docker.basalam.dev/basalam/uvicorn-gunicorn:python3.8

ENV PYTHONUNBUFFERED=1
ENV VARIABLE_NAME app
ENV MODULE_NAME app
ENV APP_MODULE app:app
ENV TZ=Asia/Tehran
ENV PYTHONPATH: "${PYTHONPATH}:$(pwd)"

RUN rm /etc/apt/apt.conf.d/docker-clean -f

## install python3-dev if needed 
# RUN --mount=type=cache,target=/var/cache/apt apt-get update && \
#     apt-get install -y --no-install-recommends python3-dev

WORKDIR /app

COPY --link ./requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

COPY --link ./src .