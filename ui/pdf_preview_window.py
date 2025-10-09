"""
Janela de Preview de PDF
Exibe preview do PDF e permite salvar ou imprimir
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os as os_module
import tempfile
import logging
from utils.pdf_generator import pdf_generator
from services.os_service import os_service

logger = logging.getLogger(__name__)


class PDFPreviewWindow:
    """
    Janela para visualizar e gerenciar PDFs de OS
    """
    
    def __init__(self, master, os_id):
        """
        Inicializa a janela de preview
        
        Args:
            master: Janela pai
            os_id: ID da OS
        """
        self.master = master
        self.os_id = os_id
        self.pdf_path = None
        self.os_data = None
        
        # Cria janela primeiro
        self.window = tk.Toplevel(master)
        self.window.title("Preview - Ordem de Serviço")
        self.window.geometry("600x400")
        self.window.transient(master)
        
        # Tenta gerar PDF
        if not self._gerar_pdf_temp():
            # Se falhou, fecha a janela
            self.window.destroy()
            return
        
        # Cria interface
        self._criar_interface()
        
        logger.info(f"Janela de preview aberta para OS ID {os_id}")
    
    def _gerar_pdf_temp(self):
        """
        Gera PDF temporário
        
        Returns:
            bool: True se sucesso, False se falhou
        """
        try:
            # Busca dados da OS
            ordem_servico = os_service.buscar_por_id(self.os_id)
            
            if not ordem_servico:
                raise ValueError(f"OS ID {self.os_id} não encontrada")
            
            # Armazena dados da OS
            self.os_data = ordem_servico
            
            # Cria arquivo temporário
            temp_dir = tempfile.gettempdir()
            self.pdf_path = os_module.path.join(temp_dir, f"OS_{ordem_servico['numero_os']}_temp.pdf")
            
            # Gera PDF
            pdf_generator.gerar_pdf_os(self.os_id, self.pdf_path)
            
            logger.info(f"PDF temporário gerado: {self.pdf_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {e}")
            messagebox.showerror(
                "Erro ao gerar PDF",
                f"Não foi possível gerar o PDF:\n\n{str(e)}"
            )
            return False
    
    def _criar_interface(self):
        """Cria a interface da janela"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Ícone e título
        icon_frame = ttk.Frame(main_frame)
        icon_frame.pack(pady=(0, 20))
        
        ttk.Label(
            icon_frame,
            text="📄",
            font=("Arial", 48)
        ).pack()
        
        # Informações
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 30))
        
        ttk.Label(
            info_frame,
            text=f"Ordem de Serviço: {self.os_data['numero_os']}",
            font=("Arial", 14, "bold")
        ).pack()
        
        ttk.Label(
            info_frame,
            text=f"Cliente: {self.os_data['cliente_nome']} {self.os_data['cliente_sobrenome']}",
            font=("Arial", 11)
        ).pack(pady=5)
        
        ttk.Label(
            info_frame,
            text=f"Data: {self.os_data['criado_em'].strftime('%d/%m/%Y')}",
            font=("Arial", 10),
            foreground="gray"
        ).pack()
        
        # Separador
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        # Informações sobre o PDF
        ttk.Label(
            main_frame,
            text="PDF gerado com sucesso!",
            font=("Arial", 11),
            foreground="green"
        ).pack(pady=10)
        
        ttk.Label(
            main_frame,
            text="Escolha uma opção abaixo:",
            font=("Arial", 10)
        ).pack(pady=5)
        
        # Botões principais
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=30)
        
        # Botão Salvar
        btn_salvar = ttk.Button(
            button_frame,
            text="💾 Salvar PDF",
            command=self._salvar_pdf,
            width=20
        )
        btn_salvar.pack(side=tk.LEFT, padx=10)
        
        # Botão Imprimir
        btn_imprimir = ttk.Button(
            button_frame,
            text="🖨️ Imprimir",
            command=self._imprimir_pdf,
            width=20
        )
        btn_imprimir.pack(side=tk.LEFT, padx=10)
        
        # Botão Fechar
        ttk.Button(
            main_frame,
            text="Fechar",
            command=self._fechar,
            width=15
        ).pack(pady=20)
        
        # Informação adicional
        ttk.Label(
            main_frame,
            text="💡 Dica: Você também pode abrir o PDF com um leitor externo após salvar",
            font=("Arial", 8),
            foreground="blue"
        ).pack(side=tk.BOTTOM, pady=10)
    
    def _salvar_pdf(self):
        """Salva o PDF em local escolhido pelo usuário"""
        try:
            # Nome padrão do arquivo
            nome_padrao = f"OS_{self.os_data['numero_os']}_{self.os_data['criado_em'].strftime('%Y%m%d')}.pdf"
            
            # Diálogo para escolher local
            arquivo_destino = filedialog.asksaveasfilename(
                parent=self.window,
                title="Salvar PDF",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=nome_padrao
            )
            
            if not arquivo_destino:
                return  # Usuário cancelou
            
            # Copia o arquivo temporário para o destino
            import shutil
            shutil.copy2(self.pdf_path, arquivo_destino)
            
            logger.info(f"PDF salvo em: {arquivo_destino}")
            
            # Pergunta se quer abrir o arquivo
            abrir = messagebox.askyesno(
                "PDF Salvo com Sucesso! ✅",
                f"PDF salvo em:\n{arquivo_destino}\n\n"
                "Deseja abrir o arquivo agora?",
                parent=self.window
            )
            
            if abrir:
                self._abrir_arquivo(arquivo_destino)
        
        except Exception as e:
            logger.error(f"Erro ao salvar PDF: {e}")
            messagebox.showerror(
                "Erro",
                f"Erro ao salvar PDF:\n{str(e)}",
                parent=self.window
            )
    
    def _imprimir_pdf(self):
        """Envia o PDF para impressão"""
        try:
            import platform
            sistema = platform.system()
            
            if sistema == "Windows":
                # Windows: usa o comando padrão de impressão
                os_module.startfile(self.pdf_path, "print")
                messagebox.showinfo(
                    "Imprimindo",
                    "PDF enviado para impressão!\n\n"
                    "Verifique a fila de impressão do sistema.",
                    parent=self.window
                )
                
            elif sistema == "Darwin":  # macOS
                # macOS: abre o Preview para impressão
                import subprocess
                subprocess.run(["open", "-a", "Preview", self.pdf_path])
                messagebox.showinfo(
                    "Imprimindo",
                    "PDF aberto no Preview.\n\n"
                    "Use Cmd+P para imprimir.",
                    parent=self.window
                )
                
            elif sistema == "Linux":
                # Linux: tenta usar lpr ou abre com o leitor padrão
                import subprocess
                try:
                    subprocess.run(["lpr", self.pdf_path], check=True)
                    messagebox.showinfo(
                        "Imprimindo",
                        "PDF enviado para impressão!",
                        parent=self.window
                    )
                except:
                    # Se lpr não funcionar, abre com xdg-open
                    subprocess.run(["xdg-open", self.pdf_path])
                    messagebox.showinfo(
                        "PDF Aberto",
                        "PDF aberto no leitor padrão.\n\n"
                        "Use a opção de impressão do aplicativo.",
                        parent=self.window
                    )
            else:
                # Sistema desconhecido
                messagebox.showwarning(
                    "Sistema não suportado",
                    "Impressão direta não disponível neste sistema.\n\n"
                    "Salve o PDF e imprima manualmente.",
                    parent=self.window
                )
            
            logger.info("PDF enviado para impressão")
            
        except Exception as e:
            logger.error(f"Erro ao imprimir PDF: {e}")
            messagebox.showerror(
                "Erro ao Imprimir",
                f"Não foi possível imprimir o PDF.\n\n"
                f"Erro: {str(e)}\n\n"
                "Salve o PDF e imprima manualmente.",
                parent=self.window
            )
    
    def _abrir_arquivo(self, caminho):
        """Abre arquivo com aplicativo padrão do sistema"""
        try:
            import platform
            sistema = platform.system()
            
            if sistema == "Windows":
                os_module.startfile(caminho)
            elif sistema == "Darwin":  # macOS
                import subprocess
                subprocess.run(["open", caminho])
            else:  # Linux
                import subprocess
                subprocess.run(["xdg-open", caminho])
                
        except Exception as e:
            logger.error(f"Erro ao abrir arquivo: {e}")
            messagebox.showerror(
                "Erro",
                f"Não foi possível abrir o arquivo:\n{str(e)}",
                parent=self.window
            )
    
    def _fechar(self):
        """Fecha a janela e limpa arquivos temporários"""
        try:
            # Remove arquivo temporário
            if self.pdf_path and os_module.path.exists(self.pdf_path):
                os_module.remove(self.pdf_path)
                logger.info(f"Arquivo temporário removido: {self.pdf_path}")
        except Exception as e:
            logger.warning(f"Erro ao remover arquivo temporário: {e}")
        
        self.window.destroy()