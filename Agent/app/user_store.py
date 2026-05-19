from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

import chromadb


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class UserRecord:
    user_id: str
    username: str
    password_hash: str
    password_salt: str
    full_name: str = ""
    settings: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utc_now_iso)
    updated_at: str = field(default_factory=_utc_now_iso)

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "full_name": self.full_name,
            "settings": self.settings,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class UserStore(Protocol):
    backend: str

    def create_user(self, username: str, password_hash: str, password_salt: str, full_name: str = "") -> UserRecord: ...

    def get_by_username(self, username: str) -> UserRecord | None: ...

    def get_by_user_id(self, user_id: str) -> UserRecord | None: ...

    def update_settings(self, user_id: str, updates: dict[str, Any]) -> UserRecord: ...

    def count_users(self) -> int: ...


class MemoryUserStore:
    backend = "memory"

    def __init__(self) -> None:
        self._users_by_id: dict[str, UserRecord] = {}
        self._id_by_username: dict[str, str] = {}

    def create_user(self, username: str, password_hash: str, password_salt: str, full_name: str = "") -> UserRecord:
        key = username.strip().lower()
        if not key:
            raise ValueError("username is required")
        if key in self._id_by_username:
            raise ValueError("username already exists")

        now = _utc_now_iso()
        user = UserRecord(
            user_id=f"usr_{uuid.uuid4().hex[:24]}",
            username=key,
            password_hash=password_hash,
            password_salt=password_salt,
            full_name=full_name.strip(),
            settings=self._default_settings(),
            created_at=now,
            updated_at=now,
        )
        self._users_by_id[user.user_id] = user
        self._id_by_username[key] = user.user_id
        return user

    def get_by_username(self, username: str) -> UserRecord | None:
        key = username.strip().lower()
        user_id = self._id_by_username.get(key)
        if not user_id:
            return None
        return self._users_by_id.get(user_id)

    def get_by_user_id(self, user_id: str) -> UserRecord | None:
        return self._users_by_id.get(user_id)

    def update_settings(self, user_id: str, updates: dict[str, Any]) -> UserRecord:
        user = self._users_by_id.get(user_id)
        if not user:
            raise ValueError("user not found")
        merged = dict(user.settings)
        merged.update(updates)
        user.settings = merged
        user.updated_at = _utc_now_iso()
        return user

    def count_users(self) -> int:
        return len(self._users_by_id)

    @staticmethod
    def _default_settings() -> dict[str, Any]:
        return {
            "persona_name": "default",
            "persona_instruction": "",
            "preferred_orchestrator": "native",
            "default_top_k": 6,
            "default_use_web_search": False,
            "default_use_rerank": True,
            "enable_langsmith": False,
            "env_overrides": {},
        }


class VectorUserStore:
    backend = "vector"

    def __init__(self, db_path: Path, collection_name: str) -> None:
        self._db_path = db_path
        self._db_path.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(self._db_path))
        self._collection = self._client.get_or_create_collection(name=collection_name)

    def create_user(self, username: str, password_hash: str, password_salt: str, full_name: str = "") -> UserRecord:
        key = username.strip().lower()
        if not key:
            raise ValueError("username is required")
        if self.get_by_username(key):
            raise ValueError("username already exists")

        now = _utc_now_iso()
        user = UserRecord(
            user_id=f"usr_{uuid.uuid4().hex[:24]}",
            username=key,
            password_hash=password_hash,
            password_salt=password_salt,
            full_name=full_name.strip(),
            settings=MemoryUserStore._default_settings(),
            created_at=now,
            updated_at=now,
        )
        self._collection.add(
            ids=[user.user_id],
            documents=[f"user:{user.username}"],
            metadatas=[self._to_metadata(user)],
        )
        return user

    def get_by_username(self, username: str) -> UserRecord | None:
        key = username.strip().lower()
        if not key:
            return None
        result = self._collection.get(where={"username": key}, include=["metadatas"])
        ids = result.get("ids", []) or []
        if not ids:
            return None
        meta = (result.get("metadatas", []) or [{}])[0]
        return self._from_metadata(user_id=ids[0], meta=meta)

    def get_by_user_id(self, user_id: str) -> UserRecord | None:
        result = self._collection.get(ids=[user_id], include=["metadatas"])
        ids = result.get("ids", []) or []
        if not ids:
            return None
        meta = (result.get("metadatas", []) or [{}])[0]
        return self._from_metadata(user_id=ids[0], meta=meta)

    def update_settings(self, user_id: str, updates: dict[str, Any]) -> UserRecord:
        user = self.get_by_user_id(user_id)
        if not user:
            raise ValueError("user not found")
        merged = dict(user.settings)
        merged.update(updates)
        user.settings = merged
        user.updated_at = _utc_now_iso()

        self._collection.update(
            ids=[user.user_id],
            documents=[f"user:{user.username}"],
            metadatas=[self._to_metadata(user)],
        )
        return user

    def count_users(self) -> int:
        return int(self._collection.count())

    @staticmethod
    def _to_metadata(user: UserRecord) -> dict[str, Any]:
        return {
            "username": user.username,
            "password_hash": user.password_hash,
            "password_salt": user.password_salt,
            "full_name": user.full_name,
            "settings_json": json.dumps(user.settings, ensure_ascii=False),
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

    @staticmethod
    def _from_metadata(user_id: str, meta: dict[str, Any]) -> UserRecord:
        settings_json = str(meta.get("settings_json", "{}"))
        try:
            settings = json.loads(settings_json)
        except json.JSONDecodeError:
            settings = {}
        if not isinstance(settings, dict):
            settings = {}
        defaults = MemoryUserStore._default_settings()
        defaults.update(settings)
        return UserRecord(
            user_id=user_id,
            username=str(meta.get("username", "")),
            password_hash=str(meta.get("password_hash", "")),
            password_salt=str(meta.get("password_salt", "")),
            full_name=str(meta.get("full_name", "")),
            settings=defaults,
            created_at=str(meta.get("created_at", _utc_now_iso())),
            updated_at=str(meta.get("updated_at", _utc_now_iso())),
        )


class QdrantUserStore:
    backend = "qdrant"

    def __init__(self, host: str, port: int, collection_name: str) -> None:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams

        self._client = QdrantClient(host=host, port=port)
        self._collection = collection_name

        if not self._client.collection_exists(collection_name):
            self._client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1, distance=Distance.DOT),
            )

    def create_user(self, username: str, password_hash: str, password_salt: str, full_name: str = "") -> UserRecord:
        from qdrant_client.models import FieldCondition, Filter, MatchValue, PointStruct

        key = username.strip().lower()
        if not key:
            raise ValueError("username is required")
        if self.get_by_username(key):
            raise ValueError("username already exists")

        now = _utc_now_iso()
        new_uuid = uuid.uuid4()
        user = UserRecord(
            user_id=f"usr_{new_uuid.hex}",
            username=key,
            password_hash=password_hash,
            password_salt=password_salt,
            full_name=full_name.strip(),
            settings=MemoryUserStore._default_settings(),
            created_at=now,
            updated_at=now,
        )
        self._client.upsert(
            collection_name=self._collection,
            points=[PointStruct(id=str(new_uuid), vector=[0.0], payload=self._to_payload(user))],
        )
        return user

    def get_by_username(self, username: str) -> UserRecord | None:
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        key = username.strip().lower()
        if not key:
            return None
        results, _ = self._client.scroll(
            collection_name=self._collection,
            scroll_filter=Filter(must=[FieldCondition(key="username", match=MatchValue(value=key))]),
            limit=1,
            with_payload=True,
        )
        if not results:
            return None
        point = results[0]
        return self._from_payload(qdrant_id=str(point.id), payload=point.payload or {})

    def get_by_user_id(self, user_id: str) -> UserRecord | None:
        if not user_id.startswith("usr_"):
            return None
        try:
            qdrant_id = str(uuid.UUID(user_id[4:]))
        except ValueError:
            return None
        results = self._client.retrieve(
            collection_name=self._collection,
            ids=[qdrant_id],
            with_payload=True,
        )
        if not results:
            return None
        point = results[0]
        return self._from_payload(qdrant_id=str(point.id), payload=point.payload or {})

    def update_settings(self, user_id: str, updates: dict[str, Any]) -> UserRecord:
        from qdrant_client.models import PointStruct

        user = self.get_by_user_id(user_id)
        if not user:
            raise ValueError("user not found")
        merged = dict(user.settings)
        merged.update(updates)
        user.settings = merged
        user.updated_at = _utc_now_iso()

        qdrant_id = str(uuid.UUID(user_id[4:]))
        self._client.upsert(
            collection_name=self._collection,
            points=[PointStruct(id=qdrant_id, vector=[0.0], payload=self._to_payload(user))],
        )
        return user

    def count_users(self) -> int:
        info = self._client.get_collection(self._collection)
        return int(info.points_count or 0)

    @staticmethod
    def _to_payload(user: UserRecord) -> dict[str, Any]:
        return {
            "user_id": user.user_id,
            "username": user.username,
            "password_hash": user.password_hash,
            "password_salt": user.password_salt,
            "full_name": user.full_name,
            "settings_json": json.dumps(user.settings, ensure_ascii=False),
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

    @staticmethod
    def _from_payload(qdrant_id: str, payload: dict[str, Any]) -> UserRecord:
        settings_json = str(payload.get("settings_json", "{}"))
        try:
            settings = json.loads(settings_json)
        except json.JSONDecodeError:
            settings = {}
        if not isinstance(settings, dict):
            settings = {}
        defaults = MemoryUserStore._default_settings()
        defaults.update(settings)
        user_id = str(payload.get("user_id") or f"usr_{uuid.UUID(qdrant_id).hex}")
        return UserRecord(
            user_id=user_id,
            username=str(payload.get("username", "")),
            password_hash=str(payload.get("password_hash", "")),
            password_salt=str(payload.get("password_salt", "")),
            full_name=str(payload.get("full_name", "")),
            settings=defaults,
            created_at=str(payload.get("created_at", _utc_now_iso())),
            updated_at=str(payload.get("updated_at", _utc_now_iso())),
        )


class MariaDbUserStore:
    backend = "mariadb"

    def __init__(self, db_url: str) -> None:
        try:
            from sqlalchemy import JSON, Column, MetaData, String, Table, create_engine, select
            from sqlalchemy.exc import IntegrityError
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("SQLAlchemy + PyMySQL are required for MariaDB mode") from exc

        self._sa_select = select
        self._sa_integrity_error = IntegrityError
        self._engine = create_engine(db_url, pool_pre_ping=True, future=True)
        self._metadata = MetaData()
        self._users = Table(
            "users",
            self._metadata,
            Column("user_id", String(64), primary_key=True),
            Column("username", String(128), unique=True, nullable=False),
            Column("password_hash", String(256), nullable=False),
            Column("password_salt", String(128), nullable=False),
            Column("full_name", String(255), nullable=False, server_default=""),
            Column("settings", JSON, nullable=False),
            Column("created_at", String(64), nullable=False),
            Column("updated_at", String(64), nullable=False),
        )
        self._metadata.create_all(self._engine)

    def create_user(self, username: str, password_hash: str, password_salt: str, full_name: str = "") -> UserRecord:
        key = username.strip().lower()
        if not key:
            raise ValueError("username is required")
        now = _utc_now_iso()
        user = UserRecord(
            user_id=f"usr_{uuid.uuid4().hex[:24]}",
            username=key,
            password_hash=password_hash,
            password_salt=password_salt,
            full_name=full_name.strip(),
            settings=MemoryUserStore._default_settings(),
            created_at=now,
            updated_at=now,
        )
        try:
            with self._engine.begin() as conn:
                conn.execute(
                    self._users.insert().values(
                        user_id=user.user_id,
                        username=user.username,
                        password_hash=user.password_hash,
                        password_salt=user.password_salt,
                        full_name=user.full_name,
                        settings=user.settings,
                        created_at=user.created_at,
                        updated_at=user.updated_at,
                    )
                )
        except self._sa_integrity_error as exc:
            raise ValueError("username already exists") from exc
        return user

    def get_by_username(self, username: str) -> UserRecord | None:
        key = username.strip().lower()
        if not key:
            return None
        stmt = self._sa_select(self._users).where(self._users.c.username == key)
        with self._engine.connect() as conn:
            row = conn.execute(stmt).mappings().first()
        if not row:
            return None
        return self._from_row(row)

    def get_by_user_id(self, user_id: str) -> UserRecord | None:
        stmt = self._sa_select(self._users).where(self._users.c.user_id == user_id)
        with self._engine.connect() as conn:
            row = conn.execute(stmt).mappings().first()
        if not row:
            return None
        return self._from_row(row)

    def update_settings(self, user_id: str, updates: dict[str, Any]) -> UserRecord:
        user = self.get_by_user_id(user_id)
        if not user:
            raise ValueError("user not found")
        merged = dict(user.settings)
        merged.update(updates)
        user.settings = merged
        user.updated_at = _utc_now_iso()

        with self._engine.begin() as conn:
            conn.execute(
                self._users.update()
                .where(self._users.c.user_id == user.user_id)
                .values(settings=user.settings, updated_at=user.updated_at)
            )
        return user

    def count_users(self) -> int:
        stmt = self._sa_select(self._users)
        with self._engine.connect() as conn:
            return len(conn.execute(stmt).fetchall())

    @staticmethod
    def _from_row(row: Any) -> UserRecord:
        settings = row.get("settings") if isinstance(row, dict) else {}
        if not isinstance(settings, dict):
            settings = {}
        defaults = MemoryUserStore._default_settings()
        defaults.update(settings)
        return UserRecord(
            user_id=str(row.get("user_id", "")),
            username=str(row.get("username", "")),
            password_hash=str(row.get("password_hash", "")),
            password_salt=str(row.get("password_salt", "")),
            full_name=str(row.get("full_name", "")),
            settings=defaults,
            created_at=str(row.get("created_at", _utc_now_iso())),
            updated_at=str(row.get("updated_at", _utc_now_iso())),
        )


@dataclass
class UserStoreInit:
    store: UserStore
    warnings: list[str] = field(default_factory=list)


def _build_mariadb_url(
    *,
    mariadb_url: str,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> str:
    if mariadb_url.strip():
        return mariadb_url.strip()
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


def build_user_store(
    *,
    mode: str,
    vector_db_path: Path,
    vector_collection: str,
    qdrant_host: str,
    qdrant_port: int,
    qdrant_collection: str,
    mariadb_url: str,
    mariadb_host: str,
    mariadb_port: int,
    mariadb_user: str,
    mariadb_password: str,
    mariadb_database: str,
) -> UserStoreInit:
    desired = (mode or "auto").strip().lower()
    warnings: list[str] = []

    if desired == "qdrant":
        try:
            return UserStoreInit(
                store=QdrantUserStore(host=qdrant_host, port=qdrant_port, collection_name=qdrant_collection),
                warnings=warnings,
            )
        except Exception as exc:
            warnings.append(f"qdrant user store unavailable: {exc}")

    if desired in {"auto", "vector"}:
        try:
            return UserStoreInit(
                store=VectorUserStore(db_path=vector_db_path, collection_name=vector_collection),
                warnings=warnings,
            )
        except Exception as exc:
            warnings.append(f"vector user store unavailable: {exc}")

    if desired in {"auto", "vector", "mariadb"}:
        try:
            db_url = _build_mariadb_url(
                mariadb_url=mariadb_url,
                host=mariadb_host,
                port=mariadb_port,
                user=mariadb_user,
                password=mariadb_password,
                database=mariadb_database,
            )
            return UserStoreInit(store=MariaDbUserStore(db_url=db_url), warnings=warnings)
        except Exception as exc:
            warnings.append(f"mariadb user store unavailable: {exc}")

    warnings.append("fallback to memory user store")
    return UserStoreInit(store=MemoryUserStore(), warnings=warnings)
