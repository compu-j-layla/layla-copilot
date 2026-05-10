#!/bin/bash
curl -fsSL https://bun.sh/install | bash && ln -s $HOME/.bun/bin/bun /usr/local/bin/bun
bun install
python3 -m uvicorn backend.main:app --reload --log-level debug &
bun run start
wait -n
exit $?