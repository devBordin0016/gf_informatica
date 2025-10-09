"""
Janela de Gerenciamento de Ordens de Serviço
Criação e consulta de OS
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime, timedelta
import logging
from services.os_service import os_service
from services.cliente_service import cliente_service
from utils.validators import validators

logger = logging.getLogger(__name__)


class OSWindow:
    """
    Janela para criar e consultar Ordens de Serviço
    """
    
    def __init__(self, master, usuario, modo='criar', os_id=None):
        """
        Inicializa a janela de OS
        
        Args:
            master: Janela pai
            usuario: Dicionário com dados do usuário autenticado
            modo: 'criar' ou 'consultar'
            os_id: ID da OS (para modo edição)
        """
        self.master = master
        self.usuario = usuario
        self.modo = modo
        self.os_id = os_id
        
        self.window = tk.Toplevel(master)
        
        if modo == 'criar':
            self.window.title("GF Informática - Nova Ordem de Serviço")
            self.window.geometry("900x700")
            self._criar_interface_nova_os()
        else:
            self.window.title("GF Informática - Consultar Ordens de Serviço")
            self.window.geometry("1100x650")
            self._criar_interface_consulta()
        
        logger.info(f"Janela de OS aberta em modo: {modo}")
    
    # ========================================================================
    # INTERFACE - NOVA OS
    # ========================================================================
    
    def _criar_interface_nova_os(self):
        """Cria interface para criar nova OS"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook (abas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba 1: Cliente
        self.aba_cliente = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.aba_cliente, text="1. Cliente")
        self._criar_aba_cliente()
        
        # Aba 2: Hardware
        self.aba_hardware = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.aba_hardware, text="2. Hardware")
        self._criar_aba_hardware()
        
        # Aba 3: Defeito e Informações
        self.aba_defeito = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.aba_defeito, text="3. Defeito e Informações")
        self._criar_aba_defeito()
        
        # Frame de botões no rodapé
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="⬅️ Anterior",
            command=self._aba_anterior,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="➡️ Próxima",
            command=self._proxima_aba,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="✅ Gerar OS",
            command=self._gerar_os,
            width=15
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="❌ Cancelar",
            command=self.window.destroy,
            width=15
        ).pack(side=tk.RIGHT, padx=5)
    
    def _criar_aba_cliente(self):
        """Cria aba de seleção/cadastro de cliente"""
        # Frame de busca
        search_frame = ttk.LabelFrame(self.aba_cliente, text="Buscar Cliente Existente", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(search_frame, text="Buscar por Nome ou CPF:").pack(anchor=tk.W, pady=5)
        
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill=tk.X, pady=5)
        
        self.cliente_search_entry = ttk.Entry(search_input_frame, width=40)
        self.cliente_search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            search_input_frame,
            text="🔍 Buscar",
            command=self._buscar_cliente,
            width=12
        ).pack(side=tk.LEFT)
        
        # Lista de clientes encontrados
        self.cliente_listbox = tk.Listbox(search_frame, height=5)
        self.cliente_listbox.pack(fill=tk.X, pady=5)
        self.cliente_listbox.bind('<<ListboxSelect>>', self._selecionar_cliente_lista)
        
        # Separador
        ttk.Separator(self.aba_cliente, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        # Frame de dados do cliente selecionado/novo
        dados_frame = ttk.LabelFrame(self.aba_cliente, text="Dados do Cliente", padding="10")
        dados_frame.pack(fill=tk.BOTH, expand=True)
        
        # ID do cliente (hidden)
        self.cliente_id_var = tk.IntVar(value=0)
        
        # Nome
        ttk.Label(dados_frame, text="Nome:*").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cliente_nome_entry = ttk.Entry(dados_frame, width=40)
        self.cliente_nome_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Sobrenome
        ttk.Label(dados_frame, text="Sobrenome:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.cliente_sobrenome_entry = ttk.Entry(dados_frame, width=40)
        self.cliente_sobrenome_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        # CPF
        ttk.Label(dados_frame, text="CPF:*").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.cliente_cpf_entry = ttk.Entry(dados_frame, width=25)
        self.cliente_cpf_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Telefone
        ttk.Label(dados_frame, text="Telefone:*").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.cliente_telefone_entry = ttk.Entry(dados_frame, width=25)
        self.cliente_telefone_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Email
        ttk.Label(dados_frame, text="Email:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.cliente_email_entry = ttk.Entry(dados_frame, width=40)
        self.cliente_email_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(
            dados_frame,
            text="* Se o cliente não existir, será cadastrado automaticamente",
            foreground="blue",
            font=("Arial", 9)
        ).grid(row=5, column=0, columnspan=2, pady=10)
    
    def _criar_aba_hardware(self):
        """Cria aba de configuração de hardware"""
        # Processador
        ttk.Label(self.aba_hardware, text="Processador:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.processador_entry = ttk.Entry(self.aba_hardware, width=50)
        self.processador_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(self.aba_hardware, text="Ex: Intel Core i5-10400", foreground="gray", font=("Arial", 8)).grid(row=0, column=2, sticky=tk.W)
        
        # Placa-mãe
        ttk.Label(self.aba_hardware, text="Placa-mãe:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.placa_mae_entry = ttk.Entry(self.aba_hardware, width=50)
        self.placa_mae_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(self.aba_hardware, text="Ex: ASUS Prime H410M-E", foreground="gray", font=("Arial", 8)).grid(row=1, column=2, sticky=tk.W)
        
        # Memória RAM
        ttk.Label(self.aba_hardware, text="Memória RAM:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.memoria_ram_entry = ttk.Entry(self.aba_hardware, width=50)
        self.memoria_ram_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(self.aba_hardware, text="Ex: 16GB DDR4 2666MHz", foreground="gray", font=("Arial", 8)).grid(row=2, column=2, sticky=tk.W)
        
        # Armazenamento
        ttk.Label(self.aba_hardware, text="Armazenamento:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.armazenamento_entry = ttk.Entry(self.aba_hardware, width=50)
        self.armazenamento_entry.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(self.aba_hardware, text="Ex: SSD 480GB + HD 1TB", foreground="gray", font=("Arial", 8)).grid(row=3, column=2, sticky=tk.W)
        
        # Placa de vídeo
        ttk.Label(self.aba_hardware, text="Placa de Vídeo:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.placa_video_entry = ttk.Entry(self.aba_hardware, width=50)
        self.placa_video_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(self.aba_hardware, text="Ex: NVIDIA GTX 1650 4GB", foreground="gray", font=("Arial", 8)).grid(row=4, column=2, sticky=tk.W)
        
        # Outros componentes
        ttk.Label(self.aba_hardware, text="Outros Componentes:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.outros_componentes_text = tk.Text(self.aba_hardware, width=50, height=5)
        self.outros_componentes_text.grid(row=5, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(
            self.aba_hardware,
            text="Ex: Fonte 500W, Gabinete...",
            foreground="gray",
            font=("Arial", 8)
        ).grid(row=5, column=2, sticky=tk.NW)
        
        ttk.Label(
            self.aba_hardware,
            text="💡 Dica: Preencha o máximo de informações possível para facilitar o diagnóstico",
            foreground="blue",
            font=("Arial", 9)
        ).grid(row=6, column=0, columnspan=3, pady=20)
    
    def _criar_aba_defeito(self):
        """Cria aba de defeito relatado e informações adicionais"""
        # Defeito relatado
        ttk.Label(self.aba_defeito, text="Defeito Relatado pelo Cliente:*", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        defeito_frame = ttk.Frame(self.aba_defeito)
        defeito_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.defeito_text = tk.Text(defeito_frame, width=80, height=8, wrap=tk.WORD)
        self.defeito_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        defeito_scroll = ttk.Scrollbar(defeito_frame, orient=tk.VERTICAL, command=self.defeito_text.yview)
        defeito_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.defeito_text.config(yscrollcommand=defeito_scroll.set)
        
        ttk.Label(
            self.aba_defeito,
            text="Descreva detalhadamente o problema relatado pelo cliente",
            foreground="gray",
            font=("Arial", 8)
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Frame de informações adicionais
        info_frame = ttk.LabelFrame(self.aba_defeito, text="Informações Adicionais", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Valor estimado
        valor_frame = ttk.Frame(info_frame)
        valor_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(valor_frame, text="Valor Estimado (R$):").pack(side=tk.LEFT, padx=(0, 10))
        self.valor_estimado_entry = ttk.Entry(valor_frame, width=15)
        self.valor_estimado_entry.pack(side=tk.LEFT)
        ttk.Label(valor_frame, text="Ex: 150.00 ou 150,50", foreground="gray", font=("Arial", 8)).pack(side=tk.LEFT, padx=10)
        
        # Prazo previsto
        prazo_frame = ttk.Frame(info_frame)
        prazo_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(prazo_frame, text="Prazo Previsto:").pack(side=tk.LEFT, padx=(0, 10))
        self.prazo_dias_spinbox = ttk.Spinbox(prazo_frame, from_=1, to=365, width=10)
        self.prazo_dias_spinbox.pack(side=tk.LEFT)
        self.prazo_dias_spinbox.set(7)  # Padrão 7 dias
        ttk.Label(prazo_frame, text="dias a partir de hoje", foreground="gray", font=("Arial", 8)).pack(side=tk.LEFT, padx=10)
        
        # Data calculada
        self.prazo_data_label = ttk.Label(prazo_frame, text="", foreground="blue", font=("Arial", 9, "bold"))
        self.prazo_data_label.pack(side=tk.LEFT, padx=10)
        
        # Bind para atualizar data ao mudar dias
        self.prazo_dias_spinbox.bind('<KeyRelease>', self._atualizar_prazo_data)
        self.prazo_dias_spinbox.bind('<<Increment>>', self._atualizar_prazo_data)
        self.prazo_dias_spinbox.bind('<<Decrement>>', self._atualizar_prazo_data)
        
        # Atualiza data inicialmente
        self._atualizar_prazo_data()
        
        # Observações
        ttk.Label(self.aba_defeito, text="Observações Técnicas:", font=("Arial", 10)).pack(anchor=tk.W, pady=(10, 5))
        
        obs_frame = ttk.Frame(self.aba_defeito)
        obs_frame.pack(fill=tk.BOTH, expand=True)
        
        self.observacoes_text = tk.Text(obs_frame, width=80, height=5, wrap=tk.WORD)
        self.observacoes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        obs_scroll = ttk.Scrollbar(obs_frame, orient=tk.VERTICAL, command=self.observacoes_text.yview)
        obs_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.observacoes_text.config(yscrollcommand=obs_scroll.set)
    
    def _atualizar_prazo_data(self, event=None):
        """Atualiza a data do prazo baseado nos dias"""
        try:
            dias = int(self.prazo_dias_spinbox.get())
            data_prevista = date.today() + timedelta(days=dias)
            self.prazo_data_label.config(text=f"→ {data_prevista.strftime('%d/%m/%Y')}")
        except:
            self.prazo_data_label.config(text="")
    
    def _buscar_cliente(self):
        """Busca clientes por nome ou CPF"""
        termo = self.cliente_search_entry.get().strip()
        
        if not termo:
            messagebox.showwarning(
                "Campo vazio",
                "Digite um nome ou CPF para buscar!",
                parent=self.window
            )
            return
        
        try:
            # Limpa listbox
            self.cliente_listbox.delete(0, tk.END)
            
            # Busca por nome
            clientes = cliente_service.buscar_por_nome(termo)
            
            # Se não encontrou por nome, tenta por CPF
            if not clientes:
                cliente_cpf = cliente_service.buscar_por_cpf(termo)
                if cliente_cpf:
                    clientes = [cliente_cpf]
            
            if not clientes:
                messagebox.showinfo(
                    "Nenhum cliente encontrado",
                    f"Nenhum cliente encontrado com: {termo}\n\n"
                    "Você pode cadastrar um novo cliente preenchendo os dados abaixo.",
                    parent=self.window
                )
                return
            
            # Preenche listbox
            for cliente in clientes:
                texto = f"ID: {cliente['id']} | {cliente['nome']} {cliente['sobrenome']} | CPF: {cliente['cpf']}"
                self.cliente_listbox.insert(tk.END, texto)
                # Armazena o objeto completo como atributo do item
                self.cliente_listbox.itemconfig(tk.END, selectbackground='lightblue')
            
            # Armazena os clientes encontrados
            self.clientes_encontrados = clientes
            
            logger.info(f"{len(clientes)} cliente(s) encontrado(s) para '{termo}'")
            
        except Exception as e:
            logger.error(f"Erro ao buscar cliente: {e}")
            messagebox.showerror(
                "Erro",
                f"Erro ao buscar cliente:\n{str(e)}",
                parent=self.window
            )
    
    def _selecionar_cliente_lista(self, event):
        """Preenche os campos com o cliente selecionado"""
        selection = self.cliente_listbox.curselection()
        
        if not selection:
            return
        
        index = selection[0]
        cliente = self.clientes_encontrados[index]
        
        # Preenche os campos
        self.cliente_id_var.set(cliente['id'])
        
        self.cliente_nome_entry.delete(0, tk.END)
        self.cliente_nome_entry.insert(0, cliente['nome'])
        
        self.cliente_sobrenome_entry.delete(0, tk.END)
        self.cliente_sobrenome_entry.insert(0, cliente['sobrenome'])
        
        self.cliente_cpf_entry.delete(0, tk.END)
        self.cliente_cpf_entry.insert(0, cliente['cpf'])
        
        self.cliente_telefone_entry.delete(0, tk.END)
        self.cliente_telefone_entry.insert(0, cliente['telefone'])
        
        self.cliente_email_entry.delete(0, tk.END)
        if cliente['email']:
            self.cliente_email_entry.insert(0, cliente['email'])
        
        # Desabilita edição de CPF (cliente já existe)
        self.cliente_cpf_entry.config(state='readonly')
        
        messagebox.showinfo(
            "Cliente selecionado",
            f"Cliente {cliente['nome']} {cliente['sobrenome']} selecionado!\n\n"
            "Prossiga para a próxima aba.",
            parent=self.window
        )
    
    def _proxima_aba(self):
        """Avança para a próxima aba"""
        current = self.notebook.index(self.notebook.select())
        
        if current < self.notebook.index("end") - 1:
            self.notebook.select(current + 1)
    
    def _aba_anterior(self):
        """Volta para a aba anterior"""
        current = self.notebook.index(self.notebook.select())
        
        if current > 0:
            self.notebook.select(current - 1)
    
    def _gerar_os(self):
        """Gera a Ordem de Serviço"""
        # Validação básica de cliente
        nome = self.cliente_nome_entry.get().strip()
        sobrenome = self.cliente_sobrenome_entry.get().strip()
        cpf = self.cliente_cpf_entry.get().strip()
        telefone = self.cliente_telefone_entry.get().strip()
        email = self.cliente_email_entry.get().strip()
        
        if not nome or not sobrenome or not cpf or not telefone:
            messagebox.showerror(
                "Dados incompletos",
                "Por favor, preencha todos os dados obrigatórios do cliente!\n\n"
                "Campos obrigatórios: Nome, Sobrenome, CPF e Telefone",
                parent=self.window
            )
            self.notebook.select(0)  # Volta para aba do cliente
            return
        
        # Validação do defeito
        defeito = self.defeito_text.get("1.0", tk.END).strip()
        
        if not defeito:
            messagebox.showerror(
                "Defeito não informado",
                "Por favor, descreva o defeito relatado pelo cliente!",
                parent=self.window
            )
            self.notebook.select(2)  # Vai para aba de defeito
            return
        
        # Confirmação
        confirmacao = messagebox.askyesno(
            "Confirmar geração de OS",
            "Deseja gerar a Ordem de Serviço?\n\n"
            f"Cliente: {nome} {sobrenome}\n"
            f"CPF: {cpf}\n\n"
            "Esta ação criará a OS no sistema.",
            parent=self.window
        )
        
        if not confirmacao:
            return
        
        try:
            # Verifica se cliente existe ou cria novo
            cliente_id = self.cliente_id_var.get()
            
            if cliente_id == 0:
                # Cliente novo - validações
                if not validators.validar_cpf(cpf):
                    messagebox.showerror(
                        "CPF inválido",
                        "O CPF informado não é válido!",
                        parent=self.window
                    )
                    return
                
                if email and not validators.validar_email(email):
                    messagebox.showerror(
                        "Email inválido",
                        "O email informado não é válido!",
                        parent=self.window
                    )
                    return
                
                # Cria o cliente
                cliente_id = cliente_service.criar_cliente(
                    nome=nome,
                    sobrenome=sobrenome,
                    cpf=cpf,
                    telefone=telefone,
                    email=email if email else None
                )
                
                logger.info(f"Novo cliente criado durante OS: ID {cliente_id}")
            
            # Coleta dados do hardware
            processador = self.processador_entry.get().strip() or None
            placa_mae = self.placa_mae_entry.get().strip() or None
            memoria_ram = self.memoria_ram_entry.get().strip() or None
            armazenamento = self.armazenamento_entry.get().strip() or None
            placa_video = self.placa_video_entry.get().strip() or None
            outros_componentes = self.outros_componentes_text.get("1.0", tk.END).strip() or None
            
            # Coleta informações adicionais
            valor_str = self.valor_estimado_entry.get().strip()
            valor_estimado = validators.validar_valor(valor_str) if valor_str else None
            
            dias = int(self.prazo_dias_spinbox.get())
            prazo_previsto = date.today() + timedelta(days=dias)
            
            observacoes = self.observacoes_text.get("1.0", tk.END).strip() or None
            
            # Cria a OS
            os_criada = os_service.criar_os(
                cliente_id=cliente_id,
                usuario_id=self.usuario['id'],
                defeito_relatado=defeito,
                processador=processador,
                placa_mae=placa_mae,
                memoria_ram=memoria_ram,
                armazenamento=armazenamento,
                placa_video=placa_video,
                outros_componentes=outros_componentes,
                valor_estimado=valor_estimado,
                prazo_previsto=prazo_previsto,
                observacoes=observacoes
            )
            
            if os_criada:
                # Sucesso!
                numero_os = os_criada['numero_os']
                
                resultado = messagebox.askyesno(
                    "OS Criada com Sucesso! ✅",
                    f"Ordem de Serviço criada com sucesso!\n\n"
                    f"Número da OS: {numero_os}\n"
                    f"Cliente: {nome} {sobrenome}\n"
                    f"Data: {date.today().strftime('%d/%m/%Y')}\n\n"
                    "Deseja gerar o PDF da OS agora?",
                    parent=self.window
                )
                
                logger.info(f"OS {numero_os} criada com sucesso")
                
                if resultado:
                    # Gera PDF
                    self._gerar_pdf_os(os_criada['id'])
                
                # Fecha a janela
                self.window.destroy()
            else:
                messagebox.showerror(
                    "Erro",
                    "Falha ao criar a Ordem de Serviço!",
                    parent=self.window
                )
        
        except ValueError as e:
            messagebox.showerror("Erro de validação", str(e), parent=self.window)
        except Exception as e:
            logger.error(f"Erro ao gerar OS: {e}")
            messagebox.showerror(
                "Erro",
                f"Erro ao gerar OS:\n{str(e)}",
                parent=self.window
            )
    
    # ========================================================================
    # INTERFACE - CONSULTA DE OS
    # ========================================================================
    
    def _criar_interface_consulta(self):
        """Cria interface para consultar OS"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de filtros
        filter_frame = ttk.LabelFrame(main_frame, text="Filtros", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Busca por número
        ttk.Label(filter_frame, text="Número da OS:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.filtro_numero_entry = ttk.Entry(filter_frame, width=15)
        self.filtro_numero_entry.grid(row=0, column=1, padx=5)
        
        # Filtro por status
        ttk.Label(filter_frame, text="Status:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.filtro_status_combo = ttk.Combobox(
            filter_frame,
            values=["Todos", "Aberta", "Em Andamento", "Concluída", "Cancelada"],
            state="readonly",
            width=15
        )
        self.filtro_status_combo.set("Todos")
        self.filtro_status_combo.grid(row=0, column=3, padx=5)
        
        # Botões
        ttk.Button(
            filter_frame,
            text="🔍 Buscar",
            command=self._buscar_os,
            width=12
        ).grid(row=0, column=4, padx=5)
        
        ttk.Button(
            filter_frame,
            text="🔄 Limpar",
            command=self._limpar_filtros,
            width=12
        ).grid(row=0, column=5, padx=5)
        
        # Tabela de OS
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        self.os_tree = ttk.Treeview(
            table_frame,
            columns=("Número", "Data", "Cliente", "Defeito", "Status", "Valor", "Prazo"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.os_tree.yview)
        hsb.config(command=self.os_tree.xview)
        
        # Configuração das colunas
        self.os_tree.heading("Número", text="Número OS")
        self.os_tree.heading("Data", text="Data")
        self.os_tree.heading("Cliente", text="Cliente")
        self.os_tree.heading("Defeito", text="Defeito Relatado")
        self.os_tree.heading("Status", text="Status")
        self.os_tree.heading("Valor", text="Valor Est.")
        self.os_tree.heading("Prazo", text="Prazo")
        
        self.os_tree.column("Número", width=100, anchor=tk.CENTER)
        self.os_tree.column("Data", width=100, anchor=tk.CENTER)
        self.os_tree.column("Cliente", width=200)
        self.os_tree.column("Defeito", width=300)
        self.os_tree.column("Status", width=120, anchor=tk.CENTER)
        self.os_tree.column("Valor", width=100, anchor=tk.E)
        self.os_tree.column("Prazo", width=100, anchor=tk.CENTER)
        
        # Posicionamento
        self.os_tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.E, tk.W))
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Bind duplo clique para visualizar detalhes
        self.os_tree.bind('<Double-Button-1>', self._visualizar_os_detalhes)
        
        # Menu de contexto
        self.os_context_menu = tk.Menu(self.os_tree, tearoff=0)
        self.os_context_menu.add_command(label="👁️ Visualizar Detalhes", command=self._visualizar_os_detalhes)
        self.os_context_menu.add_command(label="📄 Gerar PDF", command=self._gerar_pdf_os_selecionada)
        self.os_context_menu.add_separator()
        self.os_context_menu.add_command(label="🔄 Atualizar Status", command=self._atualizar_status_os)
        self.os_context_menu.add_command(label="📝 Adicionar Observação", command=self._adicionar_observacao_os)
        
        self.os_tree.bind('<Button-3>', self._mostrar_os_context_menu)
        
        # Frame de botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="👁️ Ver Detalhes",
            command=self._visualizar_os_detalhes,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📄 Gerar PDF",
            command=self._gerar_pdf_os_selecionada,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🔄 Atualizar Status",
            command=self._atualizar_status_os,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Carrega OS inicialmente
        self._carregar_todas_os()
    
    def _buscar_os(self):
        """Busca OS com base nos filtros"""
        numero = self.filtro_numero_entry.get().strip().upper()
        status_texto = self.filtro_status_combo.get()
        
        try:
            # Limpa tabela
            for item in self.os_tree.get_children():
                self.os_tree.delete(item)
            
            # Se tem número específico, busca por número
            if numero:
                os_encontrada = os_service.buscar_por_numero(numero)
                if os_encontrada:
                    self._adicionar_os_na_tabela(os_encontrada)
                else:
                    messagebox.showinfo(
                        "OS não encontrada",
                        f"Nenhuma OS encontrada com número: {numero}",
                        parent=self.window
                    )
                return
            
            # Busca por status
            status_map = {
                "Todos": None,
                "Aberta": "aberta",
                "Em Andamento": "em_andamento",
                "Concluída": "concluida",
                "Cancelada": "cancelada"
            }
            
            status = status_map.get(status_texto)
            os_list = os_service.listar_todas(status=status)
            
            for os in os_list:
                self._adicionar_os_na_tabela(os)
            
            logger.info(f"{len(os_list)} OS encontradas")
            
        except Exception as e:
            logger.error(f"Erro ao buscar OS: {e}")
            messagebox.showerror(
                "Erro",
                f"Erro ao buscar OS:\n{str(e)}",
                parent=self.window
            )
    
    def _carregar_todas_os(self):
        """Carrega todas as OS"""
        try:
            # Limpa tabela
            for item in self.os_tree.get_children():
                self.os_tree.delete(item)
            
            # Busca todas as OS
            os_list = os_service.listar_todas(limite=200)
            
            for os in os_list:
                self._adicionar_os_na_tabela(os)
            
            logger.info(f"{len(os_list)} OS carregadas")
            
        except Exception as e:
            logger.error(f"Erro ao carregar OS: {e}")
            messagebox.showerror(
                "Erro",
                f"Erro ao carregar OS:\n{str(e)}",
                parent=self.window
            )
    
    def _adicionar_os_na_tabela(self, os):
        """Adiciona uma OS na tabela"""
        nome_cliente = f"{os['cliente_nome']} {os['cliente_sobrenome']}"
        defeito_resumo = os['defeito_relatado'][:50] + "..." if len(os['defeito_relatado']) > 50 else os['defeito_relatado']
        valor = validators.formatar_valor(os['valor_estimado'])
        data = os['criado_em'].strftime('%d/%m/%Y') if os['criado_em'] else ""
        prazo = os['prazo_previsto'].strftime('%d/%m/%Y') if os['prazo_previsto'] else ""
        
        # Define cor baseada no status
        tags = ()
        if os['status'] == 'aberta':
            tags = ('aberta',)
        elif os['status'] == 'em_andamento':
            tags = ('em_andamento',)
        elif os['status'] == 'concluida':
            tags = ('concluida',)
        elif os['status'] == 'cancelada':
            tags = ('cancelada',)
        
        self.os_tree.insert(
            "",
            tk.END,
            values=(
                os['numero_os'],
                data,
                nome_cliente,
                defeito_resumo,
                os['status'].replace('_', ' ').title(),
                valor,
                prazo
            ),
            tags=tags
        )
        
        # Configuração de cores por status
        self.os_tree.tag_configure('aberta', background='#ffe6e6')
        self.os_tree.tag_configure('em_andamento', background='#fff4e6')
        self.os_tree.tag_configure('concluida', background='#e6ffe6')
        self.os_tree.tag_configure('cancelada', background='#f0f0f0')
    
    def _limpar_filtros(self):
        """Limpa os filtros e recarrega todas as OS"""
        self.filtro_numero_entry.delete(0, tk.END)
        self.filtro_status_combo.set("Todos")
        self._carregar_todas_os()
    
    def _visualizar_os_detalhes(self, event=None):
        """Visualiza detalhes completos de uma OS"""
        selection = self.os_tree.selection()
        
        if not selection:
            messagebox.showwarning(
                "Nenhuma OS selecionada",
                "Selecione uma OS na lista!",
                parent=self.window
            )
            return
        
        # Pega número da OS
        item = self.os_tree.item(selection[0])
        numero_os = item['values'][0]
        
        try:
            # Busca OS completa
            os = os_service.buscar_por_numero(numero_os)
            
            if not os:
                messagebox.showerror("Erro", "OS não encontrada!", parent=self.window)
                return
            
            # Cria janela de detalhes
            detalhes_window = tk.Toplevel(self.window)
            detalhes_window.title(f"Detalhes - {numero_os}")
            detalhes_window.geometry("700x600")
            
            # Frame com scroll
            canvas = tk.Canvas(detalhes_window)
            scrollbar = ttk.Scrollbar(detalhes_window, orient=tk.VERTICAL, command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Conteúdo
            content_frame = ttk.Frame(scrollable_frame, padding="20")
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # Cabeçalho
            ttk.Label(
                content_frame,
                text=f"ORDEM DE SERVIÇO - {numero_os}",
                font=("Arial", 16, "bold")
            ).pack(pady=(0, 20))
            
            # Informações da OS
            info_os_frame = ttk.LabelFrame(content_frame, text="Informações da OS", padding="10")
            info_os_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(info_os_frame, text=f"Número: {os['numero_os']}", font=("Arial", 10, "bold")).pack(anchor=tk.W)
            ttk.Label(info_os_frame, text=f"Data de Abertura: {os['criado_em'].strftime('%d/%m/%Y %H:%M')}").pack(anchor=tk.W)
            ttk.Label(info_os_frame, text=f"Status: {os['status'].replace('_', ' ').title()}").pack(anchor=tk.W)
            ttk.Label(info_os_frame, text=f"Responsável: {os['usuario_nome']}").pack(anchor=tk.W)
            
            if os['valor_estimado']:
                ttk.Label(info_os_frame, text=f"Valor Estimado: {validators.formatar_valor(os['valor_estimado'])}").pack(anchor=tk.W)
            
            if os['prazo_previsto']:
                ttk.Label(info_os_frame, text=f"Prazo Previsto: {os['prazo_previsto'].strftime('%d/%m/%Y')}").pack(anchor=tk.W)
            
            if os['concluido_em']:
                ttk.Label(info_os_frame, text=f"Concluído em: {os['concluido_em'].strftime('%d/%m/%Y %H:%M')}").pack(anchor=tk.W)
            
            # Dados do cliente
            cliente_frame = ttk.LabelFrame(content_frame, text="Dados do Cliente", padding="10")
            cliente_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(cliente_frame, text=f"Nome: {os['cliente_nome']} {os['cliente_sobrenome']}", font=("Arial", 10, "bold")).pack(anchor=tk.W)
            ttk.Label(cliente_frame, text=f"CPF: {os['cliente_cpf']}").pack(anchor=tk.W)
            ttk.Label(cliente_frame, text=f"Telefone: {os['cliente_telefone']}").pack(anchor=tk.W)
            if os['cliente_email']:
                ttk.Label(cliente_frame, text=f"Email: {os['cliente_email']}").pack(anchor=tk.W)
            
            # Configuração do Hardware
            hardware_frame = ttk.LabelFrame(content_frame, text="Configuração do Hardware", padding="10")
            hardware_frame.pack(fill=tk.X, pady=(0, 10))
            
            if os['processador']:
                ttk.Label(hardware_frame, text=f"Processador: {os['processador']}").pack(anchor=tk.W, pady=2)
            if os['placa_mae']:
                ttk.Label(hardware_frame, text=f"Placa-mãe: {os['placa_mae']}").pack(anchor=tk.W, pady=2)
            if os['memoria_ram']:
                ttk.Label(hardware_frame, text=f"Memória RAM: {os['memoria_ram']}").pack(anchor=tk.W, pady=2)
            if os['armazenamento']:
                ttk.Label(hardware_frame, text=f"Armazenamento: {os['armazenamento']}").pack(anchor=tk.W, pady=2)
            if os['placa_video']:
                ttk.Label(hardware_frame, text=f"Placa de Vídeo: {os['placa_video']}").pack(anchor=tk.W, pady=2)
            if os['outros_componentes']:
                ttk.Label(hardware_frame, text=f"Outros: {os['outros_componentes']}").pack(anchor=tk.W, pady=2)
            
            # Defeito Relatado
            defeito_frame = ttk.LabelFrame(content_frame, text="Defeito Relatado", padding="10")
            defeito_frame.pack(fill=tk.X, pady=(0, 10))
            
            defeito_text = tk.Text(defeito_frame, height=5, wrap=tk.WORD, state='disabled')
            defeito_text.pack(fill=tk.X)
            defeito_text.config(state='normal')
            defeito_text.insert('1.0', os['defeito_relatado'])
            defeito_text.config(state='disabled')
            
            # Observações
            if os['observacoes']:
                obs_frame = ttk.LabelFrame(content_frame, text="Observações Técnicas", padding="10")
                obs_frame.pack(fill=tk.X, pady=(0, 10))
                
                obs_text = tk.Text(obs_frame, height=5, wrap=tk.WORD, state='disabled')
                obs_text.pack(fill=tk.X)
                obs_text.config(state='normal')
                obs_text.insert('1.0', os['observacoes'])
                obs_text.config(state='disabled')
            
            # Posicionamento final
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Botão fechar
            ttk.Button(
                detalhes_window,
                text="Fechar",
                command=detalhes_window.destroy
            ).pack(side=tk.BOTTOM, pady=10)
            
        except Exception as e:
            logger.error(f"Erro ao visualizar detalhes da OS: {e}")
            messagebox.showerror(
                "Erro",
                f"Erro ao visualizar detalhes:\n{str(e)}",
                parent=self.window
            )
    
    def _atualizar_status_os(self):
        """Atualiza o status de uma OS"""
        selection = self.os_tree.selection()
        
        if not selection:
            messagebox.showwarning(
                "Nenhuma OS selecionada",
                "Selecione uma OS na lista!",
                parent=self.window
            )
            return
        
        # Pega número da OS
        item = self.os_tree.item(selection[0])
        numero_os = item['values'][0]
        
        try:
            # Busca OS
            os = os_service.buscar_por_numero(numero_os)
            
            if not os:
                messagebox.showerror("Erro", "OS não encontrada!", parent=self.window)
                return
            
            # Janela de atualização de status
            status_window = tk.Toplevel(self.window)
            status_window.title(f"Atualizar Status - {numero_os}")
            status_window.geometry("400x250")
            status_window.transient(self.window)
            status_window.grab_set()
            
            frame = ttk.Frame(status_window, padding="20")
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text=f"OS: {numero_os}", font=("Arial", 12, "bold")).pack(pady=(0, 10))
            ttk.Label(frame, text=f"Status Atual: {os['status'].replace('_', ' ').title()}").pack(pady=(0, 20))
            
            ttk.Label(frame, text="Novo Status:").pack(anchor=tk.W, pady=5)
            
            status_combo = ttk.Combobox(
                frame,
                values=["Aberta", "Em Andamento", "Concluída", "Cancelada"],
                state="readonly",
                width=25
            )
            status_combo.pack(pady=5)
            status_combo.set("Aberta")
            
            ttk.Label(frame, text="Observação (opcional):").pack(anchor=tk.W, pady=(10, 5))
            obs_text = tk.Text(frame, height=4, width=40)
            obs_text.pack(pady=5)
            
            def salvar_status():
                novo_status_texto = status_combo.get()
                observacao = obs_text.get("1.0", tk.END).strip()
                
                status_map = {
                    "Aberta": "aberta",
                    "Em Andamento": "em_andamento",
                    "Concluída": "concluida",
                    "Cancelada": "cancelada"
                }
                
                novo_status = status_map[novo_status_texto]
                
                try:
                    sucesso = os_service.atualizar_status(
                        os['id'],
                        novo_status,
                        observacao if observacao else None
                    )
                    
                    if sucesso:
                        messagebox.showinfo(
                            "Sucesso",
                            f"Status atualizado para: {novo_status_texto}",
                            parent=status_window
                        )
                        status_window.destroy()
                        self._buscar_os()  # Atualiza a lista
                    else:
                        messagebox.showerror("Erro", "Falha ao atualizar status!", parent=status_window)
                        
                except Exception as e:
                    logger.error(f"Erro ao atualizar status: {e}")
                    messagebox.showerror("Erro", str(e), parent=status_window)
            
            button_frame = ttk.Frame(frame)
            button_frame.pack(pady=20)
            
            ttk.Button(button_frame, text="✅ Salvar", command=salvar_status, width=12).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="❌ Cancelar", command=status_window.destroy, width=12).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status: {e}")
            messagebox.showerror("Erro", str(e), parent=self.window)
    
    def _adicionar_observacao_os(self):
        """Adiciona observação a uma OS"""
        selection = self.os_tree.selection()
        
        if not selection:
            messagebox.showwarning(
                "Nenhuma OS selecionada",
                "Selecione uma OS na lista!",
                parent=self.window
            )
            return
        
        # Pega número da OS
        item = self.os_tree.item(selection[0])
        numero_os = item['values'][0]
        
        try:
            # Busca OS
            os = os_service.buscar_por_numero(numero_os)
            
            if not os:
                messagebox.showerror("Erro", "OS não encontrada!", parent=self.window)
                return
            
            # Janela para adicionar observação
            obs_window = tk.Toplevel(self.window)
            obs_window.title(f"Adicionar Observação - {numero_os}")
            obs_window.geometry("500x300")
            obs_window.transient(self.window)
            obs_window.grab_set()
            
            frame = ttk.Frame(obs_window, padding="20")
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text=f"OS: {numero_os}", font=("Arial", 12, "bold")).pack(pady=(0, 20))
            ttk.Label(frame, text="Nova Observação:").pack(anchor=tk.W, pady=5)
            
            obs_text = tk.Text(frame, height=8, width=50)
            obs_text.pack(pady=5, fill=tk.BOTH, expand=True)
            obs_text.focus()
            
            def salvar_observacao():
                observacao = obs_text.get("1.0", tk.END).strip()
                
                if not observacao:
                    messagebox.showwarning("Campo vazio", "Digite uma observação!", parent=obs_window)
                    return
                
                try:
                    sucesso = os_service.adicionar_observacao(os['id'], observacao)
                    
                    if sucesso:
                        messagebox.showinfo("Sucesso", "Observação adicionada!", parent=obs_window)
                        obs_window.destroy()
                    else:
                        messagebox.showerror("Erro", "Falha ao adicionar observação!", parent=obs_window)
                        
                except Exception as e:
                    logger.error(f"Erro ao adicionar observação: {e}")
                    messagebox.showerror("Erro", str(e), parent=obs_window)
            
            button_frame = ttk.Frame(frame)
            button_frame.pack(pady=20)
            
            ttk.Button(button_frame, text="✅ Salvar", command=salvar_observacao, width=12).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="❌ Cancelar", command=obs_window.destroy, width=12).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            logger.error(f"Erro ao adicionar observação: {e}")
            messagebox.showerror("Erro", str(e), parent=self.window)
    
    def _gerar_pdf_os_selecionada(self):
        """Gera PDF da OS selecionada"""
        selection = self.os_tree.selection()
        
        if not selection:
            messagebox.showwarning(
                "Nenhuma OS selecionada",
                "Selecione uma OS na lista!",
                parent=self.window
            )
            return
        
        # Pega número da OS
        item = self.os_tree.item(selection[0])
        numero_os = item['values'][0]
        
        try:
            # Busca OS
            os = os_service.buscar_por_numero(numero_os)
            
            if not os:
                messagebox.showerror("Erro", "OS não encontrada!", parent=self.window)
                return
            
            self._gerar_pdf_os(os['id'])
            
        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {e}")
            messagebox.showerror("Erro", str(e), parent=self.window)
    
    def _gerar_pdf_os(self, os_id):
        """Gera PDF de uma OS (será implementado com pdf_preview_window)"""
        try:
            from ui.pdf_preview_window import PDFPreviewWindow
            PDFPreviewWindow(self.window, os_id)
        except ImportError:
            messagebox.showinfo(
                "Em desenvolvimento",
                "A funcionalidade de geração de PDF será implementada na próxima etapa!",
                parent=self.window
            )
    
    def _mostrar_os_context_menu(self, event):
        """Mostra menu de contexto"""
        item = self.os_tree.identify_row(event.y)
        if item:
            self.os_tree.selection_set(item)
            self.os_context_menu.post(event.x_root, event.y_root)