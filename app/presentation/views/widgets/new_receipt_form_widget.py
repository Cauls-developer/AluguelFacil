import tkinter as tk
from tkinter import ttk
from datetime import datetime
try:
    from tkcalendar import DateEntry
    TKCALENDAR_AVAILABLE = True
except ImportError:
    TKCALENDAR_AVAILABLE = False


class NewReceiptForm:
    """Widget que encapsula o formulário de novo recibo."""

    def __init__(self, parent, on_save=None, on_generate_pdf=None, on_clear=None):
        # Criar estrutura com canvas para scroll
        canvas = tk.Canvas(parent, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='white')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        content = tk.Frame(self.scrollable_frame, bg='white')
        content.pack(fill='both', expand=True, padx=40, pady=30)

        tk.Label(
            content,
            text="Gerar Novo Recibo de Pagamento",
            font=("Arial", 16, "bold"),
            bg='white',
            fg='#1565C0'
        ).pack(anchor='w', pady=(0, 20))

        # ==== TIPO DE RECIBO ====
        self._create_section_header(content, "📋 Tipo de Recibo")

        tk.Label(content, text="Tipo de Recibo:*", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(10, 5))
        self.combo_tipo = ttk.Combobox(
            content,
            font=("Arial", 11),
            width=60,
            state='readonly',
            values=['Aluguel', 'Conta de Energia', 'Serviço Prestado', 'Outros']
        )
        self.combo_tipo.set('Aluguel')
        self.combo_tipo.pack(fill='x', pady=(0, 15))

        # ==== DADOS DO PAGADOR ====
        self._create_section_header(content, "💰 Dados do Pagador")

        # Casa/Inquilino (opcional)
        tk.Label(content, text="Selecionar Casa (opcional):", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(10, 5))
        self.combo_casa = ttk.Combobox(content, font=("Arial", 11), width=60, state='readonly')
        self.combo_casa.pack(fill='x', pady=(0, 15))

        tk.Label(content, text="Ou Selecionar Inquilino (opcional):", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        self.combo_inquilino = ttk.Combobox(content, font=("Arial", 11), width=60, state='readonly')
        self.combo_inquilino.pack(fill='x', pady=(0, 15))

        tk.Label(content, text="Nome do Pagador:*", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        self.entry_nome_pagador = tk.Entry(content, font=("Arial", 11))
        self.entry_nome_pagador.pack(fill='x', pady=(0, 15))

        tk.Label(content, text="CPF do Pagador (opcional):", bg='white', font=("Arial", 11)).pack(anchor='w', pady=(0, 5))
        self.entry_cpf_pagador = tk.Entry(content, font=("Arial", 11))
        self.entry_cpf_pagador.pack(fill='x', pady=(0, 15))

        # ==== DADOS DO RECEBEDOR ====
        self._create_section_header(content, "👤 Dados do Recebedor")

        tk.Label(content, text="Nome do Recebedor:*", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(10, 5))
        self.entry_nome_recebedor = tk.Entry(content, font=("Arial", 11))
        self.entry_nome_recebedor.pack(fill='x', pady=(0, 15))

        tk.Label(content, text="CPF do Recebedor (opcional):", bg='white', font=("Arial", 11)).pack(anchor='w', pady=(0, 5))
        self.entry_cpf_recebedor = tk.Entry(content, font=("Arial", 11))
        self.entry_cpf_recebedor.pack(fill='x', pady=(0, 15))

        # ==== VALOR E DESCRIÇÃO ====
        self._create_section_header(content, "💵 Valor e Descrição")

        tk.Label(content, text="Valor (R$):*", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(10, 5))
        self.entry_valor = tk.Entry(content, font=("Arial", 11))
        self.entry_valor.pack(fill='x', pady=(0, 15))

        tk.Label(content, text="Referente a:* (ex: 'Aluguel ref. Janeiro/2025')", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        self.entry_referente = tk.Entry(content, font=("Arial", 11))
        self.entry_referente.pack(fill='x', pady=(0, 15))

        tk.Label(content, text="Descrição Detalhada (opcional):", bg='white', font=("Arial", 11)).pack(anchor='w', pady=(0, 5))
        self.text_descricao = tk.Text(content, font=("Arial", 10), height=3, width=60, wrap='word')
        self.text_descricao.pack(fill='x', pady=(0, 15))

        # ==== DATA E FORMA DE PAGAMENTO ====
        self._create_section_header(content, "📅 Data e Forma de Pagamento")

        tk.Label(content, text="Data do Pagamento:*", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(10, 5))

        if TKCALENDAR_AVAILABLE:
            self.date_pagamento = DateEntry(
                content,
                font=("Arial", 11),
                width=25,
                background='#1565C0',
                foreground='white',
                borderwidth=2,
                date_pattern='dd/mm/yyyy'
            )
        else:
            self.date_pagamento = tk.Entry(content, font=("Arial", 11))
            self.date_pagamento.insert(0, datetime.now().strftime('%d/%m/%Y'))

        self.date_pagamento.pack(fill='x', pady=(0, 15))

        tk.Label(content, text="Forma de Pagamento:", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        self.combo_forma_pag = ttk.Combobox(
            content,
            font=("Arial", 11),
            width=60,
            state='readonly',
            values=['Dinheiro', 'PIX', 'Transferência Bancária', 'Cheque', 'Cartão']
        )
        self.combo_forma_pag.set('Dinheiro')
        self.combo_forma_pag.pack(fill='x', pady=(0, 15))

        # ==== OBSERVAÇÕES ====
        self._create_section_header(content, "📝 Observações")

        tk.Label(content, text="Observações Adicionais (opcional):", bg='white', font=("Arial", 11)).pack(anchor='w', pady=(0, 5))
        self.text_observacoes = tk.Text(content, font=("Arial", 10), height=3, width=60, wrap='word')
        self.text_observacoes.pack(fill='x', pady=(0, 20))

        # ==== BOTÕES ====
        btn_frame = tk.Frame(content, bg='white')
        btn_frame.pack(fill='x', pady=20)

        self.btn_save = tk.Button(
            btn_frame,
            text="💾 Salvar Recibo",
            command=on_save,
            bg='#4CAF50',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            cursor='hand2',
            padx=30,
            pady=12
        )
        self.btn_save.pack(side='left', padx=5)

        self.btn_pdf = tk.Button(
            btn_frame,
            text="📄 Gerar PDF",
            command=on_generate_pdf,
            bg='#2196F3',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            cursor='hand2',
            padx=30,
            pady=12
        )
        self.btn_pdf.pack(side='left', padx=5)

        self.btn_clear = tk.Button(
            btn_frame,
            text="🗑️ Limpar",
            command=on_clear,
            bg='#FF9800',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            cursor='hand2',
            padx=30,
            pady=12
        )
        self.btn_clear.pack(side='left', padx=5)

        # Bind para auto-preencher ao selecionar inquilino
        self.combo_inquilino.bind('<<ComboboxSelected>>', self._on_inquilino_selected)

    def _create_section_header(self, parent, text):
        """Cria um cabeçalho de seção estilizado"""
        tk.Label(
            parent,
            text=text,
            font=("Arial", 13, "bold"),
            bg='white',
            fg='#1565C0'
        ).pack(anchor='w', pady=(10, 10))

    def _on_inquilino_selected(self, event=None):
        """Auto-preenche nome do pagador ao selecionar inquilino"""
        # Este método será configurado na view principal
        pass

    def get_widgets(self):
        """Retorna os campos expostos para manipulação pela view principal."""
        return {
            'combo_tipo': self.combo_tipo,
            'combo_casa': self.combo_casa,
            'combo_inquilino': self.combo_inquilino,
            'entry_nome_pagador': self.entry_nome_pagador,
            'entry_cpf_pagador': self.entry_cpf_pagador,
            'entry_nome_recebedor': self.entry_nome_recebedor,
            'entry_cpf_recebedor': self.entry_cpf_recebedor,
            'entry_valor': self.entry_valor,
            'entry_referente': self.entry_referente,
            'text_descricao': self.text_descricao,
            'date_pagamento': self.date_pagamento,
            'combo_forma_pag': self.combo_forma_pag,
            'text_observacoes': self.text_observacoes,
            'btn_save': self.btn_save,
            'btn_pdf': self.btn_pdf,
            'btn_clear': self.btn_clear,
        }