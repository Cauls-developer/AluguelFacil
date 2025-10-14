import tkinter as tk
from tkinter import ttk

class HouseListWidget:
    """Widget que encapsula a lista de casas com busca e ações."""

    def __init__(self, parent, on_add=None, on_edit=None, on_delete=None):
        container = tk.Frame(parent, bg='#f0f0f0')
        container.pack(fill='both', expand=True, padx=20, pady=20)

        # Top frame com botão adicionar
        top_frame = tk.Frame(container, bg='#f0f0f0')
        top_frame.pack(fill='x', pady=(0, 10))

        self.btn_add = tk.Button(
            top_frame,
            text="➕ Adicionar Nova Casa",
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
        self._on_edit = on_edit
        self._on_delete = on_delete

        self._items = []

    def clear_list(self):
        for w in self.scrollable_frame.winfo_children():
            w.destroy()

    def set_items(self, casas):
        self._items = casas
        self.clear_list()

        if not casas:
            tk.Label(
                self.scrollable_frame,
                text="Nenhuma casa cadastrada ainda",
                font=("Arial", 12),
                bg='white',
                fg='gray'
            ).pack(pady=50)
            return

        # Header
        header = tk.Frame(self.scrollable_frame, bg='#E3F2FD', height=40)
        header.pack(fill='x', padx=10, pady=(10, 0))

        tk.Label(header, text="Casa", bg='#E3F2FD', font=("Arial", 10, "bold"), width=20, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="Endereço", bg='#E3F2FD', font=("Arial", 10, "bold"), width=40, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="Inquilino", bg='#E3F2FD', font=("Arial", 10, "bold"), width=25, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="Ações", bg='#E3F2FD', font=("Arial", 10, "bold"), width=15, anchor='center').pack(side='left', padx=5)

        for i, casa in enumerate(casas):
            self._create_item(casa, i)

    def _create_item(self, casa, index):
        bg_color = '#FFFFFF' if index % 2 == 0 else '#F5F5F5'

        item_frame = tk.Frame(self.scrollable_frame, bg=bg_color, relief='solid', borderwidth=1)
        item_frame.pack(fill='x', padx=10, pady=2)

        tk.Label(item_frame, text=casa.nome, bg=bg_color, font=("Arial", 10), width=20, anchor='w').pack(side='left', padx=5, pady=10)

        tk.Label(item_frame, text=casa.endereco[:50] + "..." if len(casa.endereco) > 50 else casa.endereco, bg=bg_color, font=("Arial", 10), width=40, anchor='w').pack(side='left', padx=5)

        inquilino_text = casa.inquilino_atual.nome_completo if casa.inquilino_atual else "Disponível"
        inquilino_color = '#4CAF50' if not casa.inquilino_atual else '#1976D2'
        tk.Label(item_frame, text=inquilino_text, bg=bg_color, fg=inquilino_color, font=("Arial", 10), width=25, anchor='w').pack(side='left', padx=5)

        action_frame = tk.Frame(item_frame, bg=bg_color)
        action_frame.pack(side='left', padx=5)

        tk.Button(action_frame, text="✏️ Editar", command=lambda: self._on_edit(casa), bg='#2196F3', fg='white', font=("Arial", 9), relief='flat', cursor='hand2', padx=10, pady=5).pack(side='left', padx=2)
        tk.Button(action_frame, text="🗑️", command=lambda: self._on_delete(casa.id), bg='#F44336', fg='white', font=("Arial", 9), relief='flat', cursor='hand2', padx=10, pady=5).pack(side='left', padx=2)
