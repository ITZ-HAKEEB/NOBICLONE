# Contributing to KanhaClone

Thanks for taking the time to contribute.

## Before you start

1. Fork the repository and create a branch off `main`.
2. Keep Python at 3.11 and Node.js at 20. PyTgCalls needs Node.js 20.
3. Copy `sample.env` to `.env` and fill in your own values. Never commit `.env` or `*.session` files.

## Local setup

```bash
git clone https://github.com/Kanha-Team/KanhaClone KanhaClone
cd KanhaClone
```

```bash
apt update
apt install -y git curl ffmpeg python3-venv python3-pip
```

```bash
python3 -m venv venv
source venv/bin/activate
pip install uv
uv pip install .
```

```bash
bash start
```

## Guidelines

- Follow the style already used in the file you are editing.
- Keep master bot commands in `KanhaClone/plugins/` and cloned bot handlers in `KanhaClone/cplugin/`.
- Add new source providers under `KanhaClone/platforms/`.
- Do not hardcode API keys, tokens, or session strings.
- Add user-facing strings to `strings/langs/en.yml` instead of inline text.
- Every source file keeps the Kanha-Team copyright header and is released under the GNU v3.0 License Agreement.

## Reporting bugs

Open an issue with:

- What you did
- What you expected
- What happened
- Relevant log output with tokens and session strings removed

## Pull requests

- One focused change per pull request.
- Describe the change and how you tested it.
- By contributing you agree that your work is licensed under the GNU v3.0 License Agreement.
