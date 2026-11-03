# Security Policy

## Supported versions

| Version | Supported |
|---------|:---------:|
| 0.1.x | yes |

## Reporting a vulnerability

Please do not open a public issue for security problems.

Report vulnerabilities privately to the maintainers with:

- Description of the issue and the impact you expect
- Steps to reproduce
- Version or commit you tested
- Any proof of concept, with real tokens and session strings removed

You can expect an acknowledgement within a few days and a fix or mitigation plan once the report is confirmed.

## Handling secrets

- Never commit `.env`, `*.session`, `*.session-journal`, or BotFather tokens.
- Rotate any token that was ever exposed in a commit, chat, or log.
- `sample.env` only contains placeholders.
