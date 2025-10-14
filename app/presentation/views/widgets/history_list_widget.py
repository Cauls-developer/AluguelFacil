import tkinter as tk
from tkinter import ttk

class HistoryList:
    """Widget que encapsula a aba de histórico e a lista de consumos."""

    def __init__(self, parent, on_filter_change=None):
        container = tk.Frame(parent, bg='white')
        container.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(container, text="Histórico de Contas", font=("Arial", 16, "bold"), bg='white', fg='#1565C0').pack(anchor='w', pady=(0, 15))

        filter_frame = tk.Frame(container, bg='#F5F5F5', relief='solid', borderwidth=1)
        filter_frame.pack(fill='x', pady=(0, 15))

        filter_content = tk.Frame(filter_frame, bg='#F5F5F5')
        filter_content.pack(fill='x', padx=15, pady=15)

        tk.Label(filter_content, text="Filtrar por Casa:", bg='#F5F5F5', font=("Arial", 10)).pack(side='left', padx=(0, 10))
        self.filter_casa = ttk.Combobox(filter_content, font=("Arial", 10), width=40, state='readonly')
        self.filter_casa.pack(side='left', padx=5)
        if on_filter_change:
            self.filter_casa.bind('<<ComboboxSelected>>', lambda e: on_filter_change())

        tk.Button(
            filter_content,
            text="🔄 Atualizar",
            command=on_filter_change,
            bg='#2196F3',
            fg='white',
            font=("Arial", 10),
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=5
        ).pack(side='left', padx=10)

        list_container = tk.Frame(container, bg='white', relief='solid', borderwidth=1)
        list_container.pack(fill='both', expand=True)

        self.history_canvas = tk.Canvas(list_container, bg='white', highlightthickness=0)
        history_scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.history_canvas.yview)
        self.history_frame = tk.Frame(self.history_canvas, bg='white')

        self.history_frame.bind(
            "<Configure>",
            lambda e: self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all"))
        )

        self.history_canvas.create_window((0, 0), window=self.history_frame, anchor="nw")
        self.history_canvas.configure(yscrollcommand=history_scrollbar.set)

        self.history_canvas.pack(side="left", fill="both", expand=True)
        history_scrollbar.pack(side="right", fill="y")

    def clear_list(self):
        for w in self.history_frame.winfo_children():
            w.destroy()

    def set_filter_values(self, values):
        self.filter_casa['values'] = values
        if values:
            self.filter_casa.set(values[0])

    def create_header(self):
        header = tk.Frame(self.history_frame, bg='#E3F2FD', height=40)
        header.pack(fill='x', padx=10, pady=(10, 0))

        tk.Label(header, text="Período", bg='#E3F2FD', font=("Arial", 10, "bold"), width=12, anchor='center').pack(side='left', padx=5)
        tk.Label(header, text="Casa", bg='#E3F2FD', font=("Arial", 10, "bold"), width=20, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="Inquilino", bg='#E3F2FD', font=("Arial", 10, "bold"), width=20, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="Consumo", bg='#E3F2FD', font=("Arial", 10, "bold"), width=10, anchor='center').pack(side='left', padx=5)
        tk.Label(header, text="Valor", bg='#E3F2FD', font=("Arial", 10, "bold"), width=12, anchor='center').pack(side='left', padx=5)
        tk.Label(header, text="Ações", bg='#E3F2FD', font=("Arial", 10, "bold"), width=20, anchor='center').pack(side='left', padx=5)

    def add_item(self, consumo, index, view_callbacks):
        """Adiciona um item de histórico. view_callbacks é um dict com chaves: view, reprint, delete"""
        bg_color = '#FFFFFF' if index % 2 == 0 else '#F5F5F5'

        item_frame = tk.Frame(self.history_frame, bg=bg_color, relief='solid', borderwidth=1)
        item_frame.pack(fill='x', padx=10, pady=2)

        periodo = f"{consumo.mes:02d}/{consumo.ano}"
        tk.Label(item_frame, text=periodo, bg=bg_color, font=("Arial", 10, "bold"), width=12, anchor='center').pack(side='left', padx=5, pady=10)

        casa_nome = consumo.casa_obj.nome if hasattr(consumo, 'casa_obj') else consumo.casa.nome
        tk.Label(item_frame, text=casa_nome, bg=bg_color, font=("Arial", 10), width=20, anchor='w').pack(side='left', padx=5)

        inquilino_nome = "-"
        if hasattr(consumo, 'casa_obj') and consumo.casa_obj.inquilino_atual:
            inquilino_nome = consumo.casa_obj.inquilino_atual.nome_completo[:20]
        elif consumo.casa.inquilino_atual:
            inquilino_nome = consumo.casa.inquilino_atual.nome_completo[:20]
        tk.Label(item_frame, text=inquilino_nome, bg=bg_color, font=("Arial", 10), width=20, anchor='w').pack(side='left', padx=5)

        consumo_valor = consumo.consumo_diferenca
        tk.Label(item_frame, text=f"{consumo_valor:.1f} kWh", bg=bg_color, font=("Arial", 10), width=10, anchor='center').pack(side='left', padx=5)

        valor = consumo.consumo_individual_proporcional if consumo.consumo_individual_proporcional else 0
        tk.Label(item_frame, text=f"R$ {valor:.2f}", bg=bg_color, font=("Arial", 10, "bold"), fg='#2E7D32', width=12, anchor='center').pack(side='left', padx=5)

        action_frame = tk.Frame(item_frame, bg=bg_color)
        action_frame.pack(side='left', padx=5)

        tk.Button(
            action_frame,
            text="👁️ Ver",
            command=lambda: view_callbacks['view'](consumo),
            bg='#9C27B0',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=5
        ).pack(side='left', padx=2)

        tk.Button(
            action_frame,
            text="🖨️ Imprimir",
            command=lambda: view_callbacks['reprint'](consumo),
            bg='#2196F3',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=5
        ).pack(side='left', padx=2)

        tk.Button(
            action_frame,
            text="🗑️",
            command=lambda: view_callbacks['delete'](consumo.id),
            bg='#F44336',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=5
        ).pack(side='left', padx=2)
