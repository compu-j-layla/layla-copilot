#!/bin/bash

ngrok http 3000 &
uvicorn backend.main:app --reload --log-level debug &
bun run start
wait -n
exit $?