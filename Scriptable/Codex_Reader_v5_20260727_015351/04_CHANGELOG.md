# Changelog

## 5.0.0 — 2026-07-27

- Réécriture modulaire de l’application.
- Champ URL natif séparé de la page ChatGPT.
- Connexion Apple manuelle dans une WebView dédiée.
- Adaptateur multi-version pour l’exécution JavaScript.
- Fallback vers le WKWebView sous-jacent lorsque celui-ci est accessible.
- Extraction multi-sélecteurs des messages utilisateur et assistant.
- Vue résultat dédiée conservant titres, listes et blocs de code.
- Copie séparée de la question et de la réponse.
- Export Markdown et TXT.
- Historique local des derniers liens.
- Fenêtre présentée en feuille fermable.
- Diagnostic intégré des capacités WebView.

## Correctifs issus des prototypes

- Suppression de `ui.Button("Titre")`, incompatible avec la version Pyto testée.
- Suppression de la dépendance exclusive à `evaluate_javascript()`.
- Le lien est chargé comme URL et ne peut plus être envoyé comme prompt ChatGPT.
