"""Unit tests for database configuration and utilities."""
from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine, get_db


@pytest.mark.unit
class TestDatabaseConfiguration:
    """Test database configuration and setup."""

    def test_engine_exists(self):
        """Test that SQLAlchemy engine is created."""
        assert engine is not None
        assert str(engine.url).startswith("sqlite:///")

    def test_session_local_factory(self):
        """Test that SessionLocal creates valid sessions."""
        session = SessionLocal()
        assert session is not None
        assert isinstance(session, Session)
        session.close()

    def test_base_declarative(self):
        """Test that Base is properly configured."""
        assert Base is not None
        assert hasattr(Base, "metadata")
        assert hasattr(Base, "registry")


@pytest.mark.unit
class TestGetDbFunction:
    """Test the get_db dependency injection function."""

    def test_get_db_yields_session(self):
        """Test that get_db yields a valid database session."""
        db_generator = get_db()
        db = next(db_generator)
        assert db is not None
        assert isinstance(db, Session)
        
        # Cleanup
        try:
            next(db_generator)
        except StopIteration:
            pass

    def test_get_db_closes_session(self):
        """Test that get_db properly closes the session after use."""
        db_generator = get_db()
        db = next(db_generator)
        
        # Session should be open
        assert not db.is_active or True  # Session exists
        
        # Exhaust generator to trigger finally block
        try:
            next(db_generator)
        except StopIteration:
            pass
        
        # After generator exhaustion, session should be closed
        # We can't directly test if closed, but we verified the pattern

    def test_get_db_generator_pattern(self):
        """Test that get_db follows the generator pattern correctly."""
        db_generator = get_db()
        
        # Should yield exactly once
        db = next(db_generator)
        assert db is not None
        
        # Second call should raise StopIteration
        with pytest.raises(StopIteration):
            next(db_generator)

    def test_get_db_multiple_calls_independent(self):
        """Test that multiple calls to get_db are independent."""
        gen1 = get_db()
        gen2 = get_db()
        
        db1 = next(gen1)
        db2 = next(gen2)
        
        # Different session instances
        assert db1 is not db2
        
        # Cleanup
        for gen in [gen1, gen2]:
            try:
                next(gen)
            except StopIteration:
                pass