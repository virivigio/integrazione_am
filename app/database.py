import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from app.config import get_settings

_pool: MySQLConnectionPool | None = None


def get_pool() -> MySQLConnectionPool:
    global _pool
    if _pool is None:
        s = get_settings()
        _pool = MySQLConnectionPool(
            pool_name="orders_pool",
            pool_size=5,
            host=s.DB_HOST,
            port=s.DB_PORT,
            database=s.DB_NAME,
            user=s.DB_USERNAME,
            password=s.DB_PASSWORD,
            charset="utf8mb4",
            use_pure=True,
        )
    return _pool


def execute_query(sql: str, params: tuple = ()) -> list[dict]:
    """Execute a SELECT query and return rows as list of dicts."""
    pool = get_pool()
    conn = pool.get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()
        # Convert non-serializable types (datetime, Decimal) to str/float
        result = []
        for row in rows:
            clean = {}
            for k, v in row.items():
                if hasattr(v, "isoformat"):
                    clean[k] = v.isoformat()
                else:
                    clean[k] = v
            result.append(clean)
        return result
    finally:
        conn.close()
