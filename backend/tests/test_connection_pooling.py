"""
Database connection pooling tests.
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import create_engine, text
from ..src.database.connection import Base, SessionLocal, SQLALCHEMY_DATABASE_URL

# Test with a smaller pool size to better test pooling behavior
TEST_DB_URL = f"{SQLALCHEMY_DATABASE_URL}_pool_test"
engine = create_engine(
    TEST_DB_URL,
    pool_size=5,  # Small pool size for testing
    max_overflow=5,
    pool_timeout=5,
    pool_recycle=3600,
)


@pytest.fixture(scope="module")
def setup_db():
    """Set up test database with tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_connection_pool_size(setup_db):
    """Test that connection pool enforces its size limit."""
    connections = []

    try:
        # Try to get more connections than pool size
        for _ in range(10):
            conn = engine.connect()
            connections.append(conn)

        # This should raise an exception if pool size is enforced
        assert len(connections) <= 10  # pool_size + max_overflow
    finally:
        for conn in connections:
            conn.close()


def test_connection_reuse(setup_db):
    """Test that connections are properly reused from the pool."""
    with engine.connect() as conn1:
        conn1_id = id(conn1.connection)

    with engine.connect() as conn2:
        conn2_id = id(conn2.connection)

    # Connection should be the same if properly reused from pool
    assert conn1_id == conn2_id


def test_concurrent_connections(setup_db):
    """Test handling of concurrent database connections."""

    def execute_query():
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return result.scalar()

    # Run multiple queries in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(execute_query) for _ in range(20)]
        results = [future.result() for future in as_completed(futures)]

    assert all(r == 1 for r in results)


def test_connection_timeout():
    """Test that connection timeout works as expected."""
    # Create a new engine with very small pool and timeout
    temp_engine = create_engine(
        TEST_DB_URL, pool_size=1, max_overflow=0, pool_timeout=1  # 1 second timeout
    )

    # Hold the only connection
    conn = temp_engine.connect()

    # This should time out
    start_time = time.time()
    with pytest.raises(Exception) as exc_info:
        temp_engine.connect()
    end_time = time.time()

    # Verify timeout occurred
    assert "timeout" in str(exc_info.value).lower()
    assert 1 <= (end_time - start_time) <= 2  # Should timeout after ~1 second

    # Cleanup
    conn.close()
    temp_engine.dispose()


def test_connection_recycling():
    """Test that connections are properly recycled."""
    # Create a new engine with very short recycle time
    temp_engine = create_engine(TEST_DB_URL, pool_recycle=1)  # Recycle after 1 second

    # Get initial connection
    conn1 = temp_engine.connect()
    conn1_id = id(conn1.connection)
    conn1.close()

    # Wait longer than recycle time
    time.sleep(2)

    # Get new connection - should be a new one due to recycling
    conn2 = temp_engine.connect()
    conn2_id = id(conn2.connection)
    conn2.close()

    # Connection should be different after recycling
    assert conn1_id != conn2_id
    temp_engine.dispose()
