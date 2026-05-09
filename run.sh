#!/bin/bash

uvicorn backend.main:app --reload --log-level debug &
bun run start
wait -n
exit $?