"""
Janela de Gerenciamento de Clientes
CRUD completo de clientes com interface gráfica
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from services.cliente_service import cliente_service
from utils.validators import validators

logger = logging.getLogger(__name__)


class ClienteWindow:
    """
    Janela para gerenciar clientes (criar, editar, buscar, deletar)
    """
    
    def __init__(self, master):
        """
        Inicializa a janela de clientes
        
        Args:
            master: Janela pai
        """
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.title("GF Informática - Gerenciamento de Clientes")
        self.window.geometry("1000x600")
        
        # Variáveis
        self.cliente_selecionado = None
        self.modo_edicao = False
        
        self._criar_interface()
        self._carregar_clientes()
        
        logger.info("Janela de clientes aberta")
    
    def _criar_interface(self):
        """Cria a interface da janela"""
        # Frame principal dividido em duas partes
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Painel esquerdo - Formulário
        left_panel = ttk.LabelFrame(main_frame, text="Dados do Cliente", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        self._criar_formulario(left_panel)
        
        # Painel direito - Lista de clientes
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self._criar_lista_clientes(right_panel)
    
    def _criar_formulario(self, parent):
        """Cria o formulário de cadastro/edição"""
        # Nome
        ttk.Label(parent, text="Nome:*").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.nome_entry = ttk.Entry(parent, width=30)
        self.nome_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Sobrenome
        ttk.Label(parent, text="Sobrenome:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sobrenome_entry = ttk.Entry(parent, width=30)
        self.sobrenome_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # CPF
        ttk.Label(parent, text="CPF:*").grid(row=2, column=0, sticky=tk.W, pady=5)
        cpf_frame = ttk.Frame(parent)
        cpf_frame.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.cpf_entry = ttk.Entry(cpf_frame, width=20)
        self.cpf_entry.pack(side=tk.LEFT)
        
        ttk.Label(cpf_frame, text="(000.000.000-00)", foreground="gray", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        
        # Bind para formatar CPF automaticamente
        self.cpf_entry.bind('<FocusOut>', self._formatar_cpf_campo)
        
        # Telefone
        ttk.Label(parent, text="Telefone:*").grid(row=3, column=0, sticky=tk.W, pady=5)
        telefone_frame = ttk.Frame(parent)
        telefone_frame.grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.telefone_entry = ttk.Entry(telefone_frame, width=20)
        self.telefone_entry.pack(side=tk.LEFT)
        
        ttk.Label(telefone_frame, text="(00) 00000-0000", foreground="gray", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        
        # Bind para formatar telefone
        self.telefone_entry.bind('<FocusOut>', self._formatar_telefone_campo)
        
        # Email
        ttk.Label(parent, text="Email:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(parent, width=30)
        self.email_entry.grid(row=4, column=1, pady=5, padx=5)
        
        # Campos obrigatórios
        ttk.Label(parent, text="* Campos obrigatórios", foreground="red", font=("Arial", 8)).grid(row=5, column=0, columnspan=2, pady=10)
        
        # Botões
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        self.btn_salvar = ttk.Button(
            button_frame,
            text="💾 Salvar",
            command=self._salvar_cliente,
            width=15
        )
        self.btn_salvar.pack(side=tk.LEFT, padx=5)
        
        self.btn_cancelar = ttk.Button(
            button_frame,
            text="❌ Cancelar",
            command=self._cancelar_edicao,
            width=15,
            state=tk.DISABLED
        )
        self.btn_cancelar.pack(side=tk.LEFT, padx=5)
        
        self.btn_limpar = ttk.Button(
            button_frame,
            text="🗑️ Limpar",
            command=self._limpar_formulario,
            width=15
        )
        self.btn_limpar.pack(side=tk.LEFT, padx=5)
    
    def _criar_lista_clientes(self, parent):
        """Cria a lista/tabela de clientes"""
        # Frame de busca
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self._buscar_clientes)
        
        ttk.Button(
            search_frame,
            text="🔄 Atualizar",
            command=self._carregar_clientes,
            width=12
        ).pack(side=tk.RIGHT, padx=5)
        
        # Frame da tabela com scrollbar
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        # Treeview (tabela)
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Nome", "CPF", "Telefone", "Email"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configuração das colunas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome Completo")
        self.tree.heading("CPF", text="CPF")
        self.tree.heading("Telefone", text="Telefone")
        self.tree.heading("Email", text="Email")
        
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Nome", width=200)
        self.tree.column("CPF", width=130, anchor=tk.CENTER)
        self.tree.column("Telefone", width=130, anchor=tk.CENTER)
        self.tree.column("Email", width=200)
        
        # Posicionamento
        self.tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.E, tk.W))
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind duplo clique para editar
        self.tree.bind('<Double-Button-1>', self._editar_cliente)
        
        # Menu de contexto (botão direito)
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="✏️ Editar", command=self._editar_cliente)
        self.context_menu.add_command(label="🗑️ Deletar", command=self._deletar_cliente)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📄 Ver OS do Cliente", command=self._ver_os_cliente)
        
        self.tree.bind('<Button-3>', self._mostrar_context_menu)
    
    def _formatar_cpf_campo(self, event=None):
        """Formata o CPF no campo automaticamente"""
        cpf = self.cpf_entry.get()
        if cpf:
            cpf_formatado = validators.formatar_cpf(cpf)
            self.cpf_entry.delete(0, tk.END)
            self.cpf_entry.insert(0, cpf_formatado)
    
    def _formatar_telefone_campo(self, event=None):
        """Formata o telefone no campo automaticamente"""
        telefone = self.telefone_entry.get()
        if telefone:
            telefone_formatado = validators.formatar_telefone(telefone)
            self.telefone_entry.delete(0, tk.END)
            self.telefone_entry.insert(0, telefone_formatado)
    
    def _carregar_clientes(self):
        """Carrega todos os clientes na tabela"""
        try:
            # Limpa tabela
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Busca clientes
            clientes = cliente_service.listar_todos()
            
            # Preenche tabela
            for cliente in clientes:
                nome_completo = f"{cliente['nome']} {cliente['sobrenome']}"
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        cliente['id'],
                        nome_completo,
                        cliente['cpf'],
                        cliente['telefone'],
                        cliente['email'] or ""
                    )
                )
            
            logger.info(f"{len(clientes)} clientes carregados")
            
        except Exception as e:
            logger.error(f"Erro ao carregar clientes: {e}")
            messagebox.showerror(
                "Erro",
                f"Erro ao carregar clientes:\n{str(e)}",
                parent=self.window
            )
    
    def _buscar_clientes(self, event=None):
        """Busca clientes por nome"""
        termo = self.search_entry.get().strip()
        
        if not termo:
            self._carregar_clientes()
            return
        
        try:
            # Limpa tabela
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Busca clientes
            clientes = cliente_service.buscar_por_nome(termo)
            
            # Preenche tabela
            for cliente in clientes:
                nome_completo = f"{cliente['nome']} {cliente['sobrenome']}"
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        cliente['id'],
                        nome_completo,
                        cliente['cpf'],
                        cliente['telefone'],
                        cliente['email'] or ""
                    )
                )
            
            logger.info(f"{len(clientes)} clientes encontrados para '{termo}'")
            
        except Exception as e:
            logger.error(f"Erro ao buscar clientes: {e}")
    
    def _salvar_cliente(self):
        """Salva ou atualiza cliente"""
        # Validações
        nome = self.nome_entry.get().strip()
        sobrenome = self.sobrenome_entry.get().strip()
        cpf = self.cpf_entry.get().strip()
        telefone = self.telefone_entry.get().strip()
        email = self.email_entry.get().strip()
        
        if not nome:
            messagebox.showwarning("Campo obrigatório", "Nome é obrigatório!", parent=self.window)
            self.nome_entry.focus()
            return
        
        if not sobrenome:
            messagebox.showwarning("Campo obrigatório", "Sobrenome é obrigatório!", parent=self.window)
            self.sobrenome_entry.focus()
            return
        
        if not cpf:
            messagebox.showwarning("Campo obrigatório", "CPF é obrigatório!", parent=self.window)
            self.cpf_entry.focus()
            return
        
        if not validators.validar_cpf(cpf):
            messagebox.showerror("CPF inválido", "O CPF informado não é válido!", parent=self.window)
            self.cpf_entry.focus()
            return
        
        if not telefone:
            messagebox.showwarning("Campo obrigatório", "Telefone é obrigatório!", parent=self.window)
            self.telefone_entry.focus()
            return
        
        if email and not validators.validar_email(email):
            messagebox.showerror("Email inválido", "O email informado não é válido!", parent=self.window)
            self.email_entry.focus()
            return
        
        try:
            if self.modo_edicao:
                # Atualizar cliente existente
                sucesso = cliente_service.atualizar_cliente(
                    self.cliente_selecionado,
                    nome=nome,
                    sobrenome=sobrenome,
                    cpf=cpf,
                    telefone=telefone,
                    email=email if email else None
                )
                
                if sucesso:
                    messagebox.showinfo(
                        "Sucesso",
                        "Cliente atualizado com sucesso!",
                        parent=self.window
                    )
                    logger.info(f"Cliente ID {self.cliente_selecionado} atualizado")
                else:
                    messagebox.showerror(
                        "Erro",
                        "Falha ao atualizar cliente!",
                        parent=self.window
                    )
            else:
                # Criar novo cliente
                cliente_id = cliente_service.criar_cliente(
                    nome=nome,
                    sobrenome=sobrenome,
                    cpf=cpf,
                    telefone=telefone,
                    email=email if email else None
                )
                
                messagebox.showinfo(
                    "Sucesso",
                    f"Cliente cadastrado com sucesso!\nID: {cliente_id}",
                    parent=self.window
                )
                logger.info(f"Novo cliente cadastrado: ID {cliente_id}")
            
            # Limpa formulário e recarrega lista
            self._limpar_formulario()
            self._carregar_clientes()
            
        except ValueError as e:
            messagebox.showerror("Erro de validação", str(e), parent=self.window)
        except Exception as e:
            logger.error(f"Erro ao salvar cliente: {e}")
            messagebox.showerror(
                "Erro",
                f"Erro ao salvar cliente:\n{str(e)}",
                parent=self.window
            )
    
    def _editar_cliente(self, event=None):
        """Carrega dados do cliente selecionado para edição"""
        selection = self.tree.selection()
        
        if not selection:
            messagebox.showwarning(
                "Nenhum cliente selecionado",
                "Selecione um cliente na lista para editar!",
                parent=self.window
            )
            return
        
        # Pega dados da linha selecionada
        item = self.tree.item(selection[0])
        cliente_id = item['values'][0]
        
        try:
            # Busca cliente completo no banco
            cliente = cliente_service.buscar_por_id(cliente_id)
            
            if not cliente:
                messagebox.showerror("Erro", "Cliente não encontrado!", parent=self.window)
                return
            
            # Preenche formulário
            self.nome_entry.delete(0, tk.END)
            self.nome_entry.insert(0, cliente['nome'])
            
            self.sobrenome_entry.delete(0, tk.END)
            self.sobrenome_entry.insert(0, cliente['sobrenome'])
            
            self.cpf_entry.delete(0, tk.END)
            self.cpf_entry.insert(0, cliente['cpf'])
            
            self.telefone_entry.delete(0, tk.END)
            self.telefone_entry.insert(0, cliente['telefone'])
            
            self.email_entry.delete(0, tk.END)
            if cliente['email']:
                self.email_entry.insert(0, cliente['email'])
            
            # Ativa modo edição
            self.modo_edicao = True
            self.cliente_selecionado = cliente_id
            self.btn_cancelar.config(state=tk.NORMAL)
            self.btn_salvar.config(text="💾 Atualizar")
            
            logger.info(f"Cliente ID {cliente_id} carregado para edição")
            
        except Exception as e:
            logger.error(f"Erro ao carregar cliente para edição: {e}")
            messagebox.showerror(
                "Erro",
                f"Erro ao carregar cliente:\n{str(e)}",
                parent=self.window
            )
    
    def _deletar_cliente(self):
        """Deleta o cliente selecionado"""
        selection = self.tree.selection()
        
        if not selection:
            messagebox.showwarning(
                "Nenhum cliente selecionado",
                "Selecione um cliente na lista para deletar!",
                parent=self.window
            )
            return
        
        # Pega dados da linha selecionada
        item = self.tree.item(selection[0])
        cliente_id = item['values'][0]
        nome_completo = item['values'][1]
        
        # Confirmação
        confirmacao = messagebox.askyesno(
            "Confirmar exclusão",
            f"Tem certeza que deseja deletar o cliente:\n\n{nome_completo}\n\n"
            "Esta ação não pode ser desfeita!",
            parent=self.window
        )
        
        if not confirmacao:
            return
        
        try:
            cliente_service.deletar_cliente(cliente_id)
            
            messagebox.showinfo(
                "Sucesso",
                "Cliente deletado com sucesso!",
                parent=self.window
            )
            
            logger.info(f"Cliente ID {cliente_id} deletado")
            
            # Recarrega lista
            self._carregar_clientes()
            
        except ValueError as e:
            # Cliente tem OS vinculadas
            messagebox.showerror(
                "Não é possível deletar",
                str(e),
                parent=self.window
            )
        except Exception as e:
            logger.error(f"Erro ao deletar cliente: {e}")
            messagebox.showerror(
                "Erro",
                f"Erro ao deletar cliente:\n{str(e)}",
                parent=self.window
            )
    
    def _ver_os_cliente(self):
        """Abre lista de OS do cliente selecionado"""
        selection = self.tree.selection()
        
        if not selection:
            messagebox.showwarning(
                "Nenhum cliente selecionado",
                "Selecione um cliente na lista!",
                parent=self.window
            )
            return
        
        item = self.tree.item(selection[0])
        cliente_id = item['values'][0]
        nome_completo = item['values'][1]
        
        try:
            from services.os_service import os_service
            
            os_list = os_service.listar_por_cliente(cliente_id)
            
            if not os_list:
                messagebox.showinfo(
                    "Sem OS",
                    f"O cliente {nome_completo} não possui Ordens de Serviço cadastradas.",
                    parent=self.window
                )
                return
            
            # Cria janela para exibir as OS
            os_window = tk.Toplevel(self.window)
            os_window.title(f"Ordens de Serviço - {nome_completo}")
            os_window.geometry("800x400")
            
            # Tabela de OS
            frame = ttk.Frame(os_window, padding="10")
            frame.pack(fill=tk.BOTH, expand=True)
            
            tree = ttk.Treeview(
                frame,
                columns=("Número", "Data", "Defeito", "Status", "Valor"),
                show="headings"
            )
            
            tree.heading("Número", text="Número OS")
            tree.heading("Data", text="Data")
            tree.heading("Defeito", text="Defeito Relatado")
            tree.heading("Status", text="Status")
            tree.heading("Valor", text="Valor Estimado")
            
            tree.column("Número", width=100, anchor=tk.CENTER)
            tree.column("Data", width=100, anchor=tk.CENTER)
            tree.column("Defeito", width=300)
            tree.column("Status", width=120, anchor=tk.CENTER)
            tree.column("Valor", width=120, anchor=tk.E)
            
            for os in os_list:
                defeito_resumo = os['defeito_relatado'][:50] + "..." if len(os['defeito_relatado']) > 50 else os['defeito_relatado']
                valor = validators.formatar_valor(os['valor_estimado'])
                data = os['criado_em'].strftime('%d/%m/%Y') if os['criado_em'] else ""
                
                tree.insert(
                    "",
                    tk.END,
                    values=(
                        os['numero_os'],
                        data,
                        defeito_resumo,
                        os['status'],
                        valor
                    )
                )
            
            tree.pack(fill=tk.BOTH, expand=True)
            
            # Scrollbar
            vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
            vsb.pack(side=tk.RIGHT, fill=tk.Y)
            tree.config(yscrollcommand=vsb.set)
            
        except Exception as e:
            logger.error(f"Erro ao buscar OS do cliente: {e}")
            messagebox.showerror(
                "Erro",
                f"Erro ao buscar OS:\n{str(e)}",
                parent=self.window
            )
    
    def _cancelar_edicao(self):
        """Cancela a edição atual"""
        self._limpar_formulario()
    
    def _limpar_formulario(self):
        """Limpa todos os campos do formulário"""
        self.nome_entry.delete(0, tk.END)
        self.sobrenome_entry.delete(0, tk.END)
        self.cpf_entry.delete(0, tk.END)
        self.telefone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        
        self.modo_edicao = False
        self.cliente_selecionado = None
        self.btn_cancelar.config(state=tk.DISABLED)
        self.btn_salvar.config(text="💾 Salvar")
        
        self.nome_entry.focus()
    
    def _mostrar_context_menu(self, event):
        """Mostra menu de contexto ao clicar com botão direito"""
        # Seleciona o item sob o cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)