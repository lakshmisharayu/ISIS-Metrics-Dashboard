"""
Database module for storing and retrieving ISIS metrics history
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)

DB_PATH = 'data/isis_metrics.db'


def init_database():
    """Initialize SQLite database with required tables"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create metrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_lsps INTEGER,
            lsp_database_size INTEGER,
            isis_nodes INTEGER,
            prefixes INTEGER,
            database_overload BOOLEAN,
            lsp_count_l1 INTEGER,
            lsp_count_l2 INTEGER,
            adjacencies INTEGER,
            interfaces INTEGER,
            raw_data TEXT,
            UNIQUE(device, timestamp)
        )
    ''')
    
    # Create index for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_device_timestamp 
        ON metrics(device, timestamp DESC)
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")


def save_metrics(device: str, metrics: Dict) -> bool:
    """Save metrics to database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO metrics (
                device, timestamp, total_lsps, lsp_database_size, 
                isis_nodes, prefixes, database_overload, lsp_count_l1,
                lsp_count_l2, adjacencies, interfaces, raw_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            device,
            metrics.get('timestamp', datetime.utcnow().isoformat()),
            metrics.get('total_lsps', 0),
            metrics.get('lsp_database_size', 0),
            metrics.get('isis_nodes', 0),
            metrics.get('prefixes', 0),
            metrics.get('database_overload', False),
            metrics.get('lsp_count_l1', 0),
            metrics.get('lsp_count_l2', 0),
            metrics.get('adjacencies', 0),
            metrics.get('interfaces', 0),
            json.dumps(metrics, default=str)
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error saving metrics: {str(e)}")
        return False


def get_metrics_history(device: str, hours: int = 24) -> List[Dict]:
    """Get historical metrics for a device"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        
        cursor.execute('''
            SELECT * FROM metrics 
            WHERE device = ? AND timestamp > ?
            ORDER BY timestamp DESC
        ''', (device, cutoff_time))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching metrics history: {str(e)}")
        return []


def cleanup_old_data(days: int = 30):
    """Remove metrics older than specified days"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cutoff_time = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            DELETE FROM metrics WHERE timestamp < ?
        ''', (cutoff_time,))
        
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        
        logger.info(f"Deleted {deleted} old metrics records")
        return True
    except Exception as e:
        logger.error(f"Error cleaning up old data: {str(e)}")
        return False
