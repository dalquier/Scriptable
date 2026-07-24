# Arborescence

```text
TCC_Budy_Phase_2_1_20260725_014200/
├── 00_README.md
├── 01_ARBORESCENCE.md
├── 02_MANIFEST.json
├── 03_INSTALLATION.md
├── 04_CHANGELOG.md
└── projet/
    ├── .gitignore
    ├── app.py
    ├── bootstrap.py
    ├── run_tests.py
    ├── migrations/
    │   └── 001_conversations_messages.sql
    ├── tcc_budy/
    │   ├── application/
    │   │   └── conversation_service.py
    │   ├── domain/
    │   │   └── models.py
    │   ├── providers/
    │   │   ├── base.py
    │   │   ├── factory.py
    │   │   ├── openai_provider.py
    │   │   └── simulator.py
    │   ├── storage/
    │   │   ├── conversation_repository.py
    │   │   ├── database.py
    │   │   └── migrations.py
    │   ├── support/
    │   │   ├── config.py
    │   │   ├── errors.py
    │   │   └── logging_config.py
    │   └── ui/
    │       ├── webview.py
    │       └── assets/
    │           ├── app.css
    │           ├── app.js
    │           └── index.html
    └── tests/
        └── test_core.py
```