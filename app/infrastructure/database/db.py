"""Database instance module to avoid circular imports"""
from app.infrastructure.database.connection import DatabaseConnection

# Global database connection instance
db = DatabaseConnection()
