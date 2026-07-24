# Changelog

## 3.1.0 — 24 juillet 2026

### Créé

- nouvelle livraison complète `AssistantIA corrigé` ;
- script de diagnostic Pyto ;
- documentation et manifeste entièrement reconstruits.

### Corrigé

- structure des messages envoyés à l'API OpenAI Responses ;
- gestion de la clé API privée ;
- suppression de la base SQLite préexistante de la livraison ;
- initialisation automatique d'une base propre ;
- compatibilité des constructeurs `Label`, `TextView` et `Button` avec Pyto ;
- présentation plein écran ;
- gestion des erreurs réseau et timeout ;
- cohérence des imports internes.

### Supprimé

- `config_local.py` contenant une valeur de clé locale ;
- base `assistantia_v3.sqlite3` issue de l'archive utilisateur ;
- fichiers macOS `__MACOSX`.

### Version précédente identifiable

- AssistantIA v3.0 transmis dans `AssistantIA(1).zip`.
