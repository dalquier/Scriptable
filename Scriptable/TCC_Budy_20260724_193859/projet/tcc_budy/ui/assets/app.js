const state = {
  view: 'today',
  conversations: [],
  current: null,
  messages: [],
  busy: false,
  error: null,
  failedUserMessageId: null,
  deleteTarget: null,
};
const app = document.getElementById('app');

function pyto(action, payload={}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);

  return fetch('/api', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    cache: 'no-store',
    signal: controller.signal,
    body: JSON.stringify({action, payload}),
  })
    .then(async response => {
      let data;
      try {
        data = await response.json();
      } catch (_) {
        throw new Error('Réponse locale illisible.');
      }
      if (!response.ok) {
        throw new Error(data.message || 'Erreur du serveur local.');
      }
      window.receiveFromPyto(data);
      return data;
    })
    .catch(error => {
      const message = error && error.name === 'AbortError'
        ? 'Le serveur local ne répond pas.'
        : (error && error.message ? error.message : 'Connexion locale impossible.');
      window.receiveFromPyto({type: 'error', message});
      throw error;
    })
    .finally(() => clearTimeout(timeout));
}

window.receiveFromPyto = function(message) {
  const data = typeof message === 'string' ? JSON.parse(message) : message;
  state.busy = false;

  if (data.type === 'initial_state') {
    state.conversations = data.conversations || [];
  } else if (data.type === 'conversation_created') {
    state.current = data.conversation;
    state.messages = [];
    state.view = 'conversation';
    state.error = null;
    state.failedUserMessageId = null;
  } else if (data.type === 'conversation_loaded') {
    state.current = data.conversation;
    state.messages = data.messages || [];
    state.view = 'conversation';
    state.error = null;
    state.failedUserMessageId = null;
  } else if (data.type === 'message_result') {
    state.current = data.conversation;
    mergeMessage(data.user_message);
    mergeMessage(data.assistant_message);
    if (data.provider_error) {
      state.failedUserMessageId = data.user_message && data.user_message.id;
      state.error = data.error_message || 'La réponse n’a pas pu être générée.';
    } else {
      state.failedUserMessageId = null;
      state.error = null;
      clearDraft();
    }
    pyto('list_conversations');
  } else if (data.type === 'conversation_deleted') {
    state.conversations = state.conversations.filter(c => c.id !== data.conversation_id);
    if (state.current && state.current.id === data.conversation_id) {
      state.current = null;
      state.messages = [];
    }
    state.deleteTarget = null;
    state.view = 'history';
    state.error = null;
  } else if (data.type === 'closed') {
    return;
  } else if (data.type === 'error') {
    state.error = data.message || 'Une erreur est survenue.';
  }
  render();
};

function mergeMessage(message) {
  if (!message || !message.id) return;
  const index = state.messages.findIndex(item => item.id === message.id);
  if (index >= 0) state.messages[index] = message;
  else state.messages.push(message);
  state.messages.sort((a, b) => a.sequence - b.sequence);
}

function render() {
  if (state.view === 'conversation') return renderConversation();
  const title = state.view === 'history' ? 'Historique' : 'TCC Budy';
  app.innerHTML = `
    <div class="shell">
      <header class="header app-header"><span>${title}</span><button class="close-app" onclick="closeApp()">Fermer</button></header>
      <main class="content">
        ${state.error ? errorHtml(state.error) : ''}
        ${state.view === 'history' ? historyHtml() : todayHtml()}
      </main>
      <nav class="nav">
        <button class="${state.view === 'today' ? 'active' : ''}" onclick="go('today')">Aujourd’hui</button>
        <button class="${state.view === 'history' ? 'active' : ''}" onclick="go('history')">Historique</button>
      </nav>
      ${deleteModalHtml()}
    </div>`;
}

function todayHtml() {
  const last = state.conversations[0];
  return `
    <section class="hero">
      <h1>Comment puis-je vous aider aujourd’hui&nbsp;?</h1>
      <p class="muted">Les conversations sont enregistrées localement sur cet iPhone.</p>
    </section>
    ${last ? `
      <section class="card">
        <div class="eyebrow">Dernière conversation</div>
        <strong>${escapeHtml(last.title)}</strong>
        <p class="muted preview">${escapeHtml(last.last_message_preview || 'Aucun message')}</p>
        <div class="meta">${formatDate(last.updated_at)} · ${countLabel(last.message_count)}</div>
        <button class="primary" onclick="openConversation('${last.id}')">Reprendre</button>
      </section>` : '<p class="empty">Aucune conversation enregistrée.</p>'}
    <button class="primary" onclick="createConversation()" ${state.busy ? 'disabled' : ''}>Nouvelle conversation</button>`;
}

function historyHtml() {
  if (state.busy && !state.conversations.length) return loadingHtml('Chargement de l’historique…');
  if (!state.conversations.length) {
    return `<div class="empty">Aucune conversation enregistrée.</div><button class="primary" onclick="createConversation()">Nouvelle conversation</button>`;
  }
  return `<div class="history-list">${state.conversations.map(c => `
    <article class="card history-row">
      <button class="history-open" onclick="openConversation('${c.id}')">
        <strong>${escapeHtml(c.title)}</strong>
        <span class="meta">${formatDate(c.updated_at)} · ${countLabel(c.message_count)}</span>
        <span class="muted preview">${escapeHtml(c.last_message_preview || 'Aucun message')}</span>
      </button>
      <button class="danger-link" onclick="askDelete('${c.id}')" aria-label="Supprimer ${escapeAttr(c.title)}">Supprimer</button>
    </article>`).join('')}</div>`;
}

function renderConversation() {
  const currentId = state.current && state.current.id;
  app.innerHTML = `
    <div class="shell conversation-shell">
      <header class="header conversation-header">
        <button class="back" onclick="leaveConversation()">‹ Retour</button>
        <div class="conversation-title">${escapeHtml(state.current?.title || 'Conversation')}</div>
        <button class="close-app" onclick="closeApp()">Fermer</button>
      </header>
      <main class="content conversation-content" id="messageList">
        <div class="messages">
          ${state.messages.length ? state.messages.map(messageHtml).join('') : '<div class="empty">Écrivez librement ce qui vous préoccupe.</div>'}
          ${state.busy ? loadingHtml('Réponse en préparation…') : ''}
          ${state.error ? errorHtml(state.error, state.failedUserMessageId ? `<button onclick="retryResponse()">Réessayer</button>` : '') : ''}
        </div>
      </main>
      <footer class="composer" id="composerBar">
        <textarea id="composer" rows="1" placeholder="Écrivez ce qui vous préoccupe…" oninput="onDraftInput(this)"></textarea>
        <button id="sendButton" onclick="sendMessage()" ${state.busy ? 'disabled' : ''}>Envoyer</button>
      </footer>
    </div>`;

  requestAnimationFrame(() => {
    const composer = document.getElementById('composer');
    if (composer) {
      composer.value = readDraft(currentId);
      resizeComposer(composer);
      updateSendButton();
    }
    scrollToBottom();
  });
}

function messageHtml(message) {
  return `<div class="bubble ${message.role}">${escapeHtml(message.content)}</div>`;
}

function loadingHtml(text) {
  return `<div class="loading"><span class="spinner" aria-hidden="true"></span>${escapeHtml(text)}</div>`;
}

function errorHtml(text, action='') {
  return `<div class="error"><strong>Un problème est survenu</strong><div>${escapeHtml(text)}</div>${action}</div>`;
}

function deleteModalHtml() {
  if (!state.deleteTarget) return '';
  const conversation = state.conversations.find(c => c.id === state.deleteTarget);
  return `<div class="modal-backdrop" role="dialog" aria-modal="true">
    <div class="modal">
      <h2>Supprimer cette conversation&nbsp;?</h2>
      <p><strong>${escapeHtml(conversation?.title || 'Conversation')}</strong></p>
      <p class="muted">Tous les messages associés seront supprimés de cet appareil.</p>
      <div class="modal-actions">
        <button onclick="cancelDelete()">Annuler</button>
        <button class="danger" onclick="confirmDelete()">Supprimer</button>
      </div>
    </div>
  </div>`;
}

function closeApp() {
  if (state.busy) return;
  state.busy = true;
  pyto('close_app').catch(() => {
    state.busy = false;
  });
}

function go(view) {
  state.view = view;
  state.error = null;
  state.deleteTarget = null;
  pyto('list_conversations');
  render();
}

function leaveConversation() {
  state.view = 'today';
  state.error = null;
  pyto('list_conversations');
  render();
}

function createConversation() {
  if (state.busy) return;
  state.busy = true;
  state.error = null;
  pyto('create_conversation');
  render();
}

function openConversation(id) {
  if (state.busy) return;
  state.busy = true;
  state.error = null;
  pyto('open_conversation', { conversation_id: id });
  render();
}

function sendMessage() {
  const el = document.getElementById('composer');
  const text = (el && el.value || '').trim();
  if (!text || state.busy || !state.current) return;
  state.busy = true;
  state.error = null;
  state.failedUserMessageId = null;
  const requestId = makeRequestId();
  pyto('send_message', {
    conversation_id: state.current.id,
    text,
    request_id: requestId,
  });
  render();
}

function retryResponse() {
  if (!state.current || !state.failedUserMessageId || state.busy) return;
  state.busy = true;
  state.error = null;
  pyto('retry_response', {
    conversation_id: state.current.id,
    user_message_id: state.failedUserMessageId,
  });
  render();
}

function askDelete(id) {
  state.deleteTarget = id;
  render();
}
function cancelDelete() {
  state.deleteTarget = null;
  render();
}
function confirmDelete() {
  if (!state.deleteTarget || state.busy) return;
  state.busy = true;
  pyto('delete_conversation', { conversation_id: state.deleteTarget });
  render();
}

function onDraftInput(el) {
  if (!state.current) return;
  localStorage.setItem(draftKey(state.current.id), el.value);
  resizeComposer(el);
  updateSendButton();
}
function readDraft(id) {
  return id ? localStorage.getItem(draftKey(id)) || '' : '';
}
function clearDraft() {
  if (state.current) localStorage.removeItem(draftKey(state.current.id));
}
function draftKey(id) {
  return `tcc_budy_draft_${id}`;
}
function resizeComposer(el) {
  el.style.height = 'auto';
  el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
}
function updateSendButton() {
  const input = document.getElementById('composer');
  const button = document.getElementById('sendButton');
  if (button) button.disabled = state.busy || !input || !input.value.trim();
}
function scrollToBottom() {
  const list = document.getElementById('messageList');
  if (list) list.scrollTop = list.scrollHeight;
}
function makeRequestId() {
  if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}
function formatDate(value) {
  if (!value) return '';
  const date = new Date(value);
  const now = new Date();
  const sameDay = date.toDateString() === now.toDateString();
  if (sameDay) return date.toLocaleTimeString('fr-FR', {hour:'2-digit', minute:'2-digit'});
  return date.toLocaleDateString('fr-FR', {day:'2-digit', month:'short', year: date.getFullYear() === now.getFullYear() ? undefined : 'numeric'});
}
function countLabel(value) {
  const count = Number(value || 0);
  return `${count} message${count > 1 ? 's' : ''}`;
}
function escapeHtml(v='') {
  return String(v).replace(/[&<>'"]/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[s]));
}
function escapeAttr(v='') {
  return escapeHtml(v);
}

if (window.visualViewport) {
  const updateViewport = () => document.documentElement.style.setProperty('--viewport-height', `${window.visualViewport.height}px`);
  window.visualViewport.addEventListener('resize', updateViewport);
  window.visualViewport.addEventListener('scroll', updateViewport);
  updateViewport();
}

render();
setTimeout(() => pyto('app_ready'), 0);
