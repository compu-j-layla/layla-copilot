FROM oven/bun:1-alpine
WORKDIR /app
COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile
COPY . ./
FROM ubuntu:latest
COPY run.sh run.sh
CMD ./run.sh