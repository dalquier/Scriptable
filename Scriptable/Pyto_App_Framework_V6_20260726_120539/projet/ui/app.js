(() => {
  "use strict";

  let payload = window.__INITIAL_STATE__ || { state: {}, capabilities: {}, version: "6.0.0" };

  const byId = (id) => document.getElementById(id);
  const encode = (value) => encodeURIComponent(String(value ?? ""));

  function send(action, parameters = {}) {
    const query = Object.entries(parameters)
      .map(([key, value]) => `${encode(key)}=${encode(value)}`)
      .join("&");
    window.location.href = `pytoapp://${action}${query ? `?${query}` : ""}`;
  }

  function applyTheme(theme) {
    if (theme === "light" || theme === "dark") {
      document.documentElement.dataset.theme = theme;
    } else {
      delete document.documentElement.dataset.theme;
    }
  }

  function render(nextPayload) {
    payload = nextPayload || payload;
    const state = payload.state || {};

    byId("greeting").textContent = `Bonjour ${state.display_name || "Damien"}`;
    byId("launch-count").textContent = state.launch_count || 0;
    byId("action-count").textContent = state.action_count || 0;
    byId("last-action").textContent = state.last_action || "Aucune";

    const nameInput = byId("display-name");
    if (document.activeElement !== nameInput) {
      nameInput.value = state.display_name || "";
    }

    byId("theme-select").value = state.theme || "system";
    applyTheme(state.theme || "system");

    const list = byId("activity-list");
    const activity = Array.isArray(state.activity) ? state.activity : [];
    if (!activity.length) {
      list.innerHTML = '<div class="empty">Aucune activité enregistrée.</div>';
    } else {
      list.innerHTML = activity.map((item) => `
        <article class="activity-item">
          <strong>${escapeHtml(item.label || "Action")}</strong>
          <small>${escapeHtml(item.date || "")}</small>
        </article>
      `).join("");
    }
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function activateScreen(target) {
    document.querySelectorAll(".screen").forEach((screen) => {
      screen.classList.toggle("active", screen.dataset.screen === target);
    });
    document.querySelectorAll(".tab").forEach((tab) => {
      tab.classList.toggle("active", tab.dataset.target === target);
    });
  }

  document.addEventListener("click", (event) => {
    const tab = event.target.closest("[data-target]");
    if (tab) {
      activateScreen(tab.dataset.target);
      return;
    }

    const control = event.target.closest("[data-action]");
    if (!control) return;

    const action = control.dataset.action;
    if (action === "reset") {
      const accepted = window.confirm("Réinitialiser toutes les données locales ?");
      if (!accepted) return;
    }
    send(action);
  });

  byId("display-name").addEventListener("change", (event) => {
    const value = event.target.value.trim() || "Damien";
    send("set-preference", { key: "display_name", value });
  });

  byId("theme-select").addEventListener("change", (event) => {
    send("set-preference", { key: "theme", value: event.target.value });
  });

  window.addEventListener("stateChanged", (event) => render(event.detail));
  window.addEventListener("appError", (event) => {
    window.alert(event.detail?.message || "Une erreur est survenue.");
  });

  render(payload);
  send("ready");
})();
