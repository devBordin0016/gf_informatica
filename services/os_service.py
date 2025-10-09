"""
Serviço de Ordens de Serviço
CRUD completo para gerenciamento de OS
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from database.connection import db

logger = logging.getLogger(__name__)


class OSService:
    """
    Serviço para gerenciar Ordens de Serviço
    Métodos: criar, buscar, listar, atualizar status, etc.
    """
    
    # Status válidos
    STATUS_ABERTA = 'aberta'
    STATUS_EM_ANDAMENTO = 'em_andamento'
    STATUS_CONCLUIDA = 'concluida'
    STATUS_CANCELADA = 'cancelada'
    
    STATUS_VALIDOS = [STATUS_ABERTA, STATUS_EM_ANDAMENTO, STATUS_CONCLUIDA, STATUS_CANCELADA]
    
    @staticmethod
    def criar_os(
        cliente_id: int,
        usuario_id: int,
        defeito_relatado: str,
        processador: Optional[str] = None,
        placa_mae: Optional[str] = None,
        memoria_ram: Optional[str] = None,
        armazenamento: Optional[str] = None,
        placa_video: Optional[str] = None,
        outros_componentes: Optional[str] = None,
        valor_estimado: Optional[float] = None,
        prazo_previsto: Optional[date] = None,
        observacoes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Cria uma nova Ordem de Serviço
        O número da OS é gerado automaticamente pelo banco (OS0001, OS0002...)
        
        Args:
            cliente_id: ID do cliente
            usuario_id: ID do usuário que está criando a OS
            defeito_relatado: Descrição do problema relatado
            processador: Processador do equipamento
            placa_mae: Placa-mãe do equipamento
            memoria_ram: Memória RAM do equipamento
            armazenamento: Armazenamento do equipamento
            placa_video: Placa de vídeo do equipamento
            outros_componentes: Outros componentes
            valor_estimado: Valor estimado do serviço
            prazo_previsto: Data prevista para conclusão
            observacoes: Observações técnicas
        
        Returns:
            Dicionário com os dados da OS criada (incluindo numero_os)
        
        Raises:
            ValueError: Se dados inválidos
        """
        # Validações
        if not defeito_relatado or not defeito_relatado.strip():
            raise ValueError("Descrição do defeito é obrigatória")
        
        # Verifica se cliente existe
        from services.cliente_service import ClienteService
        if not ClienteService.buscar_por_id(cliente_id):
            raise ValueError(f"Cliente ID {cliente_id} não encontrado")
        
        try:
            query = """
                INSERT INTO ordens_servico (
                    cliente_id, usuario_id, defeito_relatado,
                    processador, placa_mae, memoria_ram, armazenamento,
                    placa_video, outros_componentes,
                    valor_estimado, prazo_previsto, observacoes,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, numero_os, criado_em
            """
            
            result = db.execute_query(
                query,
                (
                    cliente_id, usuario_id, defeito_relatado.strip(),
                    processador, placa_mae, memoria_ram, armazenamento,
                    placa_video, outros_componentes,
                    valor_estimado, prazo_previsto, observacoes,
                    OSService.STATUS_ABERTA
                ),
                fetch=True
            )
            
            if result:
                os_criada = result[0]
                logger.info(
                    f"OS criada: {os_criada['numero_os']} "
                    f"(ID={os_criada['id']}, Cliente={cliente_id})"
                )
                
                # Busca a OS completa para retornar
                return OSService.buscar_por_id(os_criada['id'])
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao criar OS: {e}")
            raise
    
    @staticmethod
    def buscar_por_id(os_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca uma OS por ID com informações completas do cliente
        
        Args:
            os_id: ID da OS
        
        Returns:
            Dicionário com dados completos da OS
        """
        try:
            query = """
                SELECT 
                    os.*,
                    c.nome as cliente_nome,
                    c.sobrenome as cliente_sobrenome,
                    c.cpf as cliente_cpf,
                    c.telefone as cliente_telefone,
                    c.email as cliente_email,
                    u.nome_completo as usuario_nome
                FROM ordens_servico os
                INNER JOIN clientes c ON os.cliente_id = c.id
                INNER JOIN usuarios u ON os.usuario_id = u.id
                WHERE os.id = %s
            """
            
            results = db.execute_query(query, (os_id,))
            
            if results:
                return results[0]
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar OS por ID: {e}")
            raise
    
    @staticmethod
    def buscar_por_numero(numero_os: str) -> Optional[Dict[str, Any]]:
        """
        Busca uma OS pelo número (ex: OS0001)
        
        Args:
            numero_os: Número da OS
        
        Returns:
            Dicionário com dados completos da OS
        """
        try:
            query = """
                SELECT 
                    os.*,
                    c.nome as cliente_nome,
                    c.sobrenome as cliente_sobrenome,
                    c.cpf as cliente_cpf,
                    c.telefone as cliente_telefone,
                    c.email as cliente_email,
                    u.nome_completo as usuario_nome
                FROM ordens_servico os
                INNER JOIN clientes c ON os.cliente_id = c.id
                INNER JOIN usuarios u ON os.usuario_id = u.id
                WHERE os.numero_os = %s
            """
            
            results = db.execute_query(query, (numero_os.upper(),))
            
            if results:
                return results[0]
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar OS por número: {e}")
            raise
    
    @staticmethod
    def listar_todas(
        status: Optional[str] = None,
        limite: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Lista todas as OS com opção de filtrar por status
        
        Args:
            status: Filtrar por status (opcional)
            limite: Número máximo de resultados
        
        Returns:
            Lista de OS ordenadas por data (mais recentes primeiro)
        """
        try:
            if status and status not in OSService.STATUS_VALIDOS:
                raise ValueError(f"Status inválido: {status}")
            
            if status:
                query = """
                    SELECT 
                        os.*,
                        c.nome as cliente_nome,
                        c.sobrenome as cliente_sobrenome,
                        c.telefone as cliente_telefone,
                        u.nome_completo as usuario_nome
                    FROM ordens_servico os
                    INNER JOIN clientes c ON os.cliente_id = c.id
                    INNER JOIN usuarios u ON os.usuario_id = u.id
                    WHERE os.status = %s
                    ORDER BY os.criado_em DESC
                    LIMIT %s
                """
                results = db.execute_query(query, (status, limite))
            else:
                query = """
                    SELECT 
                        os.*,
                        c.nome as cliente_nome,
                        c.sobrenome as cliente_sobrenome,
                        c.telefone as cliente_telefone,
                        u.nome_completo as usuario_nome
                    FROM ordens_servico os
                    INNER JOIN clientes c ON os.cliente_id = c.id
                    INNER JOIN usuarios u ON os.usuario_id = u.id
                    ORDER BY os.criado_em DESC
                    LIMIT %s
                """
                results = db.execute_query(query, (limite,))
            
            return results or []
            
        except Exception as e:
            logger.error(f"Erro ao listar OS: {e}")
            raise
    
    @staticmethod
    def listar_por_cliente(cliente_id: int) -> List[Dict[str, Any]]:
        """
        Lista todas as OS de um cliente específico
        
        Args:
            cliente_id: ID do cliente
        
        Returns:
            Lista de OS do cliente
        """
        try:
            query = """
                SELECT 
                    os.*,
                    u.nome_completo as usuario_nome
                FROM ordens_servico os
                INNER JOIN usuarios u ON os.usuario_id = u.id
                WHERE os.cliente_id = %s
                ORDER BY os.criado_em DESC
            """
            
            results = db.execute_query(query, (cliente_id,))
            return results or []
            
        except Exception as e:
            logger.error(f"Erro ao listar OS por cliente: {e}")
            raise
    
    @staticmethod
    def atualizar_status(
        os_id: int,
        novo_status: str,
        observacoes_atualizacao: Optional[str] = None
    ) -> bool:
        """
        Atualiza o status de uma OS
        
        Args:
            os_id: ID da OS
            novo_status: Novo status da OS
            observacoes_atualizacao: Observações sobre a atualização
        
        Returns:
            True se atualizado com sucesso
        """
        if novo_status not in OSService.STATUS_VALIDOS:
            raise ValueError(f"Status inválido: {novo_status}")
        
        try:
            # Se está concluindo, atualiza a data de conclusão
            if novo_status == OSService.STATUS_CONCLUIDA:
                query = """
                    UPDATE ordens_servico 
                    SET status = %s, concluido_em = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
            else:
                query = """
                    UPDATE ordens_servico 
                    SET status = %s, concluido_em = NULL
                    WHERE id = %s
                """
            
            rows = db.execute_update(query, (novo_status, os_id))
            
            # Se houver observações, adiciona
            if observacoes_atualizacao:
                OSService.adicionar_observacao(os_id, observacoes_atualizacao)
            
            if rows > 0:
                logger.info(f"OS ID {os_id} status atualizado para: {novo_status}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status da OS: {e}")
            raise
    
    @staticmethod
    def adicionar_observacao(os_id: int, nova_observacao: str) -> bool:
        """
        Adiciona uma nova observação à OS (append)
        
        Args:
            os_id: ID da OS
            nova_observacao: Texto da observação
        
        Returns:
            True se adicionado com sucesso
        """
        try:
            # Busca observações atuais
            os_atual = OSService.buscar_por_id(os_id)
            if not os_atual:
                raise ValueError(f"OS ID {os_id} não encontrada")
            
            observacoes_atuais = os_atual.get('observacoes', '') or ''
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            # Adiciona nova observação com timestamp
            if observacoes_atuais.strip():
                observacoes_novas = (
                    f"{observacoes_atuais}\n\n"
                    f"[{timestamp}] {nova_observacao}"
                )
            else:
                observacoes_novas = f"[{timestamp}] {nova_observacao}"
            
            query = "UPDATE ordens_servico SET observacoes = %s WHERE id = %s"
            rows = db.execute_update(query, (observacoes_novas, os_id))
            
            return rows > 0
            
        except Exception as e:
            logger.error(f"Erro ao adicionar observação: {e}")
            raise
    
    @staticmethod
    def atualizar_os(
        os_id: int,
        defeito_relatado: Optional[str] = None,
        processador: Optional[str] = None,
        placa_mae: Optional[str] = None,
        memoria_ram: Optional[str] = None,
        armazenamento: Optional[str] = None,
        placa_video: Optional[str] = None,
        outros_componentes: Optional[str] = None,
        valor_estimado: Optional[float] = None,
        prazo_previsto: Optional[date] = None,
        observacoes: Optional[str] = None
    ) -> bool:
        """
        Atualiza informações de uma OS existente
        
        Args:
            os_id: ID da OS
            [outros campos opcionais]
        
        Returns:
            True se atualizado com sucesso
        """
        # Busca OS atual
        os_atual = OSService.buscar_por_id(os_id)
        if not os_atual:
            raise ValueError(f"OS ID {os_id} não encontrada")
        
        # Prepara campos para atualização
        campos_atualizar = []
        valores = []
        
        if defeito_relatado is not None:
            campos_atualizar.append("defeito_relatado = %s")
            valores.append(defeito_relatado)
        
        if processador is not None:
            campos_atualizar.append("processador = %s")
            valores.append(processador)
        
        if placa_mae is not None:
            campos_atualizar.append("placa_mae = %s")
            valores.append(placa_mae)
        
        if memoria_ram is not None:
            campos_atualizar.append("memoria_ram = %s")
            valores.append(memoria_ram)
        
        if armazenamento is not None:
            campos_atualizar.append("armazenamento = %s")
            valores.append(armazenamento)
        
        if placa_video is not None:
            campos_atualizar.append("placa_video = %s")
            valores.append(placa_video)
        
        if outros_componentes is not None:
            campos_atualizar.append("outros_componentes = %s")
            valores.append(outros_componentes)
        
        if valor_estimado is not None:
            campos_atualizar.append("valor_estimado = %s")
            valores.append(valor_estimado)
        
        if prazo_previsto is not None:
            campos_atualizar.append("prazo_previsto = %s")
            valores.append(prazo_previsto)
        
        if observacoes is not None:
            campos_atualizar.append("observacoes = %s")
            valores.append(observacoes)
        
        if not campos_atualizar:
            logger.warning("Nenhum campo para atualizar")
            return False
        
        # Adiciona o ID no final
        valores.append(os_id)
        
        try:
            query = f"""
                UPDATE ordens_servico 
                SET {', '.join(campos_atualizar)}
                WHERE id = %s
            """
            
            rows = db.execute_update(query, tuple(valores))
            
            if rows > 0:
                logger.info(f"OS ID {os_id} atualizada com sucesso")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erro ao atualizar OS: {e}")
            raise
    
    @staticmethod
    def obter_estatisticas() -> Dict[str, Any]:
        """
        Retorna estatísticas gerais das OS
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            query = """
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'aberta' THEN 1 END) as abertas,
                    COUNT(CASE WHEN status = 'em_andamento' THEN 1 END) as em_andamento,
                    COUNT(CASE WHEN status = 'concluida' THEN 1 END) as concluidas,
                    COUNT(CASE WHEN status = 'cancelada' THEN 1 END) as canceladas
                FROM ordens_servico
            """
            
            results = db.execute_query(query)
            return results[0] if results else {}
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            raise


# Instância global
os_service = OSService()