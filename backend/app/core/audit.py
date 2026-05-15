import json
import logging
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from ..models.database import AuditLog

logger = logging.getLogger(__name__)


def log_event(
    db: Session,
    event_type: str,
    category: str,
    description: str,
    user_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    execution_time_ms: Optional[int] = None,
    ip_address: Optional[str] = None,
):
    """Logs an event to the audit_logs table."""
    try:
        db_log = AuditLog(
            user_id=user_id,
            event_type=event_type,
            category=category,
            description=description,
            # default=str so date/datetime/Decimal in metadata don't blow up
            # the audit write (which previously silently dropped the entry).
            event_metadata=json.dumps(metadata, default=str) if metadata else None,
            execution_time_ms=execution_time_ms,
            ip_address=ip_address,
        )
        db.add(db_log)
        db.commit()
    except Exception:
        logger.exception("Failed to write audit log entry")
        db.rollback()
