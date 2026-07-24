import hashlib
from pathlib import Path


class MigrationRunner:
    def __init__(self, database, migrations_dir: Path):
        self.database = database
        self.migrations_dir = Path(migrations_dir)

    def apply_all(self) -> None:
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        with self.database.transaction() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    applied_at TEXT NOT NULL
                )
                """
            )

        for path in sorted(self.migrations_dir.glob("*.sql")):
            version = int(path.name.split("_", 1)[0])
            sql = path.read_text(encoding="utf-8")
            checksum = hashlib.sha256(sql.encode("utf-8")).hexdigest()
            with self.database.read() as conn:
                row = conn.execute(
                    "SELECT checksum FROM schema_migrations WHERE version=?",
                    (version,),
                ).fetchone()
            if row:
                if row["checksum"] != checksum:
                    raise RuntimeError(f"Migration {version} checksum mismatch")
                continue
            with self.database.transaction() as conn:
                conn.executescript(sql)
                conn.execute(
                    "INSERT INTO schema_migrations(version,name,checksum,applied_at) "
                    "VALUES (?,?,?,CURRENT_TIMESTAMP)",
                    (version, path.name, checksum),
                )
