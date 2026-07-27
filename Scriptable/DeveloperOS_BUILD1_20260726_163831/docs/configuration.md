# Configuration

Priority, from lowest to highest: dataclass defaults; optional TOML file; environment variables prefixed `DEVELOPEROS_`; explicit call-site overrides. Unknown keys, unsupported environments, invalid log levels and invalid booleans raise `ConfigurationError`. `config/example.toml` documents supported keys.
