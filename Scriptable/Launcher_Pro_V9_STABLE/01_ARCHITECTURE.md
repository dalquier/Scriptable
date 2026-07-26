# Launcher Pro V9 Stable

## Architecture

- controller/: boucle principale et orchestration
- core/: registre, import, exécution, journalisation
- ui/: interface Pyto uniquement
- data/: registre JSON et historique
- logs/: launcher.log
- tests/: tests automatisés

Principe fondamental : l'interface ne lance jamais directement un script ni un sélecteur de fichiers. Elle retourne uniquement une intention (run, import_script, import_project, rename, delete). Le contrôleur exécute cette intention, journalise le résultat puis recrée l'interface.
