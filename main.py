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

# Importações locais
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from utils.logger import setup_logger

def main():
    """
    Função principal que inicializa a aplicação
    """
    # Configuração de logging
    logger = setup_logger('gf_informatica')
    logger.info("=" * 60)
    logger.info("Iniciando GF Informática - Sistema de OS")
    logger.info("=" * 60)
    
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
    
    # Exibe janela de login
    login_window = LoginWindow(root, on_login_success=lambda usuario: abrir_sistema(root, usuario))
    usuario = login_window.show()
    
    if usuario:
        # Login bem-sucedido - já abriu o sistema
        root.mainloop()
    else:
        logger.info("Login cancelado pelo usuário")

def abrir_sistema(root, usuario):
    """
    Abre o sistema após login bem-sucedido
    
    Args:
        root: Janela root do tkinter
        usuario: Dados do usuário autenticado
    """
    # Mostra a janela principal
    root.deiconify()
    
    # Cria janela principal do sistema
    MainWindow(root, usuario)

if __name__ == "__main__":
    main()