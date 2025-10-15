import tkinter as tk
from tkinter import ttk
from datetime import datetime
try:
    from tkcalendar import DateEntry
    TKCALENDAR_AVAILABLE = True
except ImportError:
    TKCALENDAR_AVAILABLE = False
    print("Warning: tkcalendar not available. Install with: pip install tkcalendar")

try:
    from dateutil.relativedelta import relativedelta
    DATEUTIL_AVAILABLE = True
except ImportError:
    DATEUTIL_AVAILABLE = False
    print("Warning: dateutil not available. Install with: pip install python-dateutil")


class NewContractForm:
    """Widget que encapsula o formulário de novo contrato."""

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
            text="Registrar Novo Contrato de Locação", 
            font=("Arial", 16, "bold"), 
            bg='white', 
            fg='#1565C0'
        ).pack(anchor='w', pady=(0, 20))

        # ==== SEÇÃO: PARTES DO CONTRATO ====
        self._create_section_header(content, "📋 Partes do Contrato")
        
        # Casa
        tk.Label(content, text="Selecione a Casa:*", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(10, 5))
        self.combo_casa = ttk.Combobox(content, font=("Arial", 11), width=60, state='readonly')
        self.combo_casa.pack(fill='x', pady=(0, 15))

        # Inquilino
        tk.Label(content, text="Selecione o Inquilino:*", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        self.combo_inquilino = ttk.Combobox(content, font=("Arial", 11), width=60, state='readonly')
        self.combo_inquilino.pack(fill='x', pady=(0, 15))

        ttk.Separator(content, orient='horizontal').pack(fill='x', pady=20)

        # ==== SEÇÃO: VALORES ====
        self._create_section_header(content, "💰 Valores e Pagamento")

        valores_frame = tk.Frame(content, bg='white')
        valores_frame.pack(fill='x', pady=(0, 15))

        # Valor do Aluguel
        left_valores = tk.Frame(valores_frame, bg='white')
        left_valores.pack(side='left', fill='x', expand=True, padx=(0, 10))

        tk.Label(left_valores, text="Valor do Aluguel (R$):*", bg='white', font=("Arial", 11)).pack(anchor='w')
        self.entry_valor_aluguel = tk.Entry(left_valores, font=("Arial", 11))
        self.entry_valor_aluguel.pack(fill='x', pady=(5, 0))
        
        # Bind para calcular caução e seguro fiança automaticamente
        self.entry_valor_aluguel.bind('<KeyRelease>', self.calcular_garantias_automatico)

        # Dia de Pagamento
        right_valores = tk.Frame(valores_frame, bg='white')
        right_valores.pack(side='left', fill='x', expand=True)

        tk.Label(right_valores, text="Dia do Pagamento (1-31):*", bg='white', font=("Arial", 11)).pack(anchor='w')
        self.entry_dia_pagamento = tk.Entry(right_valores, font=("Arial", 11))
        self.entry_dia_pagamento.insert(0, "25")
        self.entry_dia_pagamento.pack(fill='x', pady=(5, 0))

        # Garantias
        garantias_frame = tk.Frame(content, bg='white')
        garantias_frame.pack(fill='x', pady=(15, 15))

        left_garantias = tk.Frame(garantias_frame, bg='white')
        left_garantias.pack(side='left', fill='x', expand=True, padx=(0, 10))

        tk.Label(left_garantias, text="Valor da Caução (R$): (1 mês de aluguel)", bg='white', font=("Arial", 11)).pack(anchor='w')
        self.entry_caucao = tk.Entry(left_garantias, font=("Arial", 11))
        self.entry_caucao.pack(fill='x', pady=(5, 0))

        right_garantias = tk.Frame(garantias_frame, bg='white')
        right_garantias.pack(side='left', fill='x', expand=True)

        tk.Label(right_garantias, text="Valor Seguro Fiança (R$): (1 mês de aluguel)", bg='white', font=("Arial", 11)).pack(anchor='w')
        self.entry_seguro_fianca = tk.Entry(right_garantias, font=("Arial", 11))
        self.entry_seguro_fianca.pack(fill='x', pady=(5, 0))

        ttk.Separator(content, orient='horizontal').pack(fill='x', pady=20)

        # ==== SEÇÃO: DATAS E DURAÇÃO ====
        self._create_section_header(content, "📅 Período do Contrato")

        datas_frame = tk.Frame(content, bg='white')
        datas_frame.pack(fill='x', pady=(0, 15))

        # Data de Início
        left_datas = tk.Frame(datas_frame, bg='white')
        left_datas.pack(side='left', fill='x', expand=True, padx=(0, 10))

        tk.Label(left_datas, text="Data de Início:*", bg='white', font=("Arial", 11)).pack(anchor='w')
        
        if TKCALENDAR_AVAILABLE:
            self.date_inicio = DateEntry(
                left_datas, 
                font=("Arial", 11),
                width=25,
                background='#1565C0',
                foreground='white',
                borderwidth=2,
                date_pattern='dd/mm/yyyy'
            )
        else:
            self.date_inicio = tk.Entry(left_datas, font=("Arial", 11))
            self.date_inicio.insert(0, datetime.now().strftime('%d/%m/%Y'))
        
        self.date_inicio.pack(fill='x', pady=(5, 0))

        # Data de Fim
        right_datas = tk.Frame(datas_frame, bg='white')
        right_datas.pack(side='left', fill='x', expand=True)

        tk.Label(right_datas, text="Data de Fim:*", bg='white', font=("Arial", 11)).pack(anchor='w')
        
        if TKCALENDAR_AVAILABLE:
            self.date_fim = DateEntry(
                right_datas,
                font=("Arial", 11),
                width=25,
                background='#1565C0',
                foreground='white',
                borderwidth=2,
                date_pattern='dd/mm/yyyy'
            )
        else:
            self.date_fim = tk.Entry(right_datas, font=("Arial", 11))
            self.date_fim.insert(0, datetime.now().strftime('%d/%m/%Y'))
        
        self.date_fim.pack(fill='x', pady=(5, 0))

        # Duração em meses
        duracao_frame = tk.Frame(content, bg='white')
        duracao_frame.pack(fill='x', pady=(15, 15))

        tk.Label(duracao_frame, text="Duração (meses):*", bg='white', font=("Arial", 11)).pack(anchor='w')
        self.entry_duracao = tk.Entry(duracao_frame, font=("Arial", 11), width=20)
        self.entry_duracao.insert(0, "12")
        self.entry_duracao.pack(anchor='w', pady=(5, 0))
        
        # Bind para calcular data fim automaticamente
        self.entry_duracao.bind('<KeyRelease>', self.calcular_data_fim_automatico)
        if TKCALENDAR_AVAILABLE:
            self.date_inicio.bind('<<DateEntrySelected>>', self.calcular_data_fim_automatico)
        
        # Calcular data fim inicial
        self.calcular_data_fim_automatico()

        ttk.Separator(content, orient='horizontal').pack(fill='x', pady=20)

        # ==== SEÇÃO: MULTAS E TAXAS ====
        self._create_section_header(content, "⚖️ Multas e Taxas")

        multas_frame = tk.Frame(content, bg='white')
        multas_frame.pack(fill='x', pady=(0, 15))

        # Multa por Atraso
        left_multas = tk.Frame(multas_frame, bg='white')
        left_multas.pack(side='left', fill='x', expand=True, padx=(0, 10))

        tk.Label(left_multas, text="Multa por Atraso (%):", bg='white', font=("Arial", 11)).pack(anchor='w')
        self.entry_multa_atraso = tk.Entry(left_multas, font=("Arial", 11))
        self.entry_multa_atraso.insert(0, "10.0")
        self.entry_multa_atraso.pack(fill='x', pady=(5, 0))

        # Juros por Dia
        right_multas = tk.Frame(multas_frame, bg='white')
        right_multas.pack(side='left', fill='x', expand=True)

        tk.Label(right_multas, text="Juros ao Dia (%):", bg='white', font=("Arial", 11)).pack(anchor='w')
        self.entry_juros_dia = tk.Entry(right_multas, font=("Arial", 11))
        self.entry_juros_dia.insert(0, "0.33")
        self.entry_juros_dia.pack(fill='x', pady=(5, 0))

        # Multa Rescisão
        rescisao_frame = tk.Frame(content, bg='white')
        rescisao_frame.pack(fill='x', pady=(15, 15))

        tk.Label(rescisao_frame, text="Multa por Rescisão Antecipada (meses de aluguel):", bg='white', font=("Arial", 11)).pack(anchor='w')
        self.entry_multa_rescisao = tk.Entry(rescisao_frame, font=("Arial", 11), width=20)
        self.entry_multa_rescisao.insert(0, "3")
        self.entry_multa_rescisao.pack(anchor='w', pady=(5, 0))

        ttk.Separator(content, orient='horizontal').pack(fill='x', pady=20)

        # ==== SEÇÃO: OBSERVAÇÕES ====
        self._create_section_header(content, "📝 Observações")

        tk.Label(content, text="Observações Adicionais (opcional):", bg='white', font=("Arial", 11)).pack(anchor='w', pady=(0, 5))
        self.text_observacoes = tk.Text(content, font=("Arial", 10), height=4, width=60, wrap='word')
        self.text_observacoes.pack(fill='x', pady=(0, 20))

        # ==== BOTÕES ====
        btn_frame = tk.Frame(content, bg='white')
        btn_frame.pack(fill='x', pady=20)

        self.btn_save = tk.Button(
            btn_frame,
            text="💾 Salvar Contrato",
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
            text="📄 Gerar PDF do Contrato",
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

    def _create_section_header(self, parent, text):
        """Cria um cabeçalho de seção estilizado"""
        tk.Label(
            parent, 
            text=text, 
            font=("Arial", 13, "bold"), 
            bg='white', 
            fg='#1565C0'
        ).pack(anchor='w', pady=(10, 10))
    
    def calcular_garantias_automatico(self, event=None):
        """Calcula automaticamente caução e seguro fiança baseado no valor do aluguel"""
        try:
            valor_aluguel_str = self.entry_valor_aluguel.get().strip()
            if not valor_aluguel_str:
                return
            
            # Remove caracteres não numéricos exceto ponto e vírgula
            valor_aluguel_str = valor_aluguel_str.replace(',', '.')
            valor_aluguel = float(valor_aluguel_str)
            
            # Cada um vale 1 mês de aluguel
            self.entry_caucao.delete(0, 'end')
            self.entry_caucao.insert(0, f"{valor_aluguel:.2f}")
            
            self.entry_seguro_fianca.delete(0, 'end')
            self.entry_seguro_fianca.insert(0, f"{valor_aluguel:.2f}")
            
        except ValueError:
            # Ignora erros de conversão
            pass
    
    def calcular_data_fim_automatico(self, event=None):
        """Calcula automaticamente a data de fim baseada na data de início e duração"""
        if not DATEUTIL_AVAILABLE or not TKCALENDAR_AVAILABLE:
            return
        
        try:
            duracao_str = self.entry_duracao.get().strip()
            if not duracao_str:
                return
            
            duracao_meses = int(duracao_str)
            data_inicio = self.date_inicio.get_date()
            
            # Calcula a data de fim
            data_fim = data_inicio + relativedelta(months=duracao_meses)
            
            # Atualiza o DateEntry de data fim
            self.date_fim.set_date(data_fim)
            
        except (ValueError, AttributeError) as e:
            # Ignora erros de conversão ou se os widgets ainda não existirem
            pass
    
    def get_widgets(self):
        """Retorna os campos expostos para manipulação pela view principal."""
        return {
            'combo_casa': self.combo_casa,
            'combo_inquilino': self.combo_inquilino,
            'entry_valor_aluguel': self.entry_valor_aluguel,
            'entry_dia_pagamento': self.entry_dia_pagamento,
            'entry_caucao': self.entry_caucao,
            'entry_seguro_fianca': self.entry_seguro_fianca,
            'date_inicio': self.date_inicio,
            'date_fim': self.date_fim,
            'entry_duracao': self.entry_duracao,
            'entry_multa_atraso': self.entry_multa_atraso,
            'entry_juros_dia': self.entry_juros_dia,
            'entry_multa_rescisao': self.entry_multa_rescisao,
            'text_observacoes': self.text_observacoes,
            'btn_save': self.btn_save,
            'btn_pdf': self.btn_pdf,
            'btn_clear': self.btn_clear,
        }