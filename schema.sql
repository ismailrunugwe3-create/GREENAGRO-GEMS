CREATE TABLE IF NOT EXISTS shared_storage (
 storage_key TEXT PRIMARY KEY, payload TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1,
 updated_at TEXT NOT NULL, updated_by TEXT
);
CREATE TABLE IF NOT EXISTS audit_log (
 id TEXT PRIMARY KEY, record_id TEXT, event TEXT, module_id TEXT, form_path TEXT,
 actor TEXT, at TEXT, version INTEGER, snapshot TEXT
);
CREATE INDEX IF NOT EXISTS ix_audit_record ON audit_log(record_id, at);
CREATE TABLE IF NOT EXISTS records (
 id TEXT PRIMARY KEY, module_id TEXT NOT NULL, form_path TEXT NOT NULL, record_type TEXT,
 status TEXT DEFAULT 'DRAFT', payload TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1,
 created_at TEXT NOT NULL, created_by TEXT, updated_at TEXT NOT NULL, updated_by TEXT,
 project TEXT, site TEXT
);
CREATE INDEX IF NOT EXISTS ix_records_form ON records(form_path, updated_at);
CREATE TABLE IF NOT EXISTS master_data (
 kind TEXT NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL, active INTEGER DEFAULT 1,
 updated_at TEXT, PRIMARY KEY(kind,key)
);
CREATE TABLE IF NOT EXISTS entities (
 id TEXT PRIMARY KEY, kind TEXT NOT NULL, code TEXT NOT NULL, name TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'ACTIVE', payload TEXT NOT NULL DEFAULT '{}',
 version INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL, created_by TEXT,
 updated_at TEXT NOT NULL, updated_by TEXT, UNIQUE(kind,code)
);
CREATE INDEX IF NOT EXISTS ix_entities_kind ON entities(kind,status,name);
CREATE TABLE IF NOT EXISTS entity_links (
 id TEXT PRIMARY KEY, from_id TEXT NOT NULL, to_id TEXT NOT NULL, relation TEXT NOT NULL,
 created_at TEXT NOT NULL, created_by TEXT, UNIQUE(from_id,to_id,relation)
);
