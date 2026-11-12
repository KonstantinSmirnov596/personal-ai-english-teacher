// First-run wizard (SPEC 7): eight steps, each one can be opened again from Settings →
// Performance. Nothing here sends data outside the computer: hardware facts, measurements and
// the microphone check stay in the core's database; only step 7 talks to the LLM provider the
// user picks, through the core.
//
// Tests observe the wizard through data-testid, data-step and data-state attributes.

import { L, currentLanguage, langTag, languages, setLanguage } from './i18n.js';
import { get, patch, post } from './api.js';
import { clear, el, icons } from './dom.js';
import { Wave } from './wave.js';

export const STEPS = ['language', 'hardware', 'models', 'benchmark', 'microphone', 'sound', 'llm', 'level'];

// Microphone check (step 5): levels are 0..100 on a -60..0 dBFS scale (audio.js rmsToLevel).
const SILENCE_MS = 3000;
const SPEECH_MS = 4000;
const QUIET_LEVEL = 25; // below about -45 dBFS
const NOISY_LEVEL = 40; // above about -36 dBFS
const SPEECH_MIN_LEVEL = 35;
const LEVELS = ['A2', 'B1', 'B2', 'C1'];
// Read aloud during the level check: English in every learner language.
const MIC_PHRASE = "Hello! I'm ready to practice my English today.";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function percentile(values, p) {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.min(sorted.length - 1, Math.floor((p / 100) * sorted.length))];
}

// Folder of the user documentation for the current interface language (docs/<lang>/).
export function docsFolder() {
  return currentLanguage().startsWith('pt') ? 'pt-BR' : 'es';
}

// Gigabytes in the learner's number format (decimal comma in Spanish and Portuguese).
export function gb(mb) {
  return `${(mb / 1024).toLocaleString(langTag(), { minimumFractionDigits: 1, maximumFractionDigits: 1 })} GB`;
}

// [value, required] of one hardware check, from its numbers (profiles.py Check.params).
export function checkCells(c) {
  const V = L.wizard.values;
  const p = c.params || {};
  switch (c.id) {
    case 'gpu':
      return [p.name || V.none, V.nvidiaGpu];
    case 'driver':
      return [p.version, p.min];
    case 'architecture':
      return [p.cc, `${p.min} (Turing)`];
    case 'vram':
      return p.free_mb !== undefined ? [V.freeOf(gb(p.free_mb), gb(p.total_mb)), V.free(gb(p.min_free_mb))] : [gb(p.total_mb), gb(p.min_total_mb)];
    case 'ram':
      return [gb(p.total_mb), gb(p.min_mb)];
    case 'disk':
      return [V.free(gb(p.free_mb)), V.free(gb(p.min_free_mb))];
    case 'power':
      return [p.on_battery ? V.battery : V.mains, V.mains];
    case 'windows':
      return [String(p.build), `${p.min} (Windows 10 22H2)`];
    default:
      return [c.value, c.required];
  }
}

export class WizardView {
  constructor(app) {
    this.app = app;
    this.root = el('div', { class: 'wizard', 'data-testid': 'wizard' });
    this.timers = [];
    this.generation = 0; // a newer render cancels the async work of an older one
  }

  // Leaving the wizard (or re-rendering it) cancels the async work of the shown step.
  stopTimers() {
    this.generation += 1;
    for (const t of this.timers) clearInterval(t);
    this.timers = [];
    if (this.wave) {
      this.wave.stop();
      this.wave = null;
    }
  }

  render(step) {
    this.stopTimers();
    this.generation += 1;
    this.step = STEPS.includes(step) ? step : STEPS[0];
    const W = L.wizard;
    const index = STEPS.indexOf(this.step);
    clear(this.root);
    this.root.dataset.step = this.step;

    const stepper = el('ol', { class: 'stepper', 'aria-label': W.stepsLabel });
    STEPS.forEach((s, i) => {
      stepper.append(
        el('li', {}, [
          el('a', { href: `#/wizard/${s}`, 'aria-current': s === this.step ? 'step' : null, 'data-step': s }, [
            el('span', { class: 'stepper-num', text: String(i + 1) }),
            el('span', { class: 'stepper-label', text: W.steps[s] }),
          ]),
        ]),
      );
    });

    this.body = el('div', { class: 'wizard-body', 'data-testid': `wizard-${this.step}`, 'data-state': 'loading' });
    this.status = el('p', { class: 'form-error', role: 'status', 'data-testid': 'wizard-status' });
    this.back = el('button', { type: 'button', class: 'btn btn-ghost', 'data-testid': 'wizard-back', text: W.back, disabled: index === 0 });
    this.back.addEventListener('click', () => this.go(index - 1));
    const last = index === STEPS.length - 1;
    this.next = el('button', { type: 'button', class: 'btn btn-primary', 'data-testid': last ? 'wizard-finish' : 'wizard-next', text: last ? W.finish : W.next });
    this.next.addEventListener('click', () => (last ? this.finish() : this.go(index + 1)));

    this.root.append(
      el('div', { class: 'wizard-head' }, [
        el('p', { class: 'wizard-kicker', text: W.title }),
        el('p', { class: 'muted small', text: W.stepOf(index + 1, STEPS.length) }),
      ]),
      stepper,
      el('section', { class: 'wizard-card', 'aria-labelledby': 'wizard-step-title' }, [
        el('h1', { id: 'wizard-step-title', text: W.steps[this.step] }),
        el('p', { class: 'muted', text: W.intro[this.step] }),
        this.body,
        this.status,
      ]),
      el('div', { class: 'wizard-nav' }, [this.back, this.next]),
    );
    const gen = this.generation;
    this[this.step](gen).catch((e) => {
      if (gen !== this.generation) return;
      this.body.dataset.state = 'error';
      this.status.textContent = e.message || L.errors.internal;
    });
    return this.root;
  }

  alive(gen) {
    return gen === this.generation;
  }

  go(index) {
    location.hash = `#/wizard/${STEPS[Math.max(0, Math.min(STEPS.length - 1, index))]}`;
  }

  setState(state) {
    this.body.dataset.state = state;
  }

  // --- 1. language -------------------------------------------------------------------------

  async language() {
    const box = el('div', { class: 'segmented', role: 'radiogroup', 'aria-label': L.language.label, 'data-testid': 'wizard-language-switch' });
    for (const lang of languages()) {
      const chosen = lang.code === currentLanguage();
      const b = el('button', {
        type: 'button',
        role: 'radio',
        lang: lang.html_lang,
        'aria-checked': String(chosen),
        'aria-pressed': String(chosen),
        'data-lang': lang.code,
        text: lang.name_native,
      });
      b.addEventListener('click', async () => {
        if (lang.code !== currentLanguage()) {
          this.app.settings = await patch('/api/settings', { l1: lang.code });
          await setLanguage(lang.code, lang.html_lang);
          window.dispatchEvent(new CustomEvent('voicetutor:language', { detail: lang.code }));
        } else {
          // confirming the proposed language stores it, so it no longer follows Windows
          this.app.settings = await patch('/api/settings', { l1: lang.code });
        }
      });
      box.append(b);
    }
    this.body.append(box, el('p', { class: 'muted small', text: L.language.hint }));
    // Moving on confirms the proposed language.
    this.next.addEventListener('click', () => patch('/api/settings', { l1: currentLanguage() }).catch(() => {}), { once: true });
    this.setState('ready');
  }

  // --- 2. hardware ---------------------------------------------------------------------------

  async hardware(gen) {
    const W = L.wizard;
    this.next.disabled = true;
    const hw = await get('/api/hardware');
    if (!this.alive(gen)) return;
    const a = hw.current;
    // Free video memory alone is not a hardware limit: other programs can be closed.
    const hardLimit = hw.profile === 'unsupported' || a.reasons.some((r) => r !== 'vram');
    const table = el('table', { class: 'table check-table', 'data-testid': 'hardware-checks' }, [
      el('thead', {}, [
        el('tr', {}, [
          el('th', { scope: 'col', text: W.colItem }),
          el('th', { scope: 'col', text: W.colValue }),
          el('th', { scope: 'col', text: W.colRequired }),
          el('th', { scope: 'col', text: W.colResult }),
        ]),
      ]),
    ]);
    const tbody = el('tbody');
    for (const c of a.checks) {
      const result = c.ok ? 'ok' : c.blocking ? 'fail' : 'warn';
      const [value, required] = checkCells(c);
      tbody.append(
        el('tr', { 'data-check': c.id, 'data-result': result }, [
          el('th', { scope: 'row', text: W.checks[c.id] || c.id }),
          el('td', { class: 'mono', text: value }),
          el('td', { class: 'mono muted', text: required }),
          el('td', { class: `check-${result}` }, [c.ok ? icons.check() : icons.cross(), el('span', { text: W.result[result] })]),
        ]),
      );
    }
    table.append(tbody);

    const fixes = el('div', { class: 'fix-list' });
    for (const c of a.checks.filter((x) => !x.ok)) {
      fixes.append(
        el('div', { class: c.blocking ? 'notice notice-fail' : 'notice', 'data-testid': 'hardware-fix', 'data-check': c.id }, [
          el('h2', { text: W.checks[c.id] || c.id }),
          el('p', { text: W.fixes[c.id] || '' }),
          el('p', { class: 'muted small' }, [el('span', { text: `${W.docs} ` }), el('span', { class: 'mono', text: `docs/${docsFolder()}/${c.doc}` })]),
        ]),
      );
    }

    // The card is fine but other programs hold its memory: compacto until they are closed.
    const busy = !hardLimit && a.reasons.includes('vram');
    const profile = hardLimit ? 'unsupported' : busy ? 'vram_low' : a.profile;
    const verdict = el('div', { class: `verdict verdict-${busy ? 'unsupported' : profile}`, 'data-testid': 'hardware-profile', 'data-profile': profile }, [
      el('strong', { text: busy ? W.busyTitle : W.profileName[profile] }),
      el('p', { text: busy ? W.busyText : W.profileText[profile] }),
    ]);
    const again = el('button', { type: 'button', class: 'btn btn-small', 'data-testid': 'hardware-again', text: W.checkAgain });
    again.addEventListener('click', () => this.app.route());
    this.body.append(verdict, table, fixes, el('div', { class: 'form-actions' }, [again]));
    this.setState(profile);
    this.next.disabled = hardLimit;
  }

  // --- 3. models -----------------------------------------------------------------------------

  // The app downloads nothing at run time: missing models come from install.cmd, which
  // resumes broken downloads and verifies checksums; the app then loads them without a restart.
  async models(gen) {
    const W = L.wizard;
    const m = await get('/api/models');
    if (!this.alive(gen)) return;
    const list = el('ul', { class: 'plain-list', 'data-testid': 'model-list' });
    for (const [key, ok] of Object.entries(m.present)) {
      list.append(el('li', { class: ok ? 'check-ok' : 'check-warn', 'data-model': key, 'data-present': String(ok) }, [ok ? icons.check() : icons.cross(), el('span', { text: W.modelNames[key] || key })]));
    }
    this.body.append(list);
    if (m.all_present) {
      const health = await get('/api/health');
      if (!this.alive(gen)) return;
      if (health.status === 'error' && (health.problems || []).some((p) => p.code === 'models_missing')) {
        // installed while the app was running: load them now
        await post('/api/models/load').catch(() => {});
      }
      this.body.append(el('p', { text: W.modelsPresent }));
      this.setState('present');
      this.next.disabled = false;
      return;
    }
    this.next.disabled = true;
    const again = el('button', { type: 'button', class: 'btn btn-primary', 'data-testid': 'models-again', text: W.checkAgain });
    again.addEventListener('click', () => this.app.route());
    this.body.append(
      el('p', { text: W.modelsMissing }),
      el('ol', { class: 'steps-list' }, W.modelsSteps.map((t) => el('li', { text: t }))),
      el('div', { class: 'form-actions' }, [again]),
    );
    this.setState('missing');
  }

  // --- 4. benchmark --------------------------------------------------------------------------

  async benchmark(gen) {
    const W = L.wizard;
    const run = el('button', { type: 'button', class: 'btn btn-primary', 'data-testid': 'benchmark-run', text: W.benchmarkRun });
    const out = el('div', { class: 'bench-result' });
    const waiting = el('p', { class: 'muted', text: W.modelsLoading });
    this.body.append(waiting, el('div', { class: 'form-actions' }, [run]), out);
    run.disabled = true;
    // The stored result of an earlier run is shown until a new one is made.
    const hw = await get('/api/hardware');
    if (!this.alive(gen)) return;
    if (hw.stored) this.drawBenchmark(out, { profile: hw.stored.profile, measurements: hw.stored.measurements, applied_profile: hw.profile, stored: hw.stored });
    this.setState(hw.stored ? 'done' : 'idle');
    while (this.alive(gen)) {
      const h = await get('/api/health');
      if (h.status === 'ok') break;
      if (h.status === 'error') {
        waiting.textContent = W.modelsUnavailable;
        this.setState('unavailable');
        return;
      }
      await sleep(1000);
    }
    if (!this.alive(gen)) return;
    waiting.textContent = W.benchmarkText;
    run.disabled = false;
    run.addEventListener('click', async () => {
      run.disabled = true;
      this.setState('running');
      clear(out).append(el('p', { class: 'muted', text: W.benchmarkRunning }));
      try {
        const result = await post('/api/hardware/benchmark');
        if (!this.alive(gen)) return;
        this.drawBenchmark(out, result);
        this.setState('done');
        this.app.settings = await get('/api/settings');
      } catch (e) {
        if (!this.alive(gen)) return;
        clear(out);
        this.status.textContent = e.message || L.errors.internal;
        this.setState('error');
      } finally {
        run.disabled = false;
      }
    });
  }

  drawBenchmark(out, result) {
    const W = L.wizard;
    const m = result.measurements || {};
    const ms = (v) => (v === undefined || v < 0 ? '—' : `${Math.round(v)} ms`);
    const size = (v) => (v === undefined ? '—' : gb(v));
    const rows = [
      [W.bench.stt(m.stt_audio_s || 10), ms(m.stt_ms)],
      [W.bench.tts, ms(m.tts_first_ms)],
      [W.bench.pron, ms(m.pron_ms)],
      [W.bench.firstAudio, ms(m.first_audio_ms)],
      [W.bench.vramUsed, m.vram_used_mb ? size(m.vram_used_mb) : '—'],
      [W.bench.vramFree, size(m.vram_free_after_load_mb)],
    ];
    const table = el('table', { class: 'table check-table', 'data-testid': 'benchmark-table' }, [
      el('tbody', {}, rows.map(([k, v]) => el('tr', {}, [el('th', { scope: 'row', text: k }), el('td', { class: 'mono', text: v })]))),
    ]);
    const profile = result.applied_profile || result.profile;
    clear(out).append(
      table,
      el('div', { class: `verdict verdict-${profile}`, 'data-testid': 'benchmark-profile', 'data-profile': profile, 'data-measured': result.profile }, [
        el('strong', { text: W.profileName[profile] || profile }),
        el('p', { text: W.profileText[profile] || '' }),
        result.measured_profile && result.profile !== result.measured_profile ? el('p', { class: 'muted small', text: W.lowered }) : null,
        this.app.settings && this.app.settings.profile && this.app.settings.profile !== 'auto' ? el('p', { class: 'muted small', text: W.manualProfile }) : null,
      ]),
    );
  }

  // --- 5. microphone -------------------------------------------------------------------------

  async microphone(gen) {
    const W = L.wizard;
    const s = this.app.settings || (await get('/api/settings'));
    let devices = [];
    try {
      devices = (await navigator.mediaDevices.enumerateDevices()).filter((d) => d.kind === 'audioinput' && d.deviceId && d.deviceId !== 'default');
    } catch {
      devices = [];
    }
    if (!this.alive(gen)) return;
    const select = el('select', { class: 'select', id: 'wizard-mic' });
    select.append(el('option', { value: '', text: L.sound.systemDefault }));
    for (const d of devices) {
      const o = el('option', { value: d.deviceId, text: d.label || d.deviceId.slice(0, 8) });
      if (d.deviceId === s.input_device_id) o.selected = true;
      select.append(o);
    }
    const canvas = el('canvas', { class: 'wave', 'data-testid': 'wizard-wave', 'aria-label': L.panel.waveLabel, role: 'img' });
    const prompt = el('p', { class: 'mic-prompt', 'data-testid': 'mic-prompt', text: W.micIdle });
    const phrase = el('p', { class: 'mic-phrase hidden', lang: 'en', text: MIC_PHRASE });
    const result = el('div', { 'data-testid': 'mic-result' });
    const start = el('button', { type: 'button', class: 'btn btn-primary', 'data-testid': 'mic-start', text: W.micStart });
    this.body.append(
      el('div', { class: 'field' }, [el('label', { for: 'wizard-mic', text: L.sound.input }), select]),
      el('div', { class: 'wave-wrap' }, [canvas]),
      prompt,
      phrase,
      el('div', { class: 'form-actions' }, [start]),
      result,
    );
    this.setState('idle');
    const audio = this.app.audio;
    let micOpen = false;
    this.wave = new Wave(canvas, () => ({ level: micOpen ? audio.micLevel() : 0, source: 'mic', recording: micOpen, micOpen: false }));
    const collect = async (ms) => {
      const values = [];
      const end = performance.now() + ms;
      while (performance.now() < end) {
        values.push(audio.micLevel());
        await sleep(50);
        if (!this.alive(gen)) throw new Error('left');
      }
      return values;
    };
    start.addEventListener('click', async () => {
      start.disabled = true;
      select.disabled = true;
      clear(result);
      this.status.textContent = '';
      try {
        // Raw signal for the measurement: the browser's noise suppression and gain would hide
        // the room noise this step is measuring.
        await audio.init({ deviceId: select.value, noiseSuppression: false, autoGainControl: false });
        micOpen = true;
      } catch (e) {
        this.setState(e && e.name === 'NotAllowedError' ? 'denied' : 'no-mic');
        result.append(this.micHelp(e && e.name === 'NotAllowedError'));
        start.disabled = false;
        select.disabled = false;
        return;
      }
      try {
        this.setState('noise');
        prompt.textContent = W.micQuiet;
        const quiet = await collect(SILENCE_MS);
        this.setState('speak');
        prompt.textContent = W.micSpeak;
        phrase.classList.remove('hidden');
        const speech = await collect(SPEECH_MS);
        phrase.classList.add('hidden');
        const noise = percentile(quiet, 50);
        const voice = percentile(speech, 90);
        const room = noise < QUIET_LEVEL ? 'quiet' : noise < NOISY_LEVEL ? 'moderate' : 'noisy';
        // Louder rooms need a stricter voice detector; a quiet room keeps the raw signal,
        // which preserves the consonants the pronunciation check listens for.
        const threshold = { quiet: 0.5, moderate: 0.6, noisy: 0.7 }[room];
        const noiseSuppression = room !== 'quiet';
        const signal = voice >= SPEECH_MIN_LEVEL && voice >= noise + 6;
        this.app.settings = await patch('/api/settings', { input_device_id: select.value, vad_threshold: threshold, noise_suppression: noiseSuppression });
        if (!this.alive(gen)) return;
        prompt.textContent = W.micDone;
        result.dataset.room = room;
        result.dataset.threshold = String(threshold);
        result.dataset.noise = String(noise);
        result.dataset.voice = String(voice);
        result.append(
          el('p', { text: W.room[room](noise) }),
          el('p', { text: signal ? W.voiceOk(voice) : W.voiceLow(voice) }),
          el('p', { class: 'muted small', text: W.micApplied(threshold, noiseSuppression) }),
        );
        if (!signal) result.append(this.micHelp(false));
        this.setState(signal ? 'done' : 'no-signal');
      } catch (e) {
        if (e.message !== 'left') this.status.textContent = e.message;
      } finally {
        start.disabled = false;
        select.disabled = false;
        start.textContent = W.micAgain;
      }
    });
  }

  micHelp(denied) {
    const W = L.wizard;
    return el('div', { class: 'notice', 'data-testid': 'mic-help' }, [
      el('h2', { text: denied ? L.talk.micDeniedTitle : W.noSignalTitle }),
      el('ol', { class: 'steps-list' }, W.micHelpSteps.map((t) => el('li', { text: t }))),
    ]);
  }

  // --- 6. sound and voice --------------------------------------------------------------------

  async sound(gen) {
    const W = L.wizard;
    const S = L.sound;
    const s = this.app.settings || (await get('/api/settings'));
    const voices = await get('/api/voices');
    if (!this.alive(gen)) return;
    const voice = el('select', { class: 'select', id: 'wizard-voice', 'data-testid': 'wizard-voice' });
    for (const v of voices) {
      const o = el('option', { value: v.id, text: `${v.id} — ${v.gender === 'female' ? S.female : S.male}` });
      if (v.id === s.voice) o.selected = true;
      voice.append(o);
    }
    const save = async (change) => {
      this.app.settings = await patch('/api/settings', change);
    };
    voice.addEventListener('change', () => save({ voice: voice.value }));
    const speed = el('input', { type: 'range', id: 'wizard-speed', min: '0.7', max: '1.3', step: '0.05', value: String(s.speed) });
    const speedValue = el('span', { class: 'muted', text: `×${Number(s.speed).toFixed(2)}` });
    speed.addEventListener('input', () => (speedValue.textContent = `×${Number(speed.value).toFixed(2)}`));
    speed.addEventListener('change', () => save({ speed: Number(speed.value) }));
    const play = el('button', { type: 'button', class: 'btn', 'data-testid': 'wizard-play', text: W.playTest });
    play.addEventListener('click', async () => {
      play.disabled = true;
      try {
        const resp = await fetch('/api/voices/preview', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ voice: voice.value, speed: Number(speed.value) }),
        });
        if (!resp.ok) throw new Error(L.errors.tts_failed);
        const url = URL.createObjectURL(await resp.blob());
        const a = new Audio(url);
        const sink = this.app.settings && this.app.settings.output_device_id;
        if (sink && a.setSinkId) await a.setSinkId(sink).catch(() => {});
        a.addEventListener('ended', () => URL.revokeObjectURL(url));
        await a.play();
        this.setState('played');
      } catch (e) {
        this.status.textContent = e.message;
      } finally {
        play.disabled = false;
      }
    });
    const phones = el('div', { class: 'radio-list', role: 'radiogroup', 'aria-label': W.headphonesQuestion, 'data-testid': 'wizard-headphones' });
    for (const [value, label] of [[true, W.yes], [false, W.no]]) {
      const id = `wizard-phones-${value}`;
      const r = el('input', { type: 'radio', name: 'wizard-phones', id, value: String(value) });
      r.checked = !!s.headphones === value;
      r.addEventListener('change', () => save({ headphones: value }));
      phones.append(el('label', { class: 'check', for: id }, [r, el('span', { text: label })]));
    }
    this.body.append(
      el('div', { class: 'form-actions' }, [play]),
      el('div', { class: 'field' }, [el('label', { for: 'wizard-voice', text: S.voice }), voice]),
      el('div', { class: 'field' }, [el('label', { for: 'wizard-speed', text: S.speed }), el('div', { class: 'range-row' }, [speed, speedValue])]),
      el('div', { class: 'field' }, [el('span', { class: 'field-label', text: W.headphonesQuestion }), phones, el('p', { class: 'muted small', text: W.headphonesHint })]),
    );
    this.setState('ready');
  }

  // --- 7. LLM connection ---------------------------------------------------------------------

  async llm(gen) {
    const W = L.wizard;
    const R = L.connections;
    const [rows, templates] = await Promise.all([get('/api/connections'), get('/api/connections/templates')]);
    if (!this.alive(gen)) return;
    const active = rows.find((r) => r.is_active);
    if (active) {
      this.body.append(
        el('div', { class: 'verdict verdict-completo', 'data-testid': 'llm-active' }, [
          el('strong', { text: W.llmActive }),
          el('p', { class: 'mono', text: `${active.name} · ${active.model}` }),
        ]),
        el('p', { class: 'muted small' }, [el('span', { text: `${W.llmMore} ` }), el('a', { href: '#/settings/connections', text: R.title })]),
      );
      this.setState('ok');
      return;
    }
    const tplName = (tpl) => (R.templateNames && R.templateNames[tpl.id]) || tpl.name;
    const template = el('select', { id: 'wizard-template', class: 'select', 'data-testid': 'wizard-template' });
    for (const tpl of templates) template.append(el('option', { value: tpl.id, text: tplName(tpl) }));
    const input = (id, attrs) => el('input', { id, class: 'input mono', type: 'text', autocomplete: 'off', spellcheck: 'false', ...attrs });
    const url = input('wizard-url', { type: 'url' });
    const model = input('wizard-model', {});
    const key = input('wizard-key', { type: 'password', placeholder: R.keyPlaceholder, 'data-testid': 'wizard-key' });
    const warning = el('p', { class: 'notice hidden', 'data-testid': 'llm-local-warning', text: W.localWarning });
    const field = (label, control) => el('div', { class: 'field' }, [el('label', { for: control.id, text: label }), control]);
    const keyField = field(R.key, key);
    let tpl = null;
    const apply = () => {
      tpl = templates.find((x) => x.id === template.value) || templates[0];
      url.value = tpl.base_url;
      model.value = tpl.model;
      model.placeholder = tpl.models && tpl.models.length ? tpl.models[0] : W.modelPlaceholder;
      warning.classList.toggle('hidden', tpl.kind !== 'local');
      keyField.classList.toggle('hidden', !tpl.key_required);
    };
    template.addEventListener('change', apply);
    apply();
    const check = el('button', { type: 'button', class: 'btn btn-primary', 'data-testid': 'llm-check', text: W.llmCheck });
    const skip = el('button', { type: 'button', class: 'btn btn-ghost', 'data-testid': 'llm-skip', text: W.llmSkip });
    skip.addEventListener('click', () => this.go(STEPS.indexOf('level')));
    check.addEventListener('click', async () => {
      const body = {
        base_url: url.value.trim(),
        model: model.value.trim(),
        api_key: key.value.trim(),
        extra_params: tpl.extra_params || {},
        json_format: tpl.json_format,
      };
      if (!body.base_url || !body.model || (tpl.key_required && !body.api_key)) {
        this.status.textContent = W.llmRequired;
        return;
      }
      check.disabled = true;
      this.setState('testing');
      this.status.textContent = R.testing;
      try {
        const res = await post('/api/connections/test', body);
        if (!this.alive(gen)) return;
        if (!res.ok) {
          this.status.textContent = res.message_l1;
          this.setState('error');
          return;
        }
        await post('/api/connections', { ...body, name: tplName(tpl) });
        key.value = '';
        await this.app.refreshActiveConnection();
        this.status.textContent = '';
        this.setState('ok');
        this.render('llm');
      } catch (e) {
        this.status.textContent = e.message;
        this.setState('error');
      } finally {
        check.disabled = false;
      }
    });
    this.body.append(
      el('div', { class: 'form-grid' }, [field(R.template, template), field(R.url, url), field(R.model, model), keyField]),
      warning,
      el('p', { class: 'muted small', text: R.footnote }),
      el('div', { class: 'form-actions' }, [check, skip]),
      el('p', { class: 'muted small', text: W.llmSkipHint }),
    );
    this.setState('idle');
  }

  // --- 8. level ------------------------------------------------------------------------------

  async level() {
    const W = L.wizard;
    const s = this.app.settings || (await get('/api/settings'));
    this.chosenLevel = s.level;
    const list = el('div', { class: 'level-cards', role: 'radiogroup', 'aria-label': L.conversationSettings.level, 'data-testid': 'wizard-levels' });
    for (const lv of LEVELS) {
      const id = `wizard-level-${lv}`;
      const r = el('input', { type: 'radio', name: 'wizard-level', id, value: lv });
      r.checked = lv === s.level;
      r.addEventListener('change', () => (this.chosenLevel = lv));
      list.append(
        el('label', { class: 'level-card', for: id, 'data-level': lv }, [r, el('span', { class: 'level-name', text: lv }), el('span', { class: 'level-desc', text: W.levels[lv] })]),
      );
    }
    this.body.append(list);
    this.setState('ready');
  }

  async finish() {
    this.next.disabled = true;
    try {
      this.app.settings = await patch('/api/settings', { level: this.chosenLevel || 'B1', wizard_done: true });
      location.hash = '#/talk';
    } catch (e) {
      this.status.textContent = e.message;
      this.next.disabled = false;
    }
  }
}
