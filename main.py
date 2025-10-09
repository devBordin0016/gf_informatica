"""
Sistema de Gerenciamento de Ordem de Serviço - GF Informática
Arquivo principal de execução da aplicação

Autor: Sistema GF Informática
Data: 2025
"""

import tkinter as tk
from tkinter import messagebox
import logging
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

# Importações locais (serão criadas nas próximas etapas)
# from ui.login_window import LoginWindow
# from utils.logger import setup_logger

def main():
    """
    Função principal que inicializa a aplicação
    """
    # Configuração de logging (será implementado na etapa de utils)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Iniciando GF Informática - Sistema de OS")
    
    # Verifica se o arquivo .env existe
    if not os.path.exists('.env'):
        messagebox.showerror(
            "Erro de Configuração",
            "Arquivo .env não encontrado!\n\n"
            "Por favor, copie o arquivo .env.example para .env "
            "e configure as variáveis de ambiente."
        )
        return
    
    # Inicializa a janela principal do tkinter
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal inicialmente
    
    # Exibe janela de login (será implementada na etapa de UI)
    messagebox.showinfo(
        "GF Informática",
        "Sistema em construção!\n\n"
        "A tela de login será implementada na Etapa 6."
    )
    
    logger.info("Sistema encerrado")

if __name__ == "__main__":
    main()