"""
Serviço de Clientes
CRUD completo para gerenciamento de clientes da assistência técnica
"""

import logging
import re
from typing import Optional, List, Dict, Any
from database.connection import db

logger = logging.getLogger(__name__)


class ClienteService:
    """
    Serviço para gerenciar clientes
    Métodos: criar, buscar, listar, atualizar, deletar
    """
    
    @staticmethod
    def criar_cliente(
        nome: str,
        sobrenome: str,
        cpf: str,
        telefone: str,
        email: Optional[str] = None
    ) -> Optional[int]:
        """
        Cria um novo cliente no banco de dados
        
        Args:
            nome: Nome do cliente
            sobrenome: Sobrenome do cliente
            cpf: CPF no formato 000.000.000-00 ou 00000000000
            telefone: Telefone do cliente
            email: Email do cliente (opcional)
        
        Returns:
            ID do cliente criado ou None em caso de erro
        
        Raises:
            ValueError: Se dados inválidos
            Exception: Erro ao inserir no banco
        """
        # Validações
        if not nome or not nome.strip():
            raise ValueError("Nome é obrigatório")
        
        if not sobrenome or not sobrenome.strip():
            raise ValueError("Sobrenome é obrigatório")
        
        if not ClienteService._validar_cpf(cpf):
            raise ValueError("CPF inválido")
        
        if not telefone or not telefone.strip():
            raise ValueError("Telefone é obrigatório")
        
        # Formata o CPF
        cpf_formatado = ClienteService._formatar_cpf(cpf)
        
        # Verifica se CPF já existe
        if ClienteService.buscar_por_cpf(cpf_formatado):
            raise ValueError(f"CPF {cpf_formatado} já cadastrado")
        
        try:
            query = """
                INSERT INTO clientes (nome, sobrenome, cpf, telefone, email)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """
            
            cliente_id = db.execute_insert(
                query,
                (nome.strip(), sobrenome.strip(), cpf_formatado, telefone.strip(), email)
            )
            
            logger.info(f"Cliente criado: ID={cliente_id}, Nome={nome} {sobrenome}")
            return cliente_id
            
        except Exception as e:
            logger.error(f"Erro ao criar cliente: {e}")
            raise
    
    @staticmethod
    def buscar_por_id(cliente_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca um cliente por ID
        
        Args:
            cliente_id: ID do cliente
        
        Returns:
            Dicionário com dados do cliente ou None
        """
        try:
            query = "SELECT * FROM clientes WHERE id = %s"
            results = db.execute_query(query, (cliente_id,))
            
            if results:
                return results[0]
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por ID: {e}")
            raise
    
    @staticmethod
    def buscar_por_cpf(cpf: str) -> Optional[Dict[str, Any]]:
        """
        Busca um cliente por CPF
        
        Args:
            cpf: CPF do cliente (com ou sem formatação)
        
        Returns:
            Dicionário com dados do cliente ou None
        """
        try:
            cpf_formatado = ClienteService._formatar_cpf(cpf)
            query = "SELECT * FROM clientes WHERE cpf = %s"
            results = db.execute_query(query, (cpf_formatado,))
            
            if results:
                return results[0]
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por CPF: {e}")
            raise
    
    @staticmethod
    def listar_todos() -> List[Dict[str, Any]]:
        """
        Lista todos os clientes ordenados por nome
        
        Returns:
            Lista de dicionários com dados dos clientes
        """
        try:
            query = """
                SELECT * FROM clientes 
                ORDER BY nome, sobrenome
            """
            results = db.execute_query(query)
            return results or []
            
        except Exception as e:
            logger.error(f"Erro ao listar clientes: {e}")
            raise
    
    @staticmethod
    def buscar_por_nome(termo: str) -> List[Dict[str, Any]]:
        """
        Busca clientes por nome ou sobrenome (case-insensitive)
        
        Args:
            termo: Termo de busca
        
        Returns:
            Lista de clientes que correspondem à busca
        """
        try:
            query = """
                SELECT * FROM clientes 
                WHERE LOWER(nome) LIKE LOWER(%s) 
                   OR LOWER(sobrenome) LIKE LOWER(%s)
                ORDER BY nome, sobrenome
            """
            termo_busca = f"%{termo}%"
            results = db.execute_query(query, (termo_busca, termo_busca))
            return results or []
            
        except Exception as e:
            logger.error(f"Erro ao buscar clientes por nome: {e}")
            raise
    
    @staticmethod
    def atualizar_cliente(
        cliente_id: int,
        nome: Optional[str] = None,
        sobrenome: Optional[str] = None,
        cpf: Optional[str] = None,
        telefone: Optional[str] = None,
        email: Optional[str] = None
    ) -> bool:
        """
        Atualiza dados de um cliente existente
        Apenas os campos fornecidos serão atualizados
        
        Args:
            cliente_id: ID do cliente
            nome: Novo nome (opcional)
            sobrenome: Novo sobrenome (opcional)
            cpf: Novo CPF (opcional)
            telefone: Novo telefone (opcional)
            email: Novo email (opcional)
        
        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        # Busca cliente atual
        cliente_atual = ClienteService.buscar_por_id(cliente_id)
        if not cliente_atual:
            raise ValueError(f"Cliente ID {cliente_id} não encontrado")
        
        # Prepara os campos para atualização
        campos_atualizar = []
        valores = []
        
        if nome is not None and nome.strip():
            campos_atualizar.append("nome = %s")
            valores.append(nome.strip())
        
        if sobrenome is not None and sobrenome.strip():
            campos_atualizar.append("sobrenome = %s")
            valores.append(sobrenome.strip())
        
        if cpf is not None:
            if not ClienteService._validar_cpf(cpf):
                raise ValueError("CPF inválido")
            cpf_formatado = ClienteService._formatar_cpf(cpf)
            
            # Verifica se CPF já existe em outro cliente
            cliente_cpf = ClienteService.buscar_por_cpf(cpf_formatado)
            if cliente_cpf and cliente_cpf['id'] != cliente_id:
                raise ValueError(f"CPF {cpf_formatado} já cadastrado para outro cliente")
            
            campos_atualizar.append("cpf = %s")
            valores.append(cpf_formatado)
        
        if telefone is not None and telefone.strip():
            campos_atualizar.append("telefone = %s")
            valores.append(telefone.strip())
        
        if email is not None:
            campos_atualizar.append("email = %s")
            valores.append(email if email.strip() else None)
        
        if not campos_atualizar:
            logger.warning("Nenhum campo para atualizar")
            return False
        
        # Adiciona o ID no final dos valores
        valores.append(cliente_id)
        
        try:
            query = f"""
                UPDATE clientes 
                SET {', '.join(campos_atualizar)}
                WHERE id = %s
            """
            
            rows = db.execute_update(query, tuple(valores))
            
            if rows > 0:
                logger.info(f"Cliente ID {cliente_id} atualizado com sucesso")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erro ao atualizar cliente: {e}")
            raise
    
    @staticmethod
    def deletar_cliente(cliente_id: int) -> bool:
        """
        Deleta um cliente do banco de dados
        ATENÇÃO: Só permite deletar se não houver OS vinculadas
        
        Args:
            cliente_id: ID do cliente
        
        Returns:
            True se deletado, False caso contrário
        
        Raises:
            ValueError: Se cliente tem OS vinculadas
        """
        # Verifica se cliente existe
        cliente = ClienteService.buscar_por_id(cliente_id)
        if not cliente:
            raise ValueError(f"Cliente ID {cliente_id} não encontrado")
        
        # Verifica se tem OS vinculadas
        try:
            query_os = "SELECT COUNT(*) as total FROM ordens_servico WHERE cliente_id = %s"
            result = db.execute_query(query_os, (cliente_id,))
            
            if result and result[0]['total'] > 0:
                raise ValueError(
                    f"Não é possível deletar o cliente. "
                    f"Existem {result[0]['total']} Ordem(ns) de Serviço vinculada(s)."
                )
            
            # Deleta o cliente
            query = "DELETE FROM clientes WHERE id = %s"
            rows = db.execute_update(query, (cliente_id,))
            
            if rows > 0:
                logger.info(f"Cliente ID {cliente_id} deletado com sucesso")
                return True
            return False
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Erro ao deletar cliente: {e}")
            raise
    
    @staticmethod
    def _validar_cpf(cpf: str) -> bool:
        """
        Valida o CPF usando o algoritmo oficial
        
        Args:
            cpf: CPF a ser validado (com ou sem formatação)
        
        Returns:
            True se válido, False caso contrário
        """
        # Remove caracteres não numéricos
        cpf_numeros = re.sub(r'\D', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf_numeros) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais (ex: 111.111.111-11)
        if cpf_numeros == cpf_numeros[0] * 11:
            return False
        
        # Validação do primeiro dígito verificador
        soma = sum(int(cpf_numeros[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        if int(cpf_numeros[9]) != digito1:
            return False
        
        # Validação do segundo dígito verificador
        soma = sum(int(cpf_numeros[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        if int(cpf_numeros[10]) != digito2:
            return False
        
        return True
    
    @staticmethod
    def _formatar_cpf(cpf: str) -> str:
        """
        Formata o CPF no padrão 000.000.000-00
        
        Args:
            cpf: CPF com ou sem formatação
        
        Returns:
            CPF formatado
        """
        # Remove caracteres não numéricos
        cpf_numeros = re.sub(r'\D', '', cpf)
        
        # Formata
        return f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}"


# Instância global para facilitar o uso
cliente_service = ClienteService()