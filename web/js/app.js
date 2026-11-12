// Window shell: header, hash router, shared state, WebSocket to the core.

import { L } from './i18n.js';
import { get, post } from './api.js';
import { AudioEngine } from './audio.js';
import { ConnectionsView } from './connections.js';
import { clear, el, icons } from './dom.js';
import { HistoryView } from './history.js';
import { ReadingView } from './reading.js';
import { SettingsView } from './settings.js';
import { VocabView } from './vocab.js';
import { WizardView } from './wizard.js';
import { TalkView } from './talk.js';
import { CoreSocket } from './ws.js';

export class App {
  constructor(root) {
    this.root = root;
    this.audio = new AudioEngine();
    this.hello = null;
    this.settings = null;
    this.activeConnection = null;
    this.modelsReady = false;
    this.socketOpen = false;
    this.pending = new Map(); // request_id -> {resolve, reject}
    this.socket = new CoreSocket(
      (msg, bin) => this.onMessage(msg, bin),
      (status, code) => this.onSocketStatus(status, code),
    );
    this.talk = new TalkView(this);
    this.connections = new ConnectionsView(this);
    this.history = new HistoryView(this);
    this.vocab = new VocabView(this);
    this.reading = new ReadingView(this);
    this.settingsView = new SettingsView(this);
    this.wizard = new WizardView(this);
    this.notices = [];
    this.header = el('header', { class: 'header' });
    this.noticeBar = el('div', { class: 'notice-bar', 'data-testid': 'notice-bar' });
    this.body = el('div', { class: 'app-body' });
    root.append(this.header, this.noticeBar, this.body);
    window.addEventListener('hashchange', () => this.route());
  }

  async start() {
    document.title = L.appTitle;
    try {
      this.settings = await get('/api/settings');
    } catch {
      this.settings = null;
    }
    await this.refreshActiveConnection();
    this.socket.connect();
    // First run: the wizard opens before anything else (SPEC 7).
    if (this.settings && !this.settings.wizard_done && !location.hash.startsWith('#/wizard')) {
      history.replaceState(null, '', '#/wizard/language');
    }
    this.route();
  }

  // Battery and changed-hardware notices (hello.hardware.notices), once per run.
  renderNotices() {
    const bar = clear(this.noticeBar);
    if (this.current === 'wizard') return;
    for (const id of this.notices) {
      const text = L.notices[id];
      if (!text) continue;
      const close = el('button', { type: 'button', class: 'btn btn-small btn-ghost', 'data-testid': 'notice-dismiss', text: L.notices.dismiss });
      close.addEventListener('click', async () => {
        this.notices = this.notices.filter((n) => n !== id);
        this.renderNotices();
        await post(`/api/hardware/notices/${id}/dismiss`).catch(() => {});
      });
      const actions = [close];
      if (id === 'hardware_changed') actions.unshift(el('a', { class: 'btn btn-small', href: '#/wizard/hardware', text: L.notices.recheck }));
      bar.append(el('div', { class: 'banner', role: 'status', 'data-testid': 'hardware-notice', 'data-notice': id }, [el('p', { text }), el('div', { class: 'banner-actions' }, actions)]));
    }
  }

  async refreshActiveConnection() {
    try {
      const rows = await get('/api/connections');
      const active = rows.find((r) => r.is_active);
      this.activeConnection = active ? { id: active.id, name: active.name, model: active.model } : null;
      this.connectionRows = rows;
    } catch {
      this.activeConnection = null;
      this.connectionRows = [];
    }
    this.renderHeader();
    return this.connectionRows;
  }

  onSocketStatus(status, code) {
    this.socketOpen = status === 'open';
    this.talk.onSocketStatus(status, code);
  }

  // Sends a helper request and resolves with helper.result data (or rejects on error).
  askHelper(msg, binary) {
    const requestId = crypto.randomUUID();
    return new Promise((resolve, reject) => {
      this.pending.set(requestId, { resolve, reject });
      if (!this.socket.send({ ...msg, request_id: requestId }, binary)) {
        this.pending.delete(requestId);
        reject(Object.assign(new Error('offline'), { code: 'network' }));
      }
    });
  }

  onMessage(msg, binary) {
    if (msg.request_id && this.pending.has(msg.request_id) && (msg.type === 'helper.result' || msg.type === 'error')) {
      const p = this.pending.get(msg.request_id);
      this.pending.delete(msg.request_id);
      if (msg.type === 'helper.result') p.resolve(msg.data);
      else p.reject(Object.assign(new Error(msg.code), { code: msg.code }));
      return;
    }
    if (msg.type === 'hello') {
      this.hello = msg;
      this.settings = msg.settings;
      this.activeConnection = msg.active_connection;
      this.modelsReady = msg.models_ready;
      this.notices = (msg.hardware && msg.hardware.notices) || [];
      this.renderHeader();
      this.renderNotices();
      if (!this.modelsReady) this.pollModels();
    }
    this.talk.onMessage(msg, binary);
  }

  async pollModels() {
    while (!this.modelsReady) {
      await new Promise((r) => setTimeout(r, 1000));
      try {
        const h = await get('/api/health');
        if (h.status === 'ok') {
          this.modelsReady = true;
          this.talk.onModelsReady();
        } else if (h.status === 'error') {
          this.problems = h.problems || [];
          this.talk.onModelsReady();
          return;
        }
      } catch {
        // core restarting; keep polling
      }
    }
  }

  // After a language switch: rebuild the visible screen and the panel texts in the new language.
  rerender() {
    this.talk.relabel();
    this.route();
  }

  route() {
    const hash = location.hash || '#/talk';
    const [, section, sub] = hash.split('/');
    clear(this.body);
    let current = 'talk';
    if (section !== 'wizard') this.wizard.stopTimers();
    if (section === 'wizard') {
      current = 'wizard';
      this.current = current;
      this.body.append(this.wizard.render(sub));
    } else if (section === 'settings') {
      current = 'settings';
      this.body.append(sub && sub !== 'connections' ? this.settingsView.render(sub) : this.connections.render());
    } else if (section === 'reading') {
      current = 'reading';
      this.current = current;
      this.body.append(this.reading.render());
    } else if (section === 'vocab') {
      current = 'vocab';
      this.body.append(this.vocab.render());
    } else if (section === 'history') {
      current = 'history';
      this.body.append(this.history.render(sub));
    } else {
      this.body.append(this.talk.render());
    }
    this.current = current;
    this.renderHeader();
    this.renderNotices();
    this.talk.syncAuto(); // the detector listens only while the conversation is on screen
  }

  renderHeader() {
    const h = clear(this.header);
    if (this.current === 'wizard' && this.settings && !this.settings.wizard_done) {
      // First run: no sections to wander into before the setup is done.
      h.append(el('div', { class: 'brand', text: L.appTitle }));
      return;
    }
    const navLink = (key, href) =>
      el('a', { href, 'aria-current': this.current === key ? 'page' : null, text: L.nav[key] });
    h.append(el('nav', { class: 'nav', 'aria-label': L.nav.sections }, [navLink('talk', '#/talk'), navLink('reading', '#/reading'), navLink('vocab', '#/vocab'), navLink('history', '#/history')]));
    const center = el('div', { class: 'header-center' });
    if (this.current === 'talk') this.talk.renderHeaderCenter(center);
    h.append(center);
    const conn = this.activeConnection;
    h.append(
      el('a', { class: conn ? 'conn-chip' : 'conn-chip none', href: '#/settings/connections', 'data-testid': 'active-connection' }, [
        el('span', { class: 'dot', 'aria-hidden': 'true' }),
        el('span', { text: conn ? `${conn.name} · ${conn.model}` : L.talk.noConnectionTitle }),
      ]),
    );
    h.append(
      el('a', { class: 'icon-link', href: '#/settings/connections', 'aria-label': L.nav.settings, 'aria-current': this.current === 'settings' ? 'page' : null }, [icons.settings()]),
    );
  }
}

