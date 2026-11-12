## What changes

<!-- One topic per pull request. Link the issue it closes, if any. -->

## How it was tested

- [ ] `scripts\ci_local.ps1` passes (ruff, fast suite)
- [ ] `scripts\test.ps1 gpu` (when speech, pronunciation or models are touched)
- [ ] `scripts\test.ps1 e2e` (when the window is touched)

## Checklist

- [ ] No API keys, personal data, user paths or recordings in the diff
- [ ] No new network access at run time (only the active LLM provider)
- [ ] User-facing texts added in both `web/i18n/es-419.js` and `web/i18n/pt-BR.js` (and in `voicetutor/data/l1/*/` for core messages)
- [ ] Documentation updated in `docs/en`, `docs/es` and `docs/pt-BR` when behaviour visible to users changed
