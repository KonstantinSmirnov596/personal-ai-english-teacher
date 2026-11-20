# Security policy

## Supported versions

Only the latest release receives fixes.

## Reporting a vulnerability

Please do not open a public issue for a security problem. Use GitHub's private vulnerability reporting on this repository ("Security" tab → "Report a vulnerability"). Describe the problem, the version, and the steps to reproduce it. Never include a real API key; use a placeholder.

You can expect an answer within two weeks. Once a fix is released, the report can be published with credit to you, if you want.

## What matters most

Personal AI English Teacher is a local desktop app. Its security relies on a few promises; a way to break any of them is a vulnerability:

- **API keys** are stored only in the Windows Credential Manager. They must never reach a file, the database, a log, the window (beyond the last four characters) or any host other than the provider of that connection.
- **The local server** listens on `127.0.0.1` only and accepts requests only from the app window: a one-time launch token, a session cookie, `Origin` and `Host` checks for HTTP and WebSocket, no CORS. Another website open in a browser, or another local program without the token, must not be able to read data or act through it.
- **Network traffic** at run time goes only to the base URL of the active LLM connection. Audio never leaves the computer.
- **LLM output** is untrusted: it is inserted into the window only as text and its JSON is validated. A model answer that runs script in the window is a vulnerability.
- **Logs and diagnostics archives** contain no keys and, by default, no conversation text.

Out of scope: problems that need administrator access to the computer or full control of the user's account, and vulnerabilities in the LLM providers themselves.
