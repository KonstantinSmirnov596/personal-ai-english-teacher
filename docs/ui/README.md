# Mockups and visual design

Four static files show the target look of the screens, with Latin American Spanish as the example learner language. They are layout samples, not app code: styles are inline, data is written by hand, there are no scripts.

| File | Screen |
| --- | --- |
| `main.html` | Conversation: feed, marks, correction card, bottom panel |
| `connections.html` | Settings → API connections |
| `reading.html` | Reading: phrase, word breakdown, per-sound statistics |
| `summary.html` | Session summary |

The mockups load fonts from Google Fonts. The app must not: Inter and JetBrains Mono (OFL) are put into `web/fonts/` at install time and loaded through `@font-face`.

## Tokens

CSS variables in `web/css/tokens.css`; no colours outside this list.

| Variable | Value | Where |
| --- | --- | --- |
| `--ground` | `#F5F6F6` | Window background |
| `--surface` | `#FFFFFF` | Header, cards, bottom panel |
| `--surface-2` | `#ECEFF0` | Active tab, secondary button background |
| `--ink` | `#15181A` | Main text |
| `--ink-2` | `#3D4449` | Explanation text in cards |
| `--muted` | `#5A6166` | Captions, inactive tabs, state |
| `--faint` | `#8A9196` | Idle waveform, dashed borders |
| `--line` | `#DFE2E3` | Borders |
| `--line-strong` | `#C9CED1` | Input borders |
| `--accent` | `#2F54C8` | Recording, active connection, corrections, primary button |
| `--accent-hover` | `#1E3A94` | Hover on links and the primary button |
| `--accent-soft` | `#F0F3FB` | Background of the "key takeaway" block |
| `--pron` | `#8F3F06` | Text and underline of pronunciation marks |
| `--pron-soft` | `#FBE3CC` | Fill of a word with a pronunciation error |

Typography: Inter 400, 500, 600 for the UI; JetBrains Mono 400, 500 for URLs, models, keys and transcription. Base size 15 px, line height 1.5. Captions 13 px, small labels 12 px, screen titles 22–26 px. Radii: 8 px for buttons and fields, 12 px for cards. Feed width up to 760 px.

One light theme. A dark theme is not part of the first version.

## Marks in text

Marks differ by shape, not only by colour.

| What | Look | Action |
| --- | --- | --- |
| Grammar and vocabulary | Blue 2 px underline | Click opens the correction card on this correction |
| Pronunciation: error | Orange fill `--pron-soft`, text `--pron` | Click opens the word breakdown |
| Pronunciation: close | Orange dotted underline | Same |
| Correct | No mark | — |

Every mark is a button or an element with `role="button"`, reachable from the keyboard, with an `aria-label` in the learner's language.

## Bottom panel

The panel is fixed at the bottom of every screen with a microphone.

- **Waveform.** 48 vertical bars. Each bar is the RMS level over a window of about 50 ms; new values come in from the right. Bar height from 2 px in silence to the full strip height. Drawn on `canvas` via `requestAnimationFrame` from an `AnalyserNode`.
- **Waveform colour.** Microphone open, not recording — `--faint`. Recording — `--accent`. Tutor speaking — `--muted`, fed from the synthesis output.
- **Silent microphone.** If the level stays below the noise threshold for 5 s, a hint appears above the waveform suggesting to check the microphone in the settings.
- **State.** Text above the waveform: microphone ready, listening, transcribing, thinking, tutor speaking. A timer runs while recording.
- **Microphone button.** Duplicates Space. Turns blue while recording.
- **Switches.** "Manual / Auto" and the corrections mode.

Test attributes (`data-state`, `data-level`, `data-source`, `data-testid`) are listed in `docs/testing.md`.

## Keys

| Key | Action |
| --- | --- |
| Space | Start recording; while recording — send; while the tutor speaks — interrupt and start recording |
| Esc | Cancel recording; close a card or dialog |

Space is not captured while focus is in a text field.

## First launch and empty states

- **No connection.** The conversation screen shows one "Add API connection" button and a line of explanation.
- **Before a session.** Scenario choice and a "Start conversation" button. The click creates the `AudioContext` and requests the microphone.
- **No microphone access.** How to allow access, and a "Check again" button.
- **Connection error.** A block in the feed with the error text and "Retry" and "Switch to…" buttons.
- **Models loading at start.** Panel state "Loading models…"; the microphone button is disabled.

## Accessibility

- Every action is reachable from the keyboard; focus is visible.
- Text contrast against its background is at least 4.5:1 for primary and secondary text.
- Turns carry `lang="en"`; corrections and hints carry the learner language tag.
- With the system "reduce motion" setting the waveform updates without smoothing and other animations are off.
