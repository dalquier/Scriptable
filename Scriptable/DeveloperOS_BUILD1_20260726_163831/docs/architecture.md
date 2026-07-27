# Architecture

DeveloperOS BUILD-1 uses a `src` layout. `bootstrap` composes infrastructure; `Kernel` owns lifecycle only; `ServiceContainer` owns foundational dependencies; `Settings` owns typed configuration; `HealthService` executes independent checks; diagnostics expose a safe support snapshot. Business behavior is intentionally excluded.
