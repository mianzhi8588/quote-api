import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


DATABASE_DIR = Path("data")
DATABASE_PATH = DATABASE_DIR / "quotes.db"
QUOTE_EXPIRATION_DAYS = 7


@dataclass(frozen=True)
class QuotePriceRecord:
    quote_id: str
    unit_price: float
    total_price: float
    quantity: int
    currency: str
    status: str
    created_at: str
    expires_at: str

    def to_price_response(self) -> dict[str, str | int | float]:
        return {
            "unit_price": self.unit_price,
            "total_price": self.total_price,
            "quantity": self.quantity,
            "currency": self.currency,
        }


def get_connection() -> sqlite3.Connection:
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DATABASE_PATH)


def init_quote_storage() -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS quotes (
                quote_id TEXT PRIMARY KEY,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                currency TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
            """
        )

        connection.commit()


def save_quote_price(
    unit_price: float,
    total_price: float,
    quantity: int,
    currency: str = "USD",
) -> QuotePriceRecord:
    quote_id = str(uuid.uuid4())

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=QUOTE_EXPIRATION_DAYS)

    record = QuotePriceRecord(
        quote_id=quote_id,
        unit_price=round(unit_price, 6),
        total_price=round(total_price, 2),
        quantity=quantity,
        currency=currency,
        status="active",
        created_at=now.isoformat(),
        expires_at=expires_at.isoformat(),
    )

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO quotes (
                quote_id,
                unit_price,
                total_price,
                quantity,
                currency,
                status,
                created_at,
                expires_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.quote_id,
                record.unit_price,
                record.total_price,
                record.quantity,
                record.currency,
                record.status,
                record.created_at,
                record.expires_at,
            ),
        )

        connection.commit()

    return record


def get_quote_price(quote_id: str) -> Optional[QuotePriceRecord]:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                quote_id,
                unit_price,
                total_price,
                quantity,
                currency,
                status,
                created_at,
                expires_at
            FROM quotes
            WHERE quote_id = ?
            """,
            (quote_id,),
        )

        row = cursor.fetchone()

    if row is None:
        return None

    record = QuotePriceRecord(
        quote_id=row[0],
        unit_price=row[1],
        total_price=row[2],
        quantity=row[3],
        currency=row[4],
        status=row[5],
        created_at=row[6],
        expires_at=row[7],
    )

    expires_at = datetime.fromisoformat(record.expires_at)
    now = datetime.now(timezone.utc)

    if expires_at < now:
        mark_quote_expired(record.quote_id)
        return None

    if record.status != "active":
        return None

    return record


def mark_quote_expired(quote_id: str) -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE quotes
            SET status = 'expired'
            WHERE quote_id = ?
            """,
            (quote_id,),
        )

        connection.commit()