"""
Módulo de Conexão com PostgreSQL
Gerencia a conexão com o banco de dados usando psycopg3
"""

import os
import logging
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Classe para gerenciar conexões com o PostgreSQL
    Singleton pattern - apenas uma instância da conexão
    """
    
    _instance: Optional['DatabaseConnection'] = None
    _connection_string: Optional[str] = None
    
    def __new__(cls):
        """
        Implementa o padrão Singleton
        Garante que apenas uma instância seja criada
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """
        Inicializa a string de conexão com base no .env
        """
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5433')
        db_name = os.getenv('DB_NAME', 'gf_informatica')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        
        # Monta a connection string no formato psycopg3
        self._connection_string = (
            f"host={db_host} "
            f"port={db_port} "
            f"dbname={db_name} "
            f"user={db_user} "
            f"password={db_password}"
        )
        
        logger.info(f"Conexão configurada para {db_name}@{db_host}:{db_port}")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager para obter conexão com o banco
        Garante que a conexão será fechada automaticamente
        
        Uso:
            with db.get_connection() as conn:
                # usa conn aqui
        
        Yields:
            psycopg.Connection: Conexão ativa com o banco
        """
        conn = None
        try:
            conn = psycopg.connect(self._connection_string)
            logger.debug("Conexão com banco estabelecida")
            yield conn
        except psycopg.Error as e:
            logger.error(f"Erro ao conectar ao banco: {e}")
            raise
        finally:
            if conn:
                conn.close()
                logger.debug("Conexão com banco fechada")
    
    @contextmanager
    def get_cursor(self, row_factory=dict_row):
        """
        Context manager para obter cursor
        Por padrão, retorna resultados como dicionários
        
        Args:
            row_factory: Tipo de retorno das linhas (dict_row, tuple_row, etc)
        
        Yields:
            psycopg.Cursor: Cursor para executar queries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(row_factory=row_factory)
            try:
                yield cursor
                conn.commit()  # Commit automático se tudo correr bem
            except Exception as e:
                conn.rollback()  # Rollback em caso de erro
                logger.error(f"Erro na execução do cursor: {e}")
                raise
            finally:
                cursor.close()
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[tuple] = None,
        fetch: bool = True
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Executa uma query SELECT e retorna os resultados
        
        Args:
            query: Query SQL a ser executada
            params: Parâmetros para a query (usar %s para placeholders)
            fetch: Se True, retorna os resultados; se False, apenas executa
        
        Returns:
            Lista de dicionários com os resultados ou None
        
        Exemplo:
            results = db.execute_query(
                "SELECT * FROM clientes WHERE cpf = %s",
                ("123.456.789-00",)
            )
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                
                if fetch:
                    results = cursor.fetchall()
                    logger.info(f"Query executada: {len(results)} registros retornados")
                    return results
                else:
                    logger.info("Query executada com sucesso (sem fetch)")
                    return None
                    
        except psycopg.Error as e:
            logger.error(f"Erro ao executar query: {e}")
            raise
    
    def execute_insert(
        self, 
        query: str, 
        params: Optional[tuple] = None,
        return_id: bool = True
    ) -> Optional[int]:
        """
        Executa um INSERT e opcionalmente retorna o ID gerado
        
        Args:
            query: Query INSERT a ser executada
            params: Parâmetros para a query
            return_id: Se True, retorna o ID do registro inserido
        
        Returns:
            ID do registro inserido ou None
        
        Exemplo:
            cliente_id = db.execute_insert(
                "INSERT INTO clientes (nome, cpf) VALUES (%s, %s) RETURNING id",
                ("João Silva", "123.456.789-00")
            )
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                
                if return_id:
                    result = cursor.fetchone()
                    inserted_id = result['id'] if result else None
                    logger.info(f"Registro inserido com ID: {inserted_id}")
                    return inserted_id
                else:
                    logger.info("Insert executado com sucesso")
                    return None
                    
        except psycopg.Error as e:
            logger.error(f"Erro ao executar insert: {e}")
            raise
    
    def execute_update(
        self, 
        query: str, 
        params: Optional[tuple] = None
    ) -> int:
        """
        Executa um UPDATE ou DELETE e retorna o número de linhas afetadas
        
        Args:
            query: Query UPDATE/DELETE a ser executada
            params: Parâmetros para a query
        
        Returns:
            Número de linhas afetadas
        
        Exemplo:
            rows = db.execute_update(
                "UPDATE clientes SET telefone = %s WHERE id = %s",
                ("11999999999", 1)
            )
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                rows_affected = cursor.rowcount
                logger.info(f"Update/Delete executado: {rows_affected} linhas afetadas")
                return rows_affected
                
        except psycopg.Error as e:
            logger.error(f"Erro ao executar update/delete: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Testa se a conexão com o banco está funcionando
        
        Returns:
            True se conectou com sucesso, False caso contrário
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    if result and result[0] == 1:
                        logger.info("✅ Teste de conexão: SUCESSO")
                        return True
            return False
        except Exception as e:
            logger.error(f"❌ Teste de conexão: FALHOU - {e}")
            return False


# Instância global (Singleton)
db = DatabaseConnection()


# Função auxiliar para facilitar o uso
def get_db() -> DatabaseConnection:
    """
    Retorna a instância global do DatabaseConnection
    
    Returns:
        DatabaseConnection: Instância única da conexão
    """
    return db