import tkinter as tk
from tkinter import ttk


class ContractListWidget:
    """Widget que encapsula a lista de contratos com busca e filtros."""

    def __init__(self, parent, on_add=None, on_view=None, on_edit=None, on_end=None, on_generate_pdf=None):
        container = tk.Frame(parent, bg='#f0f0f0')
        container.pack(fill='both', expand=True, padx=20, pady=20)

        # Top frame com botão adicionar e filtros
        top_frame = tk.Frame(container, bg='#f0f0f0')
        top_frame.pack(fill='x', pady=(0, 10))

        self.btn_add = tk.Button(
            top_frame,
            text="➕ Adicionar Novo Contrato",
            command=on_add,
            bg='#4CAF50',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            relief='flat',
            cursor='hand2'
        )
        self.btn_add.pack(side='left')

        # Frame de filtros
        filter_frame = tk.Frame(container, bg='white', relief='solid', borderwidth=1)
        filter_frame.pack(fill='x', pady=(0, 15))

        filter_content = tk.Frame(filter_frame, bg='white')
        filter_content.pack(fill='x', padx=15, pady=10)

        # Filtro por Status
        tk.Label(filter_content, text="Status:", bg='white', font=("Arial", 10)).pack(side='left', padx=(0, 5))
        self.filter_status = ttk.Combobox(
            filter_content, 
            font=("Arial", 10), 
            width=15, 
            state='readonly',
            values=['Todos', 'Vigente', 'Vencido', 'Encerrado', 'Futuro']
        )
        self.filter_status.set('Todos')
        self.filter_status.pack(side='left', padx=5)

        # Filtro por Casa
        tk.Label(filter_content, text="Casa:", bg='white', font=("Arial", 10)).pack(side='left', padx=(15, 5))
        self.filter_casa = ttk.Combobox(filter_content, font=("Arial", 10), width=30, state='readonly')
        self.filter_casa.pack(side='left', padx=5)

        # Barra de busca por inquilino
        tk.Label(filter_content, text="🔍 Inquilino:", bg='white', font=("Arial", 10)).pack(side='left', padx=(15, 5))
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(filter_content, textvariable=self.search_var, font=("Arial", 10), width=25)
        self.search_entry.pack(side='left', padx=5)

        # Lista com scroll
        list_container = tk.Frame(container, bg='white', relief='solid', borderwidth=1)
        list_container.pack(fill='both', expand=True)

        self.canvas = tk.Canvas(list_container, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Callbacks
        self._on_view = on_view
        self._on_edit = on_edit
        self._on_end = on_end
        self._on_generate_pdf = on_generate_pdf

        self._items = []

    def clear_list(self):
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

    def set_items(self, contratos):
        """Popula a lista visual com os objetos contrato."""
        self._items = contratos
        self.clear_list()

        if not contratos:
            tk.Label(
                self.scrollable_frame,
                text="Nenhum contrato cadastrado ainda",
                font=("Arial", 12),
                bg='white',
                fg='gray'
            ).pack(pady=50)
            return

        # Header
        header = tk.Frame(self.scrollable_frame, bg='#E3F2FD', height=40)
        header.pack(fill='x', padx=10, pady=(10, 0))

        tk.Label(header, text="Casa", bg='#E3F2FD', font=("Arial", 10, "bold"), width=20, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="Inquilino", bg='#E3F2FD', font=("Arial", 10, "bold"), width=20, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="Valor", bg='#E3F2FD', font=("Arial", 10, "bold"), width=12, anchor='center').pack(side='left', padx=5)
        tk.Label(header, text="Início", bg='#E3F2FD', font=("Arial", 10, "bold"), width=10, anchor='center').pack(side='left', padx=5)
        tk.Label(header, text="Fim", bg='#E3F2FD', font=("Arial", 10, "bold"), width=10, anchor='center').pack(side='left', padx=5)
        tk.Label(header, text="Status", bg='#E3F2FD', font=("Arial", 10, "bold"), width=10, anchor='center').pack(side='left', padx=5)
        tk.Label(header, text="Ações", bg='#E3F2FD', font=("Arial", 10, "bold"), width=25, anchor='center').pack(side='left', padx=5)

        for i, contrato in enumerate(contratos):
            self._create_item(contrato, i)

    def _create_item(self, contrato, index):
        bg_color = '#FFFFFF' if index % 2 == 0 else '#F5F5F5'

        item_frame = tk.Frame(self.scrollable_frame, bg=bg_color, relief='solid', borderwidth=1)
        item_frame.pack(fill='x', padx=10, pady=2)

        # Casa
        casa_nome = contrato.casa.nome if hasattr(contrato, 'casa') else "N/A"
        casa_text = casa_nome[:18] + "..." if len(casa_nome) > 18 else casa_nome
        tk.Label(item_frame, text=casa_text, bg=bg_color, font=("Arial", 10), width=20, anchor='w').pack(side='left', padx=5, pady=10)

        # Inquilino
        inquilino_nome = contrato.inquilino.nome_completo if hasattr(contrato, 'inquilino') else "N/A"
        inquilino_text = inquilino_nome[:18] + "..." if len(inquilino_nome) > 18 else inquilino_nome
        tk.Label(item_frame, text=inquilino_text, bg=bg_color, font=("Arial", 10), width=20, anchor='w').pack(side='left', padx=5)

        # Valor
        tk.Label(item_frame, text=f"R$ {contrato.valor_aluguel:.2f}", bg=bg_color, font=("Arial", 10, "bold"), fg='#2E7D32', width=12, anchor='center').pack(side='left', padx=5)

        # Data de Início
        data_inicio_str = contrato.data_inicio.strftime('%d/%m/%Y') if contrato.data_inicio else "-"
        tk.Label(item_frame, text=data_inicio_str, bg=bg_color, font=("Arial", 9), width=10, anchor='center').pack(side='left', padx=5)

        # Data de Fim
        data_fim_str = contrato.data_fim.strftime('%d/%m/%Y') if contrato.data_fim else "-"
        tk.Label(item_frame, text=data_fim_str, bg=bg_color, font=("Arial", 9), width=10, anchor='center').pack(side='left', padx=5)

        # Status com cor
        status = contrato.status_descricao
        status_color = {
            'Vigente': '#4CAF50',
            'Vencido': '#FF9800',
            'Encerrado': '#9E9E9E',
            'Futuro': '#2196F3'
        }.get(status, '#9E9E9E')
        
        tk.Label(item_frame, text=status, bg=bg_color, fg=status_color, font=("Arial", 9, "bold"), width=10, anchor='center').pack(side='left', padx=5)

        # Botões de ação
        action_frame = tk.Frame(item_frame, bg=bg_color)
        action_frame.pack(side='left', padx=5)

        tk.Button(
            action_frame, 
            text="👁️ Ver", 
            command=lambda: self._on_view(contrato), 
            bg='#9C27B0', 
            fg='white', 
            font=("Arial", 8), 
            relief='flat', 
            cursor='hand2', 
            padx=6, 
            pady=4
        ).pack(side='left', padx=2)

        tk.Button(
            action_frame, 
            text="✏️ Editar", 
            command=lambda: self._on_edit(contrato), 
            bg='#2196F3', 
            fg='white', 
            font=("Arial", 8), 
            relief='flat', 
            cursor='hand2', 
            padx=6, 
            pady=4
        ).pack(side='left', padx=2)

        tk.Button(
            action_frame, 
            text="📄 PDF", 
            command=lambda: self._on_generate_pdf(contrato), 
            bg='#00BCD4', 
            fg='white', 
            font=("Arial", 8), 
            relief='flat', 
            cursor='hand2', 
            padx=6, 
            pady=4
        ).pack(side='left', padx=2)

        # Botão de encerrar (apenas para contratos ativos)
        if contrato.ativo:
            tk.Button(
                action_frame, 
                text="🔒 Encerrar", 
                command=lambda: self._on_end(contrato.id), 
                bg='#F44336', 
                fg='white', 
                font=("Arial", 8), 
                relief='flat', 
                cursor='hand2', 
                padx=6, 
                pady=4
            ).pack(side='left', padx=2)