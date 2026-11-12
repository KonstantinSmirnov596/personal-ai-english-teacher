# LLM provider templates

Plan item 0.8. Every template value below was checked in the provider's official documentation on 2026-11-12; quotes are short excerpts. The templates live in `voicetutor/data/providers.json`; `tests/test_providers.py` keeps them in sync with the table.

## What the app needs from a provider

- OpenAI-compatible Chat Completions: `POST {base_url}/chat/completions`, `Authorization: Bearer <key>`, body `{model, messages, stream, ...extra_params}`.
- Streaming over SSE with `choices[0].delta.content` and a final `data: [DONE]`. Comment lines that start with `:` (keep-alives) are skipped; a chunk with a top-level `error` ends the stream as `llm_bad_response`.
- A JSON answer for the corrector, summary and helpers. A connection's `json_format` decides how it is asked for: `json_object` sends `response_format: {"type": "json_object"}`; `json_schema` sends `response_format: {"type": "json_schema", "json_schema": {"name", "schema"}}` with the pydantic schema of the expected answer; `none` sends nothing. Every JSON prompt names the format (DeepSeek requires the word "json"; OpenAI's JSON mode checks for "JSON", so the stage 1 prompts spell it in capitals) and the answer is validated and retried once when empty or invalid.
- Reasoning (thinking) off or minimal: the tutor's first sentence must come quickly.

## Templates

| Id | Name | Kind | Base URL | Default model | JSON format | Streaming | Reasoning switch (extra parameters) | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `deepseek` | DeepSeek | cloud | `https://api.deepseek.com` | `deepseek-flash` (also `deepseek-v4-pro`) | `json_object` (only `text` and `json_object` are allowed) | SSE, `data: [DONE]`, `: keep-alive` comments while queued | `{"thinking": {"type": "disabled"}}` — thinking is on by default | [Quick start](https://api-docs.deepseek.com/), [Models and pricing](https://api-docs.deepseek.com/quick_start/pricing), [Thinking mode](https://api-docs.deepseek.com/guides/thinking_mode), [Chat completion reference](https://api-docs.deepseek.com/api/create-chat-completion), [JSON output](https://api-docs.deepseek.com/guides/json_mode), [Rate limit](https://api-docs.deepseek.com/quick_start/rate_limit) |
| `openai` | OpenAI | cloud | `https://api.openai.com/v1` | `gpt-6-luna` | `json_schema` (structured outputs; JSON mode is not listed for this model) | SSE, `chat.completion.chunk`, `data: [DONE]` | `{"reasoning_effort": "none"}` — the model defaults to `medium` | [Models](https://developers.openai.com/api/docs/models), [gpt-6-luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [Chat Completions reference](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create), [Structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs), [Responses vs Chat Completions](https://developers.openai.com/api/docs/guides/migrate-to-responses) |
| `openrouter` | OpenRouter | cloud | `https://openrouter.ai/api/v1` | none: the user picks a `vendor/model` id | `json_object` | SSE, `data: [DONE]`, `: OPENROUTER PROCESSING` comments, mid-stream `error` chunks | `{"reasoning": {"effort": "none"}, "provider": {"require_parameters": true}}` | [Quickstart](https://openrouter.ai/docs/quickstart), [Streaming](https://openrouter.ai/docs/api/reference/streaming), [Parameters](https://openrouter.ai/docs/api/reference/parameters), [Provider selection](https://openrouter.ai/docs/guides/routing/provider-selection), [Reasoning tokens](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens) |
| `ollama` | Ollama | local | `http://127.0.0.1:11434/v1` | none: the user picks a pulled model | `json_schema` (structured outputs through `response_format`) | SSE | `{"reasoning_effort": "none"}` for thinking models that allow it | [OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility), [Structured outputs](https://docs.ollama.com/capabilities/structured-outputs), [Thinking](https://docs.ollama.com/capabilities/thinking), [FAQ: bind address](https://docs.ollama.com/faq) |
| `lmstudio` | LM Studio | local | `http://127.0.0.1:1234/v1` | none: the model loaded in LM Studio | `json_schema` (the only documented structured format) | `stream` parameter documented | not documented for the OpenAI-compatible endpoint; no extra parameters | [OpenAI compatibility](https://lmstudio.ai/docs/developer/openai-compat), [Chat completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions), [Structured output](https://lmstudio.ai/docs/developer/openai-compat/structured-output), [Server quickstart](https://lmstudio.ai/docs/developer/rest/quickstart), [Authentication](https://lmstudio.ai/docs/developer/core/authentication) |
| `openai_compatible` | Other OpenAI-compatible | custom | entered by the user | entered by the user | `json_object` | as provided | entered by the user | Same protocol as the rows above; nothing provider-specific is assumed |

## Facts per provider

### DeepSeek

- Base URL `https://api.deepseek.com`, current models `deepseek-flash` and `deepseek-v4-pro`; `deepseek-chat` and `deepseek-reasoner` were announced for discontinuation on 2026-07-24 ([updates](https://api-docs.deepseek.com/updates)).
- "Thinking mode is enabled by default" ([thinking mode](https://api-docs.deepseek.com/guides/thinking_mode)); the body field `{"thinking": {"type": "disabled"}}` turns it off. `reasoning_effort: "none"` is an alternative.
- `response_format` "Must be one of `text` or `json_object`" ([reference](https://api-docs.deepseek.com/api/create-chat-completion)). JSON output needs the word "json" in the prompt and may come back blank; the docs advise to "handle blank `content`" — the app retries once ([JSON output](https://api-docs.deepseek.com/guides/json_mode)).
- Token size for cost estimates: "1 English character ≈ 0.3 token" ([token usage](https://api-docs.deepseek.com/quick_start/token_usage)).

### OpenAI

- Chat Completions "remains supported" next to the Responses API ([migration guide](https://developers.openai.com/api/docs/guides/migrate-to-responses)).
- The cheapest current model is `gpt-6-luna`, described as "Our most efficient model for focused, high-volume tasks" ([models](https://developers.openai.com/api/docs/models)); it supports Chat Completions, streaming and structured outputs, and `reasoning.effort` values from `none` to `max` with `medium` as default ([gpt-6-luna](https://developers.openai.com/api/docs/models/gpt-6-luna)).
- JSON mode (`json_object`) is documented as the "older JSON mode" and the docs prefer `json_schema` ([reference](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create), [structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs)). The template therefore uses `json_schema`.
- `max_tokens` is deprecated in favour of `max_completion_tokens` and "is not compatible with" reasoning models ([reference](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)). The app still sends `max_tokens`; with `reasoning_effort: "none"` this is accepted by Chat Completions, but if a user picks a model that rejects it, the provider error is shown. Checking this needs a paid request, so it is part of the `live` suite (owner task).

### OpenRouter

- `Authorization: Bearer <OPENROUTER_API_KEY>`; attribution headers are optional and not sent (the app sends no identifying data) ([quickstart](https://openrouter.ai/docs/quickstart)).
- Unsupported parameters are ignored by default; `provider.require_parameters: true` limits routing to providers that support `response_format` ([provider selection](https://openrouter.ai/docs/guides/routing/provider-selection)).
- `reasoning: {"effort": "none"}` "Disables reasoning entirely"; models with mandatory reasoning reject it, and the user then edits the extra parameters ([reasoning tokens](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens)).
- No default model: OpenRouter documents no default, and model ids change often.

### Ollama

- OpenAI-compatible endpoint at `http://localhost:11434/v1`; "The client requires an API key value, but Ollama ignores it" ([OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility)). The app allows an empty key for `127.0.0.1` and `localhost` and then sends no `Authorization` header.
- The server listens on `127.0.0.1:11434` by default ([FAQ](https://docs.ollama.com/faq)); the template uses `127.0.0.1` rather than `localhost`, so Windows does not try IPv6 `::1` first.
- "Structured outputs work through the OpenAI-compatible API via `response_format`" ([structured outputs](https://docs.ollama.com/capabilities/structured-outputs)).
- A local model shares VRAM with speech recognition, synthesis and the phoneme model: on 6–8 GB only a small model fits and correction quality drops. The first-run wizard (stage 3) says so. The `e2e` suite does not need Ollama.

### LM Studio

- Endpoints include `/v1/chat/completions`; examples use `http://localhost:1234/v1`, and 1234 is the default port ([OpenAI compatibility](https://lmstudio.ai/docs/developer/openai-compat), [server quickstart](https://lmstudio.ai/docs/developer/rest/quickstart)).
- "By default, LM Studio does not require authentication for API requests" ([authentication](https://lmstudio.ai/docs/developer/core/authentication)): the key may stay empty.
- Structured output is documented only as `"type": "json_schema"` ([structured output](https://lmstudio.ai/docs/developer/openai-compat/structured-output)); `json_object` is not documented, so the template uses `json_schema`.
- Not confirmed: whether LM Studio listens on `127.0.0.1` as well as `localhost` in every configuration. If the test button fails, the user can change the URL to `http://localhost:1234/v1`.

## Decisions taken from this review

| Decision | Reason |
| --- | --- |
| New per-connection setting `json_format` (`json_object`, `json_schema`, `none`), database migration 4 | LM Studio documents only `json_schema`, OpenAI prefers it; DeepSeek accepts only `json_object` |
| Empty API key allowed for `127.0.0.1` and `localhost`, no `Authorization` header then | Ollama ignores the key; LM Studio does not require one by default |
| OpenAI template model `gpt-6-luna` with `reasoning_effort: "none"` | Cheapest current model; reasoning is on (`medium`) by default and would delay the first sentence |
| OpenRouter template without a default model and with `require_parameters` | No documented default; without it a provider may silently ignore `response_format` |
| All six templates are included | Every value in the table is confirmed in official docs; the single unconfirmed point (LM Studio on `127.0.0.1`) has a documented fallback (`localhost`) |
