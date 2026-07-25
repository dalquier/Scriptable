const app = document.getElementById('app');

const state = {
  view: 'today',
  conversations: [],
  current: null,
  messages: [],
  busy: false,
  error: null,
  failedUserMessageId: null,
  deleteTarget: null,
  provider: '',
  model: ''
};

async function pyto(action, payload = {}) {
  try {
    const response = await fetch('/api', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({action, payload})
    });

    let data;
    try {
      data = await response.json();
    } catch (_) {
      throw new Error(`Réponse locale invalide (${response.status}).`);
    }

    if (!response.ok) {
      throw new Error(data.message || `Erreur locale HTTP ${response.status}.`);
    }

    handle(data);
    return data;
  } catch (error) {
    state.busy = false;
    state.error = error && error.message
      ? error.message
      : 'La commande n’a pas pu être exécutée.';
    render();
    return null;
  }
}

function handle(data) {
  state.busy = false;

  if (data.type === 'initial_state') {
    state.conversations = data.conversations || [];
    state.provider = data.provider || '';
    state.model = data.model || '';
  } else if (data.type === 'conversation_created') {
    state.current = data.conversation;
    state.messages = [];
    state.view = 'conversation';
    state.error = null;
  } else if (data.type === 'conversation_loaded') {
    state.current = data.conversation;
    state.messages = data.messages || [];
    state.view = 'conversation';
    state.error = null;
  } else if (data.type === 'message_result') {
    merge(data.user_message);
    merge(data.assistant_message);
    state.current = data.conversation;
    clearDraft();

    if (data.provider_error) {
      state.error = data.error_message || 'Réponse impossible.';
      state.failedUserMessageId = data.user_message?.id || null;
    } else {
      state.error = null;
      state.failedUserMessageId = null;
    }

    pyto('list_conversations');
  } else if (data.type === 'conversation_deleted') {
    state.conversations = state.conversations.filter(
      conversation => conversation.id !== data.conversation_id
    );
    state.view = 'history';
    state.deleteTarget = null;
    state.error = null;
  } else if (data.type === 'error') {
    state.error = data.message || 'Erreur';
  }

  render();
}

function merge(message) {
  if (!message) return;
  const index = state.messages.findIndex(item => item.id === message.id);
  if (index >= 0) state.messages[index] = message;
  else state.messages.push(message);
  state.messages.sort((a, b) => a.sequence - b.sequence);
}

function render() {
  if (state.view === 'conversation') {
    renderConversation();
    return;
  }

  app.innerHTML = `
    <div class="shell">
      <main class="page">
        ${state.error ? errorHtml(state.error) : ''}
        ${state.view === 'history' ? historyHtml() : todayHtml()}
      </main>
      <nav class="nav">
        <button class="${state.view === 'today' ? 'active' : ''}" onclick="go('today')">Aujourd’hui</button>
        <button class="${state.view === 'history' ? 'active' : ''}" onclick="go('history')">Historique</button>
      </nav>
      ${modalHtml()}
    </div>`;
}

function todayHtml() {
  const conversation = state.conversations[0];
  return `
    <section class="hero">
      <div class="eyebrow">Aujourd’hui</div>
      <h1>Comment puis-je vous aider&nbsp;?</h1>
      <p>Un espace simple pour clarifier ce qui se passe et choisir le prochain pas utile.</p>
      <div class="status-pill">
        <span class="status-dot"></span>${esc(state.provider)} · ${esc(state.model)}
      </div>
    </section>

    <section class="quick-grid">
      <button class="quick-card" onclick="startWith('J’ai besoin de parler d’une situation qui me préoccupe.')">
        <div class="quick-icon">💬</div>
        <div class="quick-title">Parler maintenant</div>
        <div class="quick-subtitle">Déposer une situation et y voir plus clair.</div>
      </button>
      <button class="quick-card" onclick="startWith('Je voudrais faire un bilan rapide de mon état aujourd’hui.')">
        <div class="quick-icon">🌿</div>
        <div class="quick-title">Faire un bilan</div>
        <div class="quick-subtitle">Énergie, humeur, tension et priorités du jour.</div>
      </button>
      <button class="quick-card" onclick="startWith('Je dois prendre une décision et j’aimerais la préparer.')">
        <div class="quick-icon">🧭</div>
        <div class="quick-title">Préparer une décision</div>
        <div class="quick-subtitle">Distinguer faits, options et conséquences.</div>
      </button>
      <button class="quick-card" onclick="startWith('Je voudrais comprendre une pensée ou une émotion récurrente.')">
        <div class="quick-icon">🧠</div>
        <div class="quick-title">Comprendre un schéma</div>
        <div class="quick-subtitle">Explorer une pensée, une émotion ou un déclencheur.</div>
      </button>
    </section>

    <section class="section">
      <div class="section-head">
        <h2>Continuer</h2>
        <button class="link-button" onclick="go('history')">Tout voir</button>
      </div>
      ${conversation ? `
        <article class="resume-card">
          <h3>${esc(conversation.title)}</h3>
          <p>${esc(conversation.last_message_preview || 'Aucun message')}</p>
          <button class="primary" onclick="openConversation('${conversation.id}')">Reprendre la conversation</button>
        </article>` : '<div class="empty">Aucune conversation pour le moment.</div>'}
      <button class="primary" onclick="createConversation()">Nouvelle conversation</button>
    </section>`;
}

function historyHtml() {
  return `
    <section class="hero">
      <div class="eyebrow">Historique</div>
      <h1>Vos conversations</h1>
      <p>Retrouvez, reprenez ou supprimez les échanges conservés localement sur cet appareil.</p>
    </section>
    <section class="history-list">
      ${state.conversations.length
        ? state.conversations.map(conversation => `
          <article class="history-card">
            <button class="history-open" onclick="openConversation('${conversation.id}')">
              <strong>${esc(conversation.title)}</strong>
              <div class="meta">${conversation.message_count} message${conversation.message_count > 1 ? 's' : ''}</div>
              <div class="preview">${esc(conversation.last_message_preview || '')}</div>
            </button>
            <button class="danger-link" onclick="askDelete('${conversation.id}')">Supprimer</button>
          </article>`).join('')
        : '<div class="empty">Aucune conversation.</div>'}
    </section>`;
}

function renderConversation() {
  app.innerHTML = `
    <div class="shell conversation-shell">
      <header class="conversation-top">
        <button class="back" onclick="leaveConversation()">‹ Retour</button>
        <div class="conversation-title">${esc(state.current?.title || 'Conversation')}</div>
      </header>
      <main class="conversation-content" id="messageList">
        <div class="messages">
          ${state.messages.length
            ? state.messages.map(message => `<div class="bubble ${message.role}">${esc(message.content)}</div>`).join('')
            : '<div class="empty">Écrivez librement ce qui vous préoccupe.</div>'}
          ${state.busy ? '<div class="loading">Réponse en préparation…</div>' : ''}
          ${state.error ? errorHtml(
            state.error,
            state.failedUserMessageId
              ? '<button class="link-button" onclick="retryResponse()">Réessayer</button>'
              : ''
          ) : ''}
        </div>
      </main>
      <footer class="composer">
        <div class="composer-inner">
          <textarea id="composer" rows="1" placeholder="Écrivez ce qui vous préoccupe…" oninput="draft(this)"></textarea>
          <button onclick="sendMessage()" ${state.busy ? 'disabled' : ''}>Envoyer</button>
        </div>
      </footer>
    </div>`;

  requestAnimationFrame(() => {
    const composer = document.getElementById('composer');
    if (composer) {
      composer.value = readDraft();
      resize(composer);
    }
    const list = document.getElementById('messageList');
    if (list) list.scrollTop = list.scrollHeight;
  });
}

function errorHtml(text, action = '') {
  return `
    <div class="error">
      <strong>Un problème est survenu</strong>
      <div>${esc(text)}</div>
      ${action}
    </div>`;
}

function modalHtml() {
  if (!state.deleteTarget) return '';
  return `
    <div class="modal-backdrop">
      <div class="modal">
        <h2>Supprimer cette conversation&nbsp;?</h2>
        <p>Cette action supprime aussi tous ses messages.</p>
        <div class="modal-actions">
          <button onclick="cancelDelete()">Annuler</button>
          <button class="danger" onclick="confirmDelete()">Supprimer</button>
        </div>
      </div>
    </div>`;
}

function go(view) {
  state.view = view;
  state.error = null;
  pyto('list_conversations');
  render();
}

function leaveConversation() {
  state.view = 'today';
  state.error = null;
  state.failedUserMessageId = null;
  pyto('list_conversations');
  render();
}

function createConversation() {
  if (state.busy) return;
  state.busy = true;
  pyto('create_conversation');
  render();
}

async function startWith(text) {
  if (state.busy) return;
  state.busy = true;
  render();

  const data = await pyto('create_conversation');
  if (!data) return;

  state.current = data.conversation;
  state.messages = [];
  state.view = 'conversation';
  render();

  requestAnimationFrame(() => {
    const composer = document.getElementById('composer');
    if (composer) {
      composer.value = text;
      draft(composer);
      composer.focus();
    }
  });
}

function openConversation(id) {
  if (state.busy) return;
  state.busy = true;
  pyto('open_conversation', {conversation_id: id});
  render();
}

function sendMessage() {
  const composer = document.getElementById('composer');
  const text = (composer?.value || '').trim();
  if (!text || state.busy || !state.current) return;

  state.busy = true;
  state.error = null;
  state.failedUserMessageId = null;

  pyto('send_message', {
    conversation_id: state.current.id,
    text,
    request_id: crypto.randomUUID
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random()}`
  });
  render();
}

function retryResponse() {
  if (!state.failedUserMessageId || state.busy) return;
  state.busy = true;
  state.error = null;
  pyto('retry_response', {
    conversation_id: state.current.id,
    user_message_id: state.failedUserMessageId
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
  if (state.busy) return;
  state.busy = true;
  pyto('delete_conversation', {conversation_id: state.deleteTarget});
  render();
}

function draft(element) {
  if (!state.current) return;
  localStorage.setItem(`draft-${state.current.id}`, element.value);
  resize(element);
}

function readDraft() {
  return state.current
    ? localStorage.getItem(`draft-${state.current.id}`) || ''
    : '';
}

function clearDraft() {
  if (state.current) localStorage.removeItem(`draft-${state.current.id}`);
}

function resize(element) {
  element.style.height = 'auto';
  element.style.height = `${Math.min(element.scrollHeight, 126)}px`;
}

function esc(value = '') {
  return String(value).replace(/[&<>'"]/g, character => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  }[character]));
}

if (window.visualViewport) {
  const updateViewport = () => {
    document.documentElement.style.setProperty('--vh', `${window.visualViewport.height}px`);
  };
  visualViewport.addEventListener('resize', updateViewport);
  updateViewport();
}

render();
setTimeout(() => pyto('app_ready'), 0);
