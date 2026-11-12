// Entry point: load the strings of the learner language before any view module evaluates.

import { get } from './api.js';
import { setAvailable, setLanguage } from './i18n.js';

async function boot() {
  let info = null;
  try {
    info = await get('/api/languages');
  } catch {
    info = null;
  }
  const list = (info && info.available) || [{ code: 'es-419', html_lang: 'es-419' }];
  const code = (info && info.current) || list[0].code;
  const meta = list.find((x) => x.code === code) || list[0];
  setAvailable(list);
  await setLanguage(meta.code, meta.html_lang);
  const { App } = await import('./app.js');
  const app = new App(document.getElementById('app'));
  window.addEventListener('voicetutor:language', () => app.rerender());
  await app.start();
}

boot();
