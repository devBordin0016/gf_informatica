"""
Serviço de Autenticação
Gerencia login e autenticação de usuários
"""

import logging
import bcrypt
from typing import Optional, Dict, Any
from database.connection import db

logger = logging.getLogger(__name__)


class AuthService:
    """
    Serviço de autenticação de usuários
    """
    
    @staticmethod
    def autenticar(username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica um usuário com username e senha
        
        Args:
            username: Nome de usuário
            password: Senha em texto plano
        
        Returns:
            Dicionário com dados do usuário se autenticado, None caso contrário
        """
        if not username or not password:
            logger.warning("Tentativa de login com credenciais vazias")
            return None
        
        try:
            # Busca usuário no banco
            query = """
                SELECT id, username, password_hash, nome_completo, email, ativo
                FROM usuarios
                WHERE username = %s
            """
            
            results = db.execute_query(query, (username,))
            
            if not results:
                logger.warning(f"Usuário não encontrado: {username}")
                return None
            
            usuario = results[0]
            
            # Verifica se usuário está ativo
            if not usuario['ativo']:
                logger.warning(f"Tentativa de login com usuário inativo: {username}")
                return None
            
            # Verifica a senha com bcrypt
            password_hash = usuario['password_hash']
            
            if AuthService._verificar_senha(password, password_hash):
                logger.info(f"Login bem-sucedido: {username}")
                
                # Remove o hash da senha antes de retornar
                del usuario['password_hash']
                return usuario
            else:
                logger.warning(f"Senha incorreta para usuário: {username}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao autenticar usuário: {e}")
            return None
    
    @staticmethod
    def alterar_senha(
        usuario_id: int,
        senha_atual: str,
        senha_nova: str
    ) -> bool:
        """
        Altera a senha de um usuário
        
        Args:
            usuario_id: ID do usuário
            senha_atual: Senha atual (para validação)
            senha_nova: Nova senha
        
        Returns:
            True se alterada com sucesso, False caso contrário
        """
        if not senha_nova or len(senha_nova) < 4:
            raise ValueError("A nova senha deve ter no mínimo 4 caracteres")
        
        try:
            # Busca usuário
            query = "SELECT password_hash FROM usuarios WHERE id = %s"
            results = db.execute_query(query, (usuario_id,))
            
            if not results:
                raise ValueError(f"Usuário ID {usuario_id} não encontrado")
            
            password_hash_atual = results[0]['password_hash']
            
            # Verifica senha atual
            if not AuthService._verificar_senha(senha_atual, password_hash_atual):
                logger.warning(f"Senha atual incorreta para usuário ID {usuario_id}")
                return False
            
            # Gera hash da nova senha
            novo_hash = AuthService._gerar_hash_senha(senha_nova)
            
            # Atualiza no banco
            query_update = "UPDATE usuarios SET password_hash = %s WHERE id = %s"
            rows = db.execute_update(query_update, (novo_hash, usuario_id))
            
            if rows > 0:
                logger.info(f"Senha alterada para usuário ID {usuario_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erro ao alterar senha: {e}")
            raise
    
    @staticmethod
    def criar_usuario(
        username: str,
        password: str,
        nome_completo: str,
        email: str
    ) -> Optional[int]:
        """
        Cria um novo usuário no sistema
        
        Args:
            username: Nome de usuário (único)
            password: Senha em texto plano
            nome_completo: Nome completo do usuário
            email: Email do usuário
        
        Returns:
            ID do usuário criado ou None
        """
        # Validações
        if not username or len(username) < 3:
            raise ValueError("Username deve ter no mínimo 3 caracteres")
        
        if not password or len(password) < 4:
            raise ValueError("Senha deve ter no mínimo 4 caracteres")
        
        if not nome_completo or not nome_completo.strip():
            raise ValueError("Nome completo é obrigatório")
        
        if not email or '@' not in email:
            raise ValueError("Email inválido")
        
        # Verifica se username já existe
        query_check = "SELECT id FROM usuarios WHERE username = %s"
        existing = db.execute_query(query_check, (username,))
        
        if existing:
            raise ValueError(f"Username '{username}' já está em uso")
        
        # Verifica se email já existe
        query_check_email = "SELECT id FROM usuarios WHERE email = %s"
        existing_email = db.execute_query(query_check_email, (email,))
        
        if existing_email:
            raise ValueError(f"Email '{email}' já está em uso")
        
        try:
            # Gera hash da senha
            password_hash = AuthService._gerar_hash_senha(password)
            
            # Insere no banco
            query = """
                INSERT INTO usuarios (username, password_hash, nome_completo, email, ativo)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """
            
            usuario_id = db.execute_insert(
                query,
                (username, password_hash, nome_completo, email, True)
            )
            
            logger.info(f"Novo usuário criado: {username} (ID={usuario_id})")
            return usuario_id
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            raise
    
    @staticmethod
    def listar_usuarios() -> list:
        """
        Lista todos os usuários (sem o hash das senhas)
        
        Returns:
            Lista de usuários
        """
        try:
            query = """
                SELECT id, username, nome_completo, email, ativo, criado_em
                FROM usuarios
                ORDER BY nome_completo
            """
            
            results = db.execute_query(query)
            return results or []
            
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {e}")
            raise
    
    @staticmethod
    def ativar_desativar_usuario(usuario_id: int, ativo: bool) -> bool:
        """
        Ativa ou desativa um usuário
        
        Args:
            usuario_id: ID do usuário
            ativo: True para ativar, False para desativar
        
        Returns:
            True se atualizado com sucesso
        """
        try:
            query = "UPDATE usuarios SET ativo = %s WHERE id = %s"
            rows = db.execute_update(query, (ativo, usuario_id))
            
            if rows > 0:
                status = "ativado" if ativo else "desativado"
                logger.info(f"Usuário ID {usuario_id} {status}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erro ao ativar/desativar usuário: {e}")
            raise
    
    @staticmethod
    def _gerar_hash_senha(password: str) -> str:
        """
        Gera hash bcrypt da senha
        
        Args:
            password: Senha em texto plano
        
        Returns:
            Hash bcrypt da senha
        """
        # Gera salt e hash
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8')
    
    @staticmethod
    def _verificar_senha(password: str, password_hash: str) -> bool:
        """
        Verifica se a senha corresponde ao hash
        
        Args:
            password: Senha em texto plano
            password_hash: Hash bcrypt armazenado
        
        Returns:
            True se a senha está correta
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Erro ao verificar senha: {e}")
            return False


# Instância global
auth_service = AuthService()