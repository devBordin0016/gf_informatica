"""
Gerador de PDF para Ordens de Serviço
Utiliza fpdf2 para criar PDFs formatados
"""

import os as os_module  # ← RENOMEADO AQUI
from datetime import datetime
from fpdf import FPDF
import logging
from services.os_service import os_service
from utils.validators import validators

logger = logging.getLogger(__name__)


class OSPDFGenerator:
    """
    Classe para gerar PDFs de Ordens de Serviço
    """
    
    def __init__(self):
        """Inicializa o gerador de PDF"""
        self.app_name = os_module.getenv('APP_NAME', 'GF Informática')  # ← ATUALIZADO
    
    def gerar_pdf_os(self, os_id: int, output_path: str = None) -> str:
        """
        Gera PDF de uma Ordem de Serviço
        
        Args:
            os_id: ID da OS
            output_path: Caminho do arquivo de saída (opcional)
        
        Returns:
            Caminho do arquivo PDF gerado
        """
        try:
            # Busca dados da OS
            ordem_servico = os_service.buscar_por_id(os_id)  # ← RENOMEADO
            
            if not ordem_servico:
                raise ValueError(f"OS ID {os_id} não encontrada")
            
            # Cria nova instância do PDF para cada geração
            pdf = FPDF()
            pdf.add_page()
            
            # Configura fonte padrão
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Gera conteúdo
            self._adicionar_cabecalho(pdf, ordem_servico)
            self._adicionar_dados_cliente(pdf, ordem_servico)
            self._adicionar_configuracao_hardware(pdf, ordem_servico)
            self._adicionar_defeito_relatado(pdf, ordem_servico)
            self._adicionar_informacoes_adicionais(pdf, ordem_servico)
            self._adicionar_rodape(pdf, ordem_servico)
            
            # Define nome do arquivo se não informado
            if not output_path:
                output_path = f"OS_{ordem_servico['numero_os']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Salva PDF
            pdf.output(output_path)
            
            logger.info(f"PDF gerado: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {e}")
            raise
    
    def _adicionar_cabecalho(self, pdf, ordem_servico):
        """Adiciona cabeçalho com logo e informações da empresa"""
        # Nome da empresa
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 10, self.app_name, 0, 1, 'C')
        
        # Subtítulo
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 5, 'Sistema de Gerenciamento de Ordem de Servico', 0, 1, 'C')
        
        # Linha separadora
        pdf.ln(5)
        pdf.set_draw_color(0, 0, 0)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)
        
        # Título da OS
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f'ORDEM DE SERVICO - {ordem_servico["numero_os"]}', 0, 1, 'C')
        pdf.ln(5)
        
        # Informações da OS (caixa)
        y_start = pdf.get_y()
        
        pdf.set_fill_color(240, 240, 240)
        pdf.rect(10, y_start, 190, 25, 'F')
        
        pdf.set_font('Arial', '', 10)
        
        # Primeira linha
        pdf.set_xy(15, y_start + 5)
        pdf.cell(60, 5, f'Data de Abertura: {ordem_servico["criado_em"].strftime("%d/%m/%Y %H:%M")}')
        
        pdf.set_xy(100, y_start + 5)
        pdf.cell(60, 5, f'Status: {ordem_servico["status"].replace("_", " ").title()}')
        
        # Segunda linha
        pdf.set_xy(15, y_start + 12)
        pdf.cell(60, 5, f'Responsavel: {ordem_servico["usuario_nome"]}')
        
        if ordem_servico['valor_estimado']:
            pdf.set_xy(100, y_start + 12)
            pdf.cell(60, 5, f'Valor Estimado: {validators.formatar_valor(ordem_servico["valor_estimado"])}')
        
        # Terceira linha
        if ordem_servico['prazo_previsto']:
            pdf.set_xy(15, y_start + 19)
            pdf.cell(60, 5, f'Prazo Previsto: {ordem_servico["prazo_previsto"].strftime("%d/%m/%Y")}')
        
        if ordem_servico['concluido_em']:
            pdf.set_xy(100, y_start + 19)
            pdf.cell(60, 5, f'Concluido em: {ordem_servico["concluido_em"].strftime("%d/%m/%Y %H:%M")}')
        
        pdf.set_y(y_start + 30)
    
    def _adicionar_dados_cliente(self, pdf, ordem_servico):
        """Adiciona dados do cliente"""
        pdf.ln(5)
        
        # Título da seção
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(200, 200, 200)
        pdf.cell(0, 8, 'DADOS DO CLIENTE', 0, 1, 'L', True)
        pdf.ln(2)
        
        # Conteúdo
        pdf.set_font('Arial', '', 10)
        
        pdf.cell(40, 6, 'Nome Completo:', 0, 0, 'L')
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, f'{ordem_servico["cliente_nome"]} {ordem_servico["cliente_sobrenome"]}', 0, 1, 'L')
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(40, 6, 'CPF:', 0, 0, 'L')
        pdf.cell(60, 6, ordem_servico['cliente_cpf'], 0, 0, 'L')
        pdf.cell(20, 6, 'Telefone:', 0, 0, 'L')
        pdf.cell(0, 6, ordem_servico['cliente_telefone'], 0, 1, 'L')
        
        if ordem_servico['cliente_email']:
            pdf.cell(40, 6, 'Email:', 0, 0, 'L')
            pdf.cell(0, 6, ordem_servico['cliente_email'], 0, 1, 'L')
    
    def _adicionar_configuracao_hardware(self, pdf, ordem_servico):
        """Adiciona configuração do hardware"""
        # Verifica se tem alguma informação de hardware
        tem_hardware = any([
            ordem_servico['processador'],
            ordem_servico['placa_mae'],
            ordem_servico['memoria_ram'],
            ordem_servico['armazenamento'],
            ordem_servico['placa_video'],
            ordem_servico['outros_componentes']
        ])
        
        if not tem_hardware:
            return
        
        pdf.ln(5)
        
        # Título da seção
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(200, 200, 200)
        pdf.cell(0, 8, 'CONFIGURACAO DO HARDWARE', 0, 1, 'L', True)
        pdf.ln(2)
        
        # Conteúdo
        pdf.set_font('Arial', '', 10)
        
        if ordem_servico['processador']:
            pdf.cell(0, 6, f"Processador: {ordem_servico['processador']}", 0, 1, 'L')
        
        if ordem_servico['placa_mae']:
            pdf.cell(0, 6, f"Placa-mae: {ordem_servico['placa_mae']}", 0, 1, 'L')
        
        if ordem_servico['memoria_ram']:
            pdf.cell(0, 6, f"Memoria RAM: {ordem_servico['memoria_ram']}", 0, 1, 'L')
        
        if ordem_servico['armazenamento']:
            pdf.cell(0, 6, f"Armazenamento: {ordem_servico['armazenamento']}", 0, 1, 'L')
        
        if ordem_servico['placa_video']:
            pdf.cell(0, 6, f"Placa de Video: {ordem_servico['placa_video']}", 0, 1, 'L')
        
        if ordem_servico['outros_componentes']:
            # Usa multi_cell apenas aqui, começando em nova linha
            pdf.cell(0, 6, "Outros Componentes:", 0, 1, 'L')
            pdf.multi_cell(0, 6, ordem_servico['outros_componentes'])

    def _adicionar_defeito_relatado(self, pdf, ordem_servico):
        """Adiciona defeito relatado pelo cliente"""
        pdf.ln(5)
        
        # Título da seção
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(200, 200, 200)
        pdf.cell(0, 8, 'DEFEITO RELATADO PELO CLIENTE', 0, 1, 'L', True)
        pdf.ln(2)
        
        # Conteúdo
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 6, ordem_servico['defeito_relatado'])
    
    def _adicionar_informacoes_adicionais(self, pdf, ordem_servico):
        """Adiciona observações técnicas se houver"""
        if not ordem_servico['observacoes']:
            return
        
        pdf.ln(5)
        
        # Título da seção
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(200, 200, 200)
        pdf.cell(0, 8, 'OBSERVACOES TECNICAS', 0, 1, 'L', True)
        pdf.ln(2)
        
        # Conteúdo
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 6, ordem_servico['observacoes'])
    
    def _adicionar_rodape(self, pdf, ordem_servico):
        """Adiciona rodapé com assinaturas"""
        # Posiciona no final da página
        pdf.ln(15)
        
        # Linha separadora
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)
        
        # Campos de assinatura
        y_pos = pdf.get_y()
        
        # Assinatura do cliente
        pdf.set_xy(20, y_pos)
        pdf.cell(70, 6, '_' * 35, 0, 0, 'C')
        
        # Assinatura do técnico
        pdf.set_xy(110, y_pos)
        pdf.cell(70, 6, '_' * 35, 0, 0, 'C')
        
        # Legendas
        pdf.set_xy(20, y_pos + 8)
        pdf.set_font('Arial', '', 9)
        pdf.cell(70, 5, 'Assinatura do Cliente', 0, 0, 'C')
        
        pdf.set_xy(110, y_pos + 8)
        pdf.cell(70, 5, 'Assinatura do Tecnico', 0, 0, 'C')
        
        # Data de emissão
        pdf.ln(15)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 5, f'Documento gerado em: {datetime.now().strftime("%d/%m/%Y as %H:%M")}', 0, 1, 'C')
        
        # Informação do sistema
        pdf.set_font('Arial', 'I', 7)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 5, f'{self.app_name} - Sistema de Ordem de Servico v1.0.0', 0, 1, 'C')


# Instância global
pdf_generator = OSPDFGenerator()