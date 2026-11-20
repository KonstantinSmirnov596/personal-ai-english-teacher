# Changelog

All notable changes are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [0.1.1] - 2026-11-20

### Fixed

- The installer could stop right after installing Python with "Python was installed but uv cannot find it". Windows PowerShell sometimes ended the `uv python find` step early and read its exit code as a failure; the installer now waits for the step to finish.

## [0.1.0] - 2026-11-20

First public version.

### Added

- Spoken conversation practice with an AI tutor that speaks only General American English: scenarios, levels A2–C1, manual and automatic turns, interrupting by voice with headphones.
- Interface, corrections, translations, hints and tips in Latin American Spanish (`es-419`) and Brazilian Portuguese (`pt-BR`), switchable without a restart. New learner languages are files only.
- Corrections of grammar, vocabulary and phrasing with explanations in the learner's language; session summary with a key takeaway, speaking exercises, recurring mistakes over sessions and useful phrases for the vocabulary.
- "Reading": sound-by-sound pronunciation feedback on 30 phrases, with catalogs of the mistakes typical for Spanish and Portuguese speakers (substitutions, missing and inserted sounds such as "estart"), and cautious pronunciation marks in the conversation.
- Vocabulary review on a growing schedule; history with export to JSON and CSV.
- API connections to any OpenAI-compatible provider, with templates for DeepSeek, OpenAI, OpenRouter, Ollama and LM Studio; keys stored only in the Windows Credential Manager.
- Hardware profiles `completo` and `compacto`, a first-run wizard with a hardware check, a short benchmark and a microphone check, and clear messages instead of crashes when video memory runs short.
- Installer for users without Python (`install.cmd`): requirements check before any download, pinned and checksummed downloads, shortcuts; `uninstall.cmd`.
- User documentation in English, Spanish and Portuguese.

### Privacy

- Speech recognition, speech synthesis and pronunciation assessment run on the user's NVIDIA GPU; audio never leaves the computer.
- At run time the only network traffic goes to the active LLM provider; no telemetry, update checks or external assets.
