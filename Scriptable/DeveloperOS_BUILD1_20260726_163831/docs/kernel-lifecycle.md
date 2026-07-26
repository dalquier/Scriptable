# Kernel lifecycle

States are `CREATED`, `INITIALIZING`, `INITIALIZED`, `STARTING`, `RUNNING`, `STOPPING`, `STOPPED` and `FAILED`. Transitions are centrally validated. Initialization, starting and stopping are synchronous and deterministic. Repeated start while running and repeated stop after stopping are no-ops. Boundary failures become `KernelCriticalError` and set `FAILED`.
