"""
Tela de Login
Interface de autenticação do usuário
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from services.auth_service import auth_service

logger = logging.getLogger(__name__)


class LoginWindow:
    """
    Janela de login do sistema
    """
    
    def __init__(self, master, on_login_success):
        """
        Inicializa a janela de login
        
        Args:
            master: Janela pai (root do tkinter)
            on_login_success: Callback chamado após login bem-sucedido
        """
        self.master = master
        self.on_login_success = on_login_success
        self.window = None
        self.usuario_autenticado = None
        
        self._criar_janela()
    
    def _criar_janela(self):
        """Cria a janela de login"""
        self.window = tk.Toplevel(self.master)
        self.window.title("GF Informática - Login")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        
        # Centraliza a janela
        self._centralizar_janela()
        
        # Impede fechar a janela com X (deve fazer logout)
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo/Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(pady=(0, 30))
        
        title_label = ttk.Label(
            title_frame,
            text="🖥️ GF INFORMÁTICA",
            font=("Arial", 20, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Sistema de Ordem de Serviço",
            font=("Arial", 10)
        )
        subtitle_label.pack()
        
        # Frame do formulário
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Usuário
        ttk.Label(form_frame, text="Usuário:").pack(anchor=tk.W, pady=(0, 5))
        self.username_entry = ttk.Entry(form_frame, width=40)
        self.username_entry.pack(pady=(0, 15))
        self.username_entry.focus()
        
        # Senha
        ttk.Label(form_frame, text="Senha:").pack(anchor=tk.W, pady=(0, 5))
        self.password_entry = ttk.Entry(form_frame, width=40, show="●")
        self.password_entry.pack(pady=(0, 20))
        
        # Botão de login
        login_button = ttk.Button(
            form_frame,
            text="Entrar",
            command=self._fazer_login,
            width=20
        )
        login_button.pack(pady=(0, 10))
        
        # Versão
        version_label = ttk.Label(
            main_frame,
            text="v1.0.0",
            font=("Arial", 8),
            foreground="gray"
        )
        version_label.pack(side=tk.BOTTOM)
        
        # Bind Enter para fazer login
        self.username_entry.bind('<Return>', lambda e: self._fazer_login())
        self.password_entry.bind('<Return>', lambda e: self._fazer_login())
    
    def _centralizar_janela(self):
        """Centraliza a janela na tela"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def _fazer_login(self):
        """Processa o login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning(
                "Campos vazios",
                "Por favor, preencha usuário e senha.",
                parent=self.window
            )
            return
        
        try:
            # Tenta autenticar
            usuario = auth_service.autenticar(username, password)
            
            if usuario:
                self.usuario_autenticado = usuario
                logger.info(f"Login bem-sucedido: {username}")
                
                # Fecha janela de login
                self.window.destroy()
                
                # Chama callback de sucesso
                self.on_login_success(usuario)
            else:
                messagebox.showerror(
                    "Erro de autenticação",
                    "Usuário ou senha incorretos.",
                    parent=self.window
                )
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus()
                
        except Exception as e:
            logger.error(f"Erro ao fazer login: {e}")
            messagebox.showerror(
                "Erro",
                f"Erro ao processar login:\n{str(e)}",
                parent=self.window
            )
    
    def _on_closing(self):
        """Trata o fechamento da janela"""
        if messagebox.askokcancel(
            "Sair",
            "Deseja sair do sistema?",
            parent=self.window
        ):
            self.master.quit()
    
    def show(self):
        """Exibe a janela de login"""
        self.window.grab_set()  # Torna modal
        self.window.wait_window()  # Aguarda fechar
        return self.usuario_autenticado