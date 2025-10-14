import tkinter as tk
from tkinter import ttk, messagebox

class TenantListWidget:
    """Widget que encapsula a lista de inquilinos com busca e ações."""

    def __init__(self, parent, on_add=None, on_view=None, on_edit=None, on_delete=None):
        container = tk.Frame(parent, bg='#f0f0f0')
        container.pack(fill='both', expand=True, padx=20, pady=20)

        # Top frame com botão adicionar
        top_frame = tk.Frame(container, bg='#f0f0f0')
        top_frame.pack(fill='x', pady=(0, 10))

        self.btn_add = tk.Button(
            top_frame,
            text="➕ Adicionar Novo Inquilino",
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

        # Barra de busca
        search_frame = tk.Frame(container, bg='white', relief='solid', borderwidth=1)
        search_frame.pack(fill='x', pady=(0, 15))

        tk.Label(search_frame, text="🔍 Buscar:", bg='white', font=("Arial", 10)).pack(side='left', padx=10)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 11), width=40)
        self.search_entry.pack(side='left', padx=5, pady=8)

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

        # callbacks
        self._on_view = on_view
        self._on_edit = on_edit
        self._on_delete = on_delete

        # bind search
        self.search_var.trace('w', lambda *args: self._on_search_change())

        # internal storage of items
        self._items = []

    def _on_search_change(self):
        # external filtering should be implemented by owner; we provide the search term
        pass

    def clear_list(self):
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

    def set_items(self, inquilinos):
        """Popula a lista visual com os objetos inquilino."""
        self._items = inquilinos
        self.clear_list()

        if not inquilinos:
            tk.Label(
                self.scrollable_frame,
                text="Nenhum inquilino cadastrado ainda",
                font=("Arial", 12),
                bg='white',
                fg='gray'
            ).pack(pady=50)
            return

        # Header
        header = tk.Frame(self.scrollable_frame, bg='#E3F2FD', height=40)
        header.pack(fill='x', padx=10, pady=(10, 0))

        tk.Label(header, text="Nome", bg='#E3F2FD', font=("Arial", 10, "bold"), width=25, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="CPF", bg='#E3F2FD', font=("Arial", 10, "bold"), width=15, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="Telefone", bg='#E3F2FD', font=("Arial", 10, "bold"), width=15, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="Nascimento", bg='#E3F2FD', font=("Arial", 10, "bold"), width=12, anchor='center').pack(side='left', padx=5)
        tk.Label(header, text="Ações", bg='#E3F2FD', font=("Arial", 10, "bold"), width=15, anchor='center').pack(side='left', padx=5)

        for i, inquilino in enumerate(inquilinos):
            self._create_item(inquilino, i)

    def _create_item(self, inquilino, index):
        bg_color = '#FFFFFF' if index % 2 == 0 else '#F5F5F5'

        item_frame = tk.Frame(self.scrollable_frame, bg=bg_color, relief='solid', borderwidth=1)
        item_frame.pack(fill='x', padx=10, pady=2)

        # Nome
        nome_text = inquilino.nome_completo[:30] + "..." if len(inquilino.nome_completo) > 30 else inquilino.nome_completo
        tk.Label(item_frame, text=nome_text, bg=bg_color, font=("Arial", 10), width=25, anchor='w').pack(side='left', padx=5, pady=10)

        # CPF
        tk.Label(item_frame, text=inquilino.cpf, bg=bg_color, font=("Arial", 10), width=15, anchor='w').pack(side='left', padx=5)

        # Telefone
        tk.Label(item_frame, text=inquilino.telefone, bg=bg_color, font=("Arial", 10), width=15, anchor='w').pack(side='left', padx=5)

        # Data de Nascimento
        data_nasc = inquilino.data_nascimento.strftime('%d/%m/%Y') if inquilino.data_nascimento else "-"
        tk.Label(item_frame, text=data_nasc, bg=bg_color, font=("Arial", 10), width=12, anchor='center').pack(side='left', padx=5)

        # Botões
        action_frame = tk.Frame(item_frame, bg=bg_color)
        action_frame.pack(side='left', padx=5)

        tk.Button(action_frame, text="👁️ Ver", command=lambda: self._on_view(inquilino), bg='#9C27B0', fg='white', font=("Arial", 9), relief='flat', cursor='hand2', padx=8, pady=5).pack(side='left', padx=2)
        tk.Button(action_frame, text="✏️ Editar", command=lambda: self._on_edit(inquilino), bg='#2196F3', fg='white', font=("Arial", 9), relief='flat', cursor='hand2', padx=8, pady=5).pack(side='left', padx=2)
        tk.Button(action_frame, text="🗑️", command=lambda: self._on_delete(inquilino.id), bg='#F44336', fg='white', font=("Arial", 9), relief='flat', cursor='hand2', padx=8, pady=5).pack(side='left', padx=2)
