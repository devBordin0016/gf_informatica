"""
Janela Principal
Menu e navegação do sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from ui.cliente_window import ClienteWindow
from ui.os_window import OSWindow

logger = logging.getLogger(__name__)


class MainWindow:
    """
    Janela principal do sistema com menu e área de trabalho
    """
    
    def __init__(self, master, usuario):
        """
        Inicializa a janela principal
        
        Args:
            master: Janela root do tkinter
            usuario: Dicionário com dados do usuário autenticado
        """
        self.master = master
        self.usuario = usuario
        
        # Configura a janela principal
        self.master.title(f"GF Informática - {usuario['nome_completo']}")
        self.master.geometry("1200x700")
        
        # Centraliza a janela
        self._centralizar_janela()
        
        # Cria a interface
        self._criar_menu()
        self._criar_interface()
        
        # Exibe tela de boas-vindas
        self._mostrar_boas_vindas()
        
        logger.info(f"Janela principal aberta para usuário: {usuario['username']}")
    
    def _centralizar_janela(self):
        """Centraliza a janela na tela"""
        self.master.update_idletasks()
        width = 1200
        height = 700
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'{width}x{height}+{x}+{y}')
    
    def _criar_menu(self):
        """Cria a barra de menu"""
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        
        # Menu Cadastros
        cadastros_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Cadastros", menu=cadastros_menu)
        cadastros_menu.add_command(
            label="Clientes",
            command=self._abrir_clientes,
            accelerator="Ctrl+C"
        )
        cadastros_menu.add_separator()
        cadastros_menu.add_command(
            label="Sair",
            command=self._sair,
            accelerator="Ctrl+Q"
        )
        
        # Menu Ordem de Serviço
        os_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ordem de Serviço", menu=os_menu)
        os_menu.add_command(
            label="Nova OS",
            command=self._nova_os,
            accelerator="Ctrl+N"
        )
        os_menu.add_command(
            label="Consultar OS",
            command=self._consultar_os,
            accelerator="Ctrl+F"
        )
        
        # Menu Ajuda
        ajuda_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=ajuda_menu)
        ajuda_menu.add_command(label="Sobre", command=self._sobre)
        
        # Atalhos de teclado
        self.master.bind('<Control-c>', lambda e: self._abrir_clientes())
        self.master.bind('<Control-n>', lambda e: self._nova_os())
        self.master.bind('<Control-f>', lambda e: self._consultar_os())
        self.master.bind('<Control-q>', lambda e: self._sair())
    
    def _criar_interface(self):
        """Cria a interface principal"""
        # Frame superior (toolbar)
        toolbar = ttk.Frame(self.master)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Botões da toolbar
        ttk.Button(
            toolbar,
            text="📋 Clientes",
            command=self._abrir_clientes,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar,
            text="➕ Nova OS",
            command=self._nova_os,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar,
            text="🔍 Consultar OS",
            command=self._consultar_os,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Informações do usuário (direita)
        user_frame = ttk.Frame(toolbar)
        user_frame.pack(side=tk.RIGHT)
        
        ttk.Label(
            user_frame,
            text=f"👤 {self.usuario['nome_completo']}",
            font=("Arial", 9)
        ).pack(side=tk.RIGHT, padx=10)
        
        # Separador
        ttk.Separator(self.master, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10)
        
        # Área de trabalho (centro)
        self.work_area = ttk.Frame(self.master)
        self.work_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barra de status (rodapé)
        self.status_bar = ttk.Label(
            self.master,
            text="Pronto",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _mostrar_boas_vindas(self):
        """Mostra tela de boas-vindas"""
        # Limpa área de trabalho
        for widget in self.work_area.winfo_children():
            widget.destroy()
        
        # Frame centralizado
        welcome_frame = ttk.Frame(self.work_area)
        welcome_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Logo/Título
        ttk.Label(
            welcome_frame,
            text="🖥️ GF INFORMÁTICA",
            font=("Arial", 28, "bold")
        ).pack(pady=20)
        
        ttk.Label(
            welcome_frame,
            text="Sistema de Gerenciamento de Ordem de Serviço",
            font=("Arial", 12)
        ).pack(pady=10)
        
        ttk.Label(
            welcome_frame,
            text=f"Bem-vindo(a), {self.usuario['nome_completo']}!",
            font=("Arial", 14)
        ).pack(pady=20)
        
        # Botões de ação rápida
        button_frame = ttk.Frame(welcome_frame)
        button_frame.pack(pady=30)
        
        ttk.Button(
            button_frame,
            text="📋 Gerenciar Clientes",
            command=self._abrir_clientes,
            width=25
        ).pack(pady=5)
        
        ttk.Button(
            button_frame,
            text="➕ Nova Ordem de Serviço",
            command=self._nova_os,
            width=25
        ).pack(pady=5)
        
        ttk.Button(
            button_frame,
            text="🔍 Consultar OS",
            command=self._consultar_os,
            width=25
        ).pack(pady=5)
    
    def _abrir_clientes(self):
        """Abre janela de gerenciamento de clientes"""
        ClienteWindow(self.master)
        self.status_bar.config(text="Gerenciamento de Clientes aberto")
    
    def _nova_os(self):
        """Abre janela para criar nova OS"""
        OSWindow(self.master, self.usuario, modo='criar')
        self.status_bar.config(text="Nova OS aberta")
    
    def _consultar_os(self):
        """Abre janela de consulta de OS"""
        OSWindow(self.master, self.usuario, modo='consultar')
        self.status_bar.config(text="Consulta de OS aberta")
    
    def _sobre(self):
        """Exibe informações sobre o sistema"""
        messagebox.showinfo(
            "Sobre",
            "GF INFORMÁTICA\n"
            "Sistema de Gerenciamento de Ordem de Serviço\n\n"
            "Versão: 1.0.0\n"
            "Desenvolvido em Python com tkinter\n\n"
            "© 2025 GF Informática"
        )
    
    def _sair(self):
        """Sai do sistema"""
        if messagebox.askokcancel("Sair", "Deseja realmente sair do sistema?"):
            logger.info(f"Usuário {self.usuario['username']} saiu do sistema")
            self.master.quit()