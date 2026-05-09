FROM oven/bun:1-alpine
WORKDIR /app
COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile
COPY . ./
FROM python:3
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt
COPY . .
FROM ubuntu:latest
RUN ["chmod", "+x", "/run.sh"]
COPY run.sh run.sh
CMD ./run.sh