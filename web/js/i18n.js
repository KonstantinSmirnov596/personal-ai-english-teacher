// Interface strings in the learner's language (web/i18n/<code>.js), switched at runtime.
//
// `L` is one shared object. Views read it when they render (`L.talk.start`) or keep a reference
// to a section (`const R = L.connections`); switching the language replaces the contents of the
// same objects in place, so both styles see the new language after a re-render.

export const L = {};

let current = { code: '', htmlLang: 'en' };
let available = [];

function clone(value) {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    const out = {};
    for (const [k, v] of Object.entries(value)) out[k] = clone(v);
    return out;
  }
  return value;
}

function replaceInPlace(target, source) {
  for (const key of Object.keys(target)) if (!(key in source)) delete target[key];
  for (const [key, value] of Object.entries(source)) {
    const isObject = value && typeof value === 'object' && !Array.isArray(value);
    const targetIsObject = target[key] && typeof target[key] === 'object' && !Array.isArray(target[key]);
    if (isObject && targetIsObject) replaceInPlace(target[key], value);
    else target[key] = clone(value);
  }
}

// Loads web/i18n/<code>.js; codes come from the core (GET /api/languages), never from a user.
export async function setLanguage(code, htmlLang) {
  const mod = await import(`../i18n/${code}.js`);
  replaceInPlace(L, mod.default);
  current = { code, htmlLang: htmlLang || code };
  document.documentElement.lang = current.htmlLang;
  document.title = L.appTitle;
}

export function setAvailable(list) {
  available = list;
}

export function languages() {
  return available;
}

export function currentLanguage() {
  return current.code;
}

// BCP 47 tag for elements that hold learner-language text (`lang` attribute).
export function langTag() {
  return current.htmlLang;
}
