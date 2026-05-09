#!/bin/bash
bun install
uvicorn backend.main:app --reload --log-level debug &
bun run start
wait -n
exit $?