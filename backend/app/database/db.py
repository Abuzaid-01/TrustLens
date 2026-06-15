"""
Database connection manager and initialization.
Uses SQLite for zero-setup deployment. Swap to PostgreSQL for production.
"""

import sqlite3
import os
from app.core.config import DB_PATH


def get_db() -> sqlite3.Connection:
    """Get a database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize database schema. Called on app startup."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS businesses (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            address TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            business_id TEXT NOT NULL,
            customer_name TEXT DEFAULT '',
            customer_email TEXT DEFAULT '',
            amount REAL DEFAULT 0.0,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            items TEXT DEFAULT '[]',
            review_submitted INTEGER DEFAULT 0,
            FOREIGN KEY (business_id) REFERENCES businesses(id)
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            business_id TEXT NOT NULL,
            review_text TEXT NOT NULL,
            trust_score INTEGER DEFAULT 0,
            trust_level TEXT DEFAULT 'Medium',
            action TEXT DEFAULT 'review',
            breakdown TEXT DEFAULT '{}',
            agents_log TEXT DEFAULT '{}',
            has_media INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (business_id) REFERENCES businesses(id)
        );

        CREATE TABLE IF NOT EXISTS review_media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT DEFAULT 'image',
            original_name TEXT DEFAULT '',
            vision_analysis TEXT DEFAULT '{}',
            matches_review INTEGER DEFAULT 1,
            match_score REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (review_id) REFERENCES reviews(id)
        );
    """)

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")
