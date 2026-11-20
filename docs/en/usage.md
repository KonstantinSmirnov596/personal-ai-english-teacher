# Using Personal AI English Teacher

Personal AI English Teacher has four sections in the top bar: Conversation, Reading, Vocabulary and History. Settings are behind the sliders icon on the right. The interface, corrections, translations and tips are in your language (Spanish or Portuguese); the tutor always speaks General American English.

## First start

The first time, a setup wizard opens: language, hardware check, models, a short measurement, microphone, voice, API connection and level. You can open it again at any time from Settings → Performance → "Run the wizard again". See `hardware.md` for the hardware check and `api-keys.md` for the connection.

## Conversation

<a id="conversation"></a>

1. Choose a scenario (a job interview, small talk, a meeting…) and your level, then click "Start conversation". The tutor speaks first.
2. Press **Space** to start answering and **Space** again to send. **Esc** cancels the answer. While the tutor speaks, Space interrupts it.
3. Your answer appears as text, the tutor answers aloud and in text.

Turn modes (the switch in the bottom panel):

- **Manual**: Space starts and ends each answer. Best with speakers.
- **Automatic**: just speak; your answer is sent after a pause (Settings → Conversation sets the pause). With speakers the microphone is closed while the tutor speaks; with headphones you can interrupt the tutor by voice (Settings → Conversation → "I use headphones").

Under each tutor line: **Replay**, **Slower** and **Translate**. In the bottom panel: **Hint** (ideas for your answer), **How do I say…?** (type a phrase in your language and get it in English) and **Finish**.

### Corrections

Mistakes in your answer are underlined. The card shows the fix and a short explanation in your language, and a more natural way to say it. Choose when they appear in the bottom panel or in Settings → Corrections: instantly, on click, at the end of the session, or off. Clear pronunciation mistakes are marked in the conversation too (in the `compacto` profile this is off by default; Settings → Corrections).

### Summary

"Finish" shows the session summary: the most important takeaway, all corrections, short speaking exercises built from your mistakes ("Say it in English: …"), recurring mistakes over several sessions, sounds to practice, and the tutor's useful phrases, which you can add to your vocabulary.

## Reading

<a id="reading"></a>

Reading checks your pronunciation sound by sound, without a language model (it works without an API connection).

1. Listen to the phrase ("Reference", "Slow reference") if you like.
2. Press **Space** or the microphone, read the phrase aloud, press **Space** again.
3. Words with a problem are marked: "close" or "error". Click a word to see which sound was heard instead of which, a tip in your language, and buttons to hear the word and repeat only that word.
4. If a mark is wrong, click "That was right": the check becomes less strict for that sound.

"Sounds to practice" lists the sounds you had trouble with in the last 7 days. Each phrase names the sounds it trains; "Previous" and "Next phrase" move through the 30 phrases.

## Vocabulary

<a id="vocabulary"></a>

Phrases you add from a summary come back for review on a growing schedule. Read the English phrase, think of the meaning, click "Show translation", then "I remember" or "I don't remember".

## History

<a id="history"></a>

Every session with its transcript, corrections and summary. You can open, export (JSON or CSV) or delete a session; deleting also removes its recordings.

## Settings

<a id="settings"></a>

| Section | What it holds |
| --- | --- |
| API connections | Your providers and keys; one is active (`api-keys.md`) |
| Language | Spanish or Portuguese for the interface and explanations, switched without a restart |
| Sound and voice | Microphone, speakers, the tutor's voice and speed, noise suppression |
| Conversation | Level, turn mode, pause length in automatic mode, the tutor's recasts, headphones |
| Corrections | When corrections appear; pronunciation marks in the conversation |
| Performance | Profile (`completo`, `compacto`, automatic), last measurement, the wizard again |
| Data | How long recordings are kept, export, "Delete all data", detailed log |

## Keyboard

| Key | Conversation | Reading |
| --- | --- | --- |
| Space | Start, send, interrupt | Start and stop recording |
| Esc | Cancel the answer | Cancel the recording |
