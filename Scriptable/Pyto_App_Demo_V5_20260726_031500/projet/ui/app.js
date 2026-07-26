(() => {
  const titles = {
    home: "Accueil",
    activity: "Activité",
    architecture: "Architecture",
    settings: "Réglages",
  };

  let state = window.__INITIAL_STATE__ || {};
  let toastTimer = null;

  function send(action, params = {}) {
    const query = new URLSearchParams(params).toString();
    window.location.href = `pytoapp://${action}${query ? `?${query}` : ""}`;
  }

  function showToast(message) {
    if (!message) return;
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), 1800);
  }

  function formatDate(value) {
    try {
      return new Intl.DateTimeFormat("fr-FR", {
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      }).format(new Date(value));
    } catch (_) {
      return value || "";
    }
  }

  function renderActivity() {
    const container = document.getElementById("activity-list");
    const activities = Array.isArray(state.activities) ? state.activities : [];
    if (!activities.length) {
      container.innerHTML = '<div class="empty-state">Aucune activité enregistrée.</div>';
      return;
    }
    container.innerHTML = activities.map(item => `
      <div class="activity-item">
        <span class="activity-dot"></span>
        <div><strong>${escapeHtml(item.title || "Activité")}</strong><small>${formatDate(item.timestamp)}</small></div>
      </div>`).join("");
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, char => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;"
    })[char]);
  }

  function render() {
    document.getElementById("display-name").textContent = state.display_name || "Damien";
    document.getElementById("launch-count").textContent = state.launch_count || 0;
    document.getElementById("action-count").textContent = state.action_count || 0;
    document.getElementById("name-input").value = state.display_name || "Damien";
    document.getElementById("notifications-toggle").checked = state.notifications_enabled !== false;
    renderActivity();
  }

  function selectScreen(target) {
    document.querySelectorAll(".screen").forEach(screen => {
      screen.classList.toggle("active", screen.dataset.screen === target);
    });
    document.querySelectorAll(".tab").forEach(tab => {
      tab.classList.toggle("active", tab.dataset.target === target);
    });
    document.getElementById("screen-title").textContent = titles[target] || "Application";
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  document.addEventListener("click", event => {
    const tab = event.target.closest("[data-target]");
    if (tab) {
      selectScreen(tab.dataset.target);
      return;
    }

    const actionButton = event.target.closest("[data-action]");
    if (!actionButton) return;
    const action = actionButton.dataset.action;

    if (action === "open-url") {
      send(action, { url: actionButton.dataset.url || "https://pyto.app" });
      return;
    }

    if (action === "reset") {
      if (confirm("Réinitialiser toutes les données de démonstration ?")) send("reset");
      return;
    }

    send(action);
  });

  document.getElementById("save-name").addEventListener("click", () => {
    const value = document.getElementById("name-input").value.trim() || "Damien";
    send("preference", { key: "display_name", value });
  });

  document.getElementById("notifications-toggle").addEventListener("change", event => {
    send("preference", {
      key: "notifications_enabled",
      value: event.target.checked ? "true" : "false",
    });
  });

  window.PytoApp = {
    receiveState(nextState, message) {
      state = nextState || {};
      render();
      showToast(message);
    },
    receiveError(message) {
      showToast(`Erreur : ${message}`);
    },
  };

  render();
})();
