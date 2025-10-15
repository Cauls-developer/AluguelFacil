import tkinter as tk
from tkinter import ttk


class ReceiptListWidget:
    """Widget que encapsula a lista de recibos com busca e filtros."""

    def __init__(self, parent, on_add=None, on_view=None, on_reprint=None, on_delete=None):
        container = tk.Frame(parent, bg='#f0f0f0')
        container.pack(fill='both', expand=True, padx=20, pady=20)

        # Top frame com botão adicionar e filtros
        top_frame = tk.Frame(container, bg='#f0f0f0')
        top_frame.pack(fill='x', pady=(0, 10))

        self.btn_add = tk.Button(
            top_frame,
            text="➕ Adicionar Novo Recibo",
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

        # Filtro por Tipo
        tk.Label(filter_content, text="Tipo:", bg='white', font=("Arial", 10)).pack(side='left', padx=(0, 5))
        self.filter_tipo = ttk.Combobox(
            filter_content,
            font=("Arial", 10),
            width=20,
            state='readonly',
            values=['Todos', 'Aluguel', 'Conta de Energia', 'Serviço Prestado', 'Outros']
        )
        self.filter_tipo.set('Todos')
        self.filter_tipo.pack(side='left', padx=5)

        # Barra de busca por pagador
        tk.Label(filter_content, text="🔍 Pagador:", bg='white', font=("Arial", 10)).pack(side='left', padx=(15, 5))
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(filter_content, textvariable=self.search_var, font=("Arial", 10), width=30)
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
        self._on_reprint = on_reprint
        self._on_delete = on_delete

        self._items = []

    def clear_list(self):
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

    def set_items(self, recibos):
        """Popula a lista visual com os objetos recibo."""
        self._items = recibos
        self.clear_list()

        if not recibos:
            tk.Label(
                self.scrollable_frame,
                text="Nenhum recibo cadastrado ainda",
                font=("Arial", 12),
                bg='white',
                fg='gray'
            ).pack(pady=50)
            return

        # Header
        header = tk.Frame(self.scrollable_frame, bg='#E3F2FD', height=40)
        header.pack(fill='x', padx=10, pady=(10, 0))

        tk.Label(header, text="Nº", bg='#E3F2FD', font=("Arial", 10, "bold"), width=8, anchor='center').pack(side='left', padx=5)
        tk.Label(header, text="Data Pag.", bg='#E3F2FD', font=("Arial", 10, "bold"), width=12, anchor='center').pack(side='left', padx=5)
        tk.Label(header, text="Tipo", bg='#E3F2FD', font=("Arial", 10, "bold"), width=15, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="Pagador", bg='#E3F2FD', font=("Arial", 10, "bold"), width=25, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="Referente a", bg='#E3F2FD', font=("Arial", 10, "bold"), width=25, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="Valor", bg='#E3F2FD', font=("Arial", 10, "bold"), width=12, anchor='center').pack(side='left', padx=5)
        tk.Label(header, text="Ações", bg='#E3F2FD', font=("Arial", 10, "bold"), width=20, anchor='center').pack(side='left', padx=5)

        for i, recibo in enumerate(recibos):
            self._create_item(recibo, i)

    def _create_item(self, recibo, index):
        bg_color = '#FFFFFF' if index % 2 == 0 else '#F5F5F5'

        item_frame = tk.Frame(self.scrollable_frame, bg=bg_color, relief='solid', borderwidth=1)
        item_frame.pack(fill='x', padx=10, pady=2)

        # Número
        tk.Label(item_frame, text=f"#{recibo.id}", bg=bg_color, font=("Arial", 10, "bold"), width=8, anchor='center').pack(side='left', padx=5, pady=10)

        # Data de Pagamento
        data_str = recibo.data_pagamento.strftime('%d/%m/%Y') if recibo.data_pagamento else "-"
        tk.Label(item_frame, text=data_str, bg=bg_color, font=("Arial", 9), width=12, anchor='center').pack(side='left', padx=5)

        # Tipo
        tipo_map = {
            'aluguel': 'Aluguel',
            'energia': 'Energia',
            'servico': 'Serviço',
            'outros': 'Outros'
        }
        tipo_display = tipo_map.get(recibo.tipo_recibo, recibo.tipo_recibo)
        tk.Label(item_frame, text=tipo_display, bg=bg_color, font=("Arial", 9), width=15, anchor='w').pack(side='left', padx=5)

        # Pagador
        pagador_text = recibo.nome_pagador[:23] + "..." if len(recibo.nome_pagador) > 23 else recibo.nome_pagador
        tk.Label(item_frame, text=pagador_text, bg=bg_color, font=("Arial", 9), width=25, anchor='w').pack(side='left', padx=5)

        # Referente a
        ref_text = recibo.referente_a[:23] + "..." if len(recibo.referente_a) > 23 else recibo.referente_a
        tk.Label(item_frame, text=ref_text, bg=bg_color, font=("Arial", 9), width=25, anchor='w').pack(side='left', padx=5)

        # Valor
        tk.Label(item_frame, text=f"R$ {recibo.valor:.2f}", bg=bg_color, font=("Arial", 10, "bold"), fg='#2E7D32', width=12, anchor='center').pack(side='left', padx=5)

        # Botões de ação
        action_frame = tk.Frame(item_frame, bg=bg_color)
        action_frame.pack(side='left', padx=5)

        tk.Button(
            action_frame,
            text="👁️ Ver",
            command=lambda: self._on_view(recibo),
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
            text="🖨️ Imprimir",
            command=lambda: self._on_reprint(recibo),
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
            text="🗑️",
            command=lambda: self._on_delete(recibo.id),
            bg='#F44336',
            fg='white',
            font=("Arial", 8),
            relief='flat',
            cursor='hand2',
            padx=6,
            pady=4
        ).pack(side='left', padx=2)