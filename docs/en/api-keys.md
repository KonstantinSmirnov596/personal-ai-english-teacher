# API keys and providers

The tutor's replies, the corrections, translations and the session summary come from a large language model (LLM) at a provider you choose. Voice Tutor sends it only the text of the conversation: never audio, never your name. You pay the provider directly; Voice Tutor has no account and no fees of its own.

## Choosing a provider

The connection window has ready-made templates. Every value in them was checked against the provider's documentation (`docs/reports/providers.md`).

| Template | Kind | Key | Notes |
| --- | --- | --- | --- |
| DeepSeek | Cloud | Required | Prepaid balance |
| OpenAI | Cloud | Required | Spend limits per project |
| OpenRouter | Cloud | Required | One key for models of many companies; you type the model name (`vendor/model`) |
| Ollama | Local | Not needed | Runs on your computer; shares the graphics card with speech recognition (see below) |
| LM Studio | Local | Not needed | Runs on your computer; same caveat as Ollama |
| Other OpenAI-compatible | Any | Usually | Any service with an OpenAI-compatible `chat/completions` endpoint |

## Creating a key with a spending limit

Create a separate key just for Voice Tutor and give it a limit, so a mistake can never cost more than you decided.

<a id="deepseek"></a>
### DeepSeek

1. Sign in at [platform.deepseek.com](https://platform.deepseek.com) and open "API keys"; create a key ([DeepSeek: your first API call](https://api-docs.deepseek.com/)).
2. Top up a small amount. DeepSeek works with a prepaid balance: usage is deducted from it, and when it is empty the provider answers "insufficient balance" (HTTP 402) instead of charging more ([error codes](https://api-docs.deepseek.com/quick_start/error_codes)). The balance itself is your limit.

<a id="openai"></a>
### OpenAI

1. In the OpenAI platform, create a project for Voice Tutor and create a secret key inside that project ([managing projects](https://help.openai.com/en/articles/9186755-managing-projects-in-the-api-platform)).
2. Set a monthly spend limit on the project and turn on "Enforce a hard limit": requests then fail once the limit is reached, instead of only sending an alert ([spend limits](https://developers.openai.com/api/docs/guides/spend-limits)).

<a id="openrouter"></a>
### OpenRouter

1. Create a key in the OpenRouter dashboard and give it a credit limit, optionally resetting daily, weekly or monthly ([capping keys](https://openrouter.ai/docs/guides/best-practices/capping-shared-agent-keys)).
2. Choose a model on OpenRouter and type its id (for example `vendor/model-name`) in the "Model" field of the connection.

<a id="local"></a>
### Ollama and LM Studio

Local servers need no key and send nothing to the internet. A language model on your own graphics card, however, competes with speech recognition, the tutor's voice and the pronunciation check for video memory. With 6–8 GB only a small model fits, and the quality of corrections drops. If you try it, choose the `compacto` profile in Settings → Performance and a small model.

## Adding the key in the app

1. Open Settings → API connections → Add connection (the first-run wizard shows the same form on step 7).
2. Choose the template, paste the key into "API key" and click "Save", then "Test". The test sends one short request and shows the time it took or the provider's error.
3. The first connection becomes the active one. With several connections, the round button in the table chooses the active one; the change applies from the next reply.

The key is stored in the Windows Credential Manager, not in a file. The window only ever shows its last four characters. Never send a key to anyone, including in a bug report.

## What a conversation costs

<a id="cost"></a>

Providers charge per token. A token is a piece of a word; DeepSeek, for example, counts roughly 0.3 tokens per English character ([token usage](https://api-docs.deepseek.com/quick_start/token_usage)). Each of your answers starts two requests: the tutor's reply and the correction of your sentence (none when corrections are off). The session summary is one more request, and each hint, translation or "How do I say…?" is one more.

Measured with the test provider (`scripts/token_usage.py`, a job-interview session at level B1, 10 answers of 10–15 words, corrections on):

| Request | Input tokens | Output tokens, at most |
| --- | --- | --- |
| Tutor's reply | 850 for the first answer, growing by about 50 per answer (1300 at the tenth) | 400 |
| Correction of your answer | about 1450 | 800 |
| Session summary | about 1000 | 1200 |
| Hint | about 300 | 600 |
| A whole 10-answer session with one hint | about 26,000 | usually far below the maximum |

Cost of one session ≈ (input tokens × input price + output tokens × output price) summed over all requests. Prices change often; check your provider's price page and the usage page of your account after the first sessions.

## When something goes wrong

| What the app says | Usual cause | What to do |
| --- | --- | --- |
| The provider rejected the key or the account has no balance | Wrong key, key deleted, balance empty, spend limit reached | Check the key and the balance or limit at the provider |
| The provider asks to wait | Too many requests per minute | Wait a minute; the "Retry" button repeats the reply |
| The provider cannot be reached | No internet, firewall, wrong base URL | Check the connection; for local servers, check that Ollama or LM Studio is running |
| The provider returned an error or an incomplete answer | Model name wrong, model does not support the requested format, provider outage | Check the model name; try another model or provider |
