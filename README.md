# Layla Smart Glasses Copilot

Low-latency meeting copilot for AR smart glasses. Streams live audio, applies on-device trigger detection and cloud LLM reasoning, and surfaces contextual prompts through a privacy-first HUD integration.

## Usage
Make sure you have installed and set-up the following:
- [Node.js](https://nodejs.org/en/download/)
- [Bun](https://bun.sh/docs/installation)
- [ngrok](https://ngrok.com/download/)

### Installing dependencies
Create a local clone of this repository with
```bash
$ git clone --single-branch https://github.com/compu-j-layla/layla-copilot/tree/feature/v1.1.0
```
`cd` into the directory containing the repository and run
```bash
$ python -m pip freeze > requirements.txt
```
to install Python dependencies.
Run
```bash
$ bun install
```
to install other dependencies.

### Setting up the app
