"""
Módulo de banco de dados
Gerencia conexões e operações com PostgreSQL
"""

from .connection import DatabaseConnection, db, get_db

__all__ = ['DatabaseConnection', 'db', 'get_db']