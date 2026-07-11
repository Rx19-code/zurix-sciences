"""
Admin Health Check endpoint.

Returns a snapshot of system health suitable for a 1-page ops dashboard:
- MongoDB: connectivity, version, database size, top collection counts
- Backup: most recent backup file, age in hours, size
- Disk: total / used / free / percent used
- Memory: total / available / used percent (Linux only, /proc/meminfo)
- Uptime: system boot time, current backend process start time
- Errors: last N lines of the most recent backend error log (best-effort)

Everything degrades gracefully: if a subsystem is unavailable, its field is
`null` and `error` explains why. This endpoint is ADMIN-ONLY.
"""
from __future__ import annotations

import logging
import os
import platform
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Header

from database import db, ADMIN_PASSWORD

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)

# ─── Config ─────────────────────────────────────────────────────────────────
BACKUP_DIR = Path(os.environ.get("ZURIX_BACKUP_DIR", "/var/backups/zurix-mongodb"))
BACKUP_MAX_AGE_HOURS = 26  # green ≤26h, yellow 26–48h, red >48h
DISK_YELLOW_PCT = 75
DISK_RED_PCT = 90
MEMORY_YELLOW_PCT = 80
MEMORY_RED_PCT = 92
COLLECTIONS_TO_COUNT = [
    "products", "users", "verification_logs", "verification_codes",
    "payment_orders", "wholesale_price_lists", "wholesale_invoices",
    "peptide_library", "stacks",
]

# Backend process start time (captured at import)
_BACKEND_STARTED_AT = time.time()


# ─── Helpers ────────────────────────────────────────────────────────────────
def _severity(pct: float, yellow: float, red: float) -> str:
    if pct >= red:
        return "red"
    if pct >= yellow:
        return "yellow"
    return "green"


def _fmt_bytes(n: int | float | None) -> str | None:
    if n is None:
        return None
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


async def _mongo_health() -> dict[str, Any]:
    try:
        # Server version
        info = await db.client.server_info()
        # DB stats
        stats = await db.command("dbStats")
        # Collection counts (parallel would be nicer but keep simple)
        counts: dict[str, int] = {}
        for name in COLLECTIONS_TO_COUNT:
            try:
                counts[name] = await db[name].count_documents({})
            except Exception:  # noqa: BLE001
                counts[name] = -1
        return {
            "status": "ok",
            "severity": "green",
            "version": info.get("version"),
            "db_name": stats.get("db"),
            "data_size_bytes": stats.get("dataSize"),
            "data_size": _fmt_bytes(stats.get("dataSize")),
            "storage_size_bytes": stats.get("storageSize"),
            "storage_size": _fmt_bytes(stats.get("storageSize")),
            "indexes": stats.get("indexes"),
            "objects": stats.get("objects"),
            "collections_count": stats.get("collections"),
            "counts": counts,
        }
    except Exception as e:
        logger.exception("Mongo health failed")
        return {"status": "error", "severity": "red", "error": str(e)}


def _backup_health() -> dict[str, Any]:
    try:
        if not BACKUP_DIR.exists():
            return {
                "status": "missing",
                "severity": "yellow",
                "error": f"Backup directory does not exist: {BACKUP_DIR}",
                "backups_dir": str(BACKUP_DIR),
            }
        files = sorted(
            BACKUP_DIR.glob("zurix-backup-*.tar.gz"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not files:
            return {
                "status": "empty",
                "severity": "red",
                "error": "No backup files found. Cron may not be running.",
                "backups_dir": str(BACKUP_DIR),
            }
        latest = files[0]
        stat = latest.stat()
        age_seconds = time.time() - stat.st_mtime
        age_hours = age_seconds / 3600
        severity = _severity(age_hours, BACKUP_MAX_AGE_HOURS, BACKUP_MAX_AGE_HOURS * 2)
        total_size = sum(f.stat().st_size for f in files)
        return {
            "status": "ok" if severity == "green" else severity,
            "severity": severity,
            "backups_dir": str(BACKUP_DIR),
            "latest_file": latest.name,
            "latest_size_bytes": stat.st_size,
            "latest_size": _fmt_bytes(stat.st_size),
            "latest_timestamp": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "latest_age_hours": round(age_hours, 1),
            "total_backups": len(files),
            "total_size_bytes": total_size,
            "total_size": _fmt_bytes(total_size),
        }
    except Exception as e:
        logger.exception("Backup health failed")
        return {"status": "error", "severity": "red", "error": str(e)}


def _disk_health() -> dict[str, Any]:
    try:
        total, used, free = shutil.disk_usage("/")
        pct = (used / total) * 100 if total else 0
        return {
            "status": "ok",
            "severity": _severity(pct, DISK_YELLOW_PCT, DISK_RED_PCT),
            "total_bytes": total,
            "used_bytes": used,
            "free_bytes": free,
            "total": _fmt_bytes(total),
            "used": _fmt_bytes(used),
            "free": _fmt_bytes(free),
            "percent_used": round(pct, 1),
        }
    except Exception as e:
        logger.exception("Disk health failed")
        return {"status": "error", "severity": "red", "error": str(e)}


def _memory_health() -> dict[str, Any]:
    """Read /proc/meminfo (Linux). Returns null-fields elsewhere."""
    try:
        meminfo_path = Path("/proc/meminfo")
        if not meminfo_path.exists():
            return {"status": "unavailable", "severity": "green", "error": "/proc/meminfo not present"}
        data: dict[str, int] = {}
        for line in meminfo_path.read_text().splitlines():
            parts = line.split(":")
            if len(parts) != 2:
                continue
            key = parts[0].strip()
            val_str = parts[1].strip().split()[0]
            try:
                data[key] = int(val_str) * 1024  # kB → bytes
            except ValueError:
                continue
        total = data.get("MemTotal", 0)
        available = data.get("MemAvailable", 0)
        used = total - available
        pct = (used / total) * 100 if total else 0
        return {
            "status": "ok",
            "severity": _severity(pct, MEMORY_YELLOW_PCT, MEMORY_RED_PCT),
            "total_bytes": total,
            "available_bytes": available,
            "used_bytes": used,
            "total": _fmt_bytes(total),
            "available": _fmt_bytes(available),
            "used": _fmt_bytes(used),
            "percent_used": round(pct, 1),
        }
    except Exception as e:
        logger.exception("Memory health failed")
        return {"status": "error", "severity": "red", "error": str(e)}


def _uptime_health() -> dict[str, Any]:
    try:
        # System uptime from /proc/uptime
        system_up_seconds = None
        uptime_path = Path("/proc/uptime")
        if uptime_path.exists():
            system_up_seconds = float(uptime_path.read_text().split()[0])

        backend_up_seconds = time.time() - _BACKEND_STARTED_AT

        def humanize(s: float | None) -> str | None:
            if s is None:
                return None
            days, rem = divmod(int(s), 86400)
            hours, rem = divmod(rem, 3600)
            minutes = rem // 60
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"

        return {
            "status": "ok",
            "severity": "green",
            "system_uptime_seconds": system_up_seconds,
            "system_uptime": humanize(system_up_seconds),
            "backend_uptime_seconds": round(backend_up_seconds, 1),
            "backend_uptime": humanize(backend_up_seconds),
            "backend_started_at": datetime.fromtimestamp(_BACKEND_STARTED_AT, tz=timezone.utc).isoformat(),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        }
    except Exception as e:
        logger.exception("Uptime health failed")
        return {"status": "error", "severity": "red", "error": str(e)}


def _errors_recent() -> dict[str, Any]:
    """Best-effort tail of the most recent backend error log."""
    candidates = [
        Path("/root/.pm2/logs/zurix-backend-error.log"),
        Path("/var/log/supervisor/backend.err.log"),
        Path("/var/log/zurix-backend.err.log"),
    ]
    for path in candidates:
        if path.exists():
            try:
                # Tail last ~40 lines efficiently
                with path.open("rb") as f:
                    f.seek(0, 2)
                    size = f.tell()
                    to_read = min(size, 12 * 1024)
                    f.seek(size - to_read, 0)
                    tail = f.read().decode(errors="replace")
                lines = [line for line in tail.splitlines() if line.strip()][-15:]
                return {
                    "status": "ok",
                    "severity": "green",
                    "log_file": str(path),
                    "lines": lines,
                }
            except Exception as e:  # noqa: BLE001
                logger.exception("Failed reading error log %s", path)
                return {"status": "error", "severity": "yellow", "error": str(e), "log_file": str(path)}
    return {"status": "unavailable", "severity": "green", "error": "No backend log file found"}


# ─── Endpoint ───────────────────────────────────────────────────────────────
@router.get("/admin/health")
async def admin_health(x_admin_password: str = Header(None)):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    checks = {
        "mongo": await _mongo_health(),
        "backup": _backup_health(),
        "disk": _disk_health(),
        "memory": _memory_health(),
        "uptime": _uptime_health(),
        "errors": _errors_recent(),
    }

    # Overall severity = worst of all
    order = {"green": 0, "yellow": 1, "red": 2}
    overall = "green"
    for c in checks.values():
        sev = c.get("severity", "green")
        if order.get(sev, 0) > order.get(overall, 0):
            overall = sev

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_severity": overall,
        "checks": checks,
    }
