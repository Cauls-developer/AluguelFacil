import tkinter as tk
from tkinter import ttk
from datetime import datetime

class NewBillForm:
    """Widget que encapsula o formulário de nova conta."""

    def __init__(self, parent, on_casa_selected=None, on_calc=None,
                 on_save=None, on_generate_pdf=None, on_clear=None):
        # cria estrutura com canvas para scroll
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

        tk.Label(content, text="Registrar Novo Consumo", font=("Arial", 16, "bold"), bg='white', fg='#1565C0').pack(anchor='w', pady=(0, 20))

        # Casa
        tk.Label(content, text="Selecione a Casa:*", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(10, 5))
        self.combo_casa = ttk.Combobox(content, font=("Arial", 11), width=60, state='readonly')
        self.combo_casa.pack(fill='x', pady=(0, 15))
        if on_casa_selected:
            self.combo_casa.bind('<<ComboboxSelected>>', on_casa_selected)

        # Período
        period_frame = tk.Frame(content, bg='white')
        period_frame.pack(fill='x', pady=(0, 15))

        mes_frame = tk.Frame(period_frame, bg='white')
        mes_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        tk.Label(mes_frame, text="Mês:*", bg='white', font=("Arial", 11, "bold")).pack(anchor='w')
        self.combo_mes = ttk.Combobox(mes_frame, font=("Arial", 11), state='readonly',
                                       values=['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                                              'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'])
        self.combo_mes.current(datetime.now().month - 1)
        self.combo_mes.pack(fill='x')

        ano_frame = tk.Frame(period_frame, bg='white')
        ano_frame.pack(side='left', fill='x', expand=True)
        tk.Label(ano_frame, text="Ano:*", bg='white', font=("Arial", 11, "bold")).pack(anchor='w')
        self.entry_ano = tk.Entry(ano_frame, font=("Arial", 11))
        self.entry_ano.insert(0, str(datetime.now().year))
        self.entry_ano.pack(fill='x')

        ttk.Separator(content, orient='horizontal').pack(fill='x', pady=20)

        # Leituras
        tk.Label(content, text="Leituras do Medidor", font=("Arial", 14, "bold"), bg='white', fg='#1565C0').pack(anchor='w', pady=(0, 15))

        readings_frame = tk.Frame(content, bg='white')
        readings_frame.pack(fill='x', pady=(0, 15))

        left_readings = tk.Frame(readings_frame, bg='white')
        left_readings.pack(side='left', fill='x', expand=True, padx=(0, 10))

        tk.Label(left_readings, text="Leitura Anterior (kWh):*", bg='white', font=("Arial", 11)).pack(anchor='w')
        self.entry_leitura_anterior = tk.Entry(left_readings, font=("Arial", 11))
        self.entry_leitura_anterior.pack(fill='x', pady=(5, 0))

        tk.Label(left_readings, text="Leitura Atual (kWh):*", bg='white', font=("Arial", 11)).pack(anchor='w', pady=(15, 0))
        self.entry_leitura_atual = tk.Entry(left_readings, font=("Arial", 11))
        self.entry_leitura_atual.pack(fill='x', pady=(5, 0))
        if on_calc:
            self.entry_leitura_atual.bind('<KeyRelease>', on_calc)

        right_readings = tk.Frame(readings_frame, bg='white')
        right_readings.pack(side='left', fill='x', expand=True)

        tk.Label(right_readings, text="Consumo Geral do Local (kWh):*", bg='white', font=("Arial", 11)).pack(anchor='w')
        self.entry_consumo_geral = tk.Entry(right_readings, font=("Arial", 11))
        self.entry_consumo_geral.pack(fill='x', pady=(5, 0))
        if on_calc:
            self.entry_consumo_geral.bind('<KeyRelease>', on_calc)

        tk.Label(right_readings, text="Valor Total da Conta (R$):*", bg='white', font=("Arial", 11)).pack(anchor='w', pady=(15, 0))
        self.entry_valor_total = tk.Entry(right_readings, font=("Arial", 11))
        self.entry_valor_total.pack(fill='x', pady=(5, 0))
        if on_calc:
            self.entry_valor_total.bind('<KeyRelease>', on_calc)

        # Cálculos
        calc_frame = tk.LabelFrame(content, text="  💡 Cálculo Automático  ", bg='#E8F5E9', font=("Arial", 12, "bold"), fg='#2E7D32')
        calc_frame.pack(fill='x', pady=20)

        calc_content = tk.Frame(calc_frame, bg='#E8F5E9')
        calc_content.pack(fill='x', padx=20, pady=15)

        self.lbl_consumo_individual = tk.Label(calc_content, text="Consumo Individual: - kWh", bg='#E8F5E9', font=("Arial", 12))
        self.lbl_consumo_individual.pack(anchor='w', pady=3)

        self.lbl_proporcional = tk.Label(calc_content, text="Percentual: - %", bg='#E8F5E9', font=("Arial", 12))
        self.lbl_proporcional.pack(anchor='w', pady=3)

        self.lbl_valor_individual = tk.Label(calc_content, text="Valor a Pagar: R$ 0,00", bg='#E8F5E9', font=("Arial", 14, "bold"), fg='#d32f2f')
        self.lbl_valor_individual.pack(anchor='w', pady=3)

        # Botões
        btn_frame = tk.Frame(content, bg='white')
        btn_frame.pack(fill='x', pady=20)

        self.btn_save = tk.Button(
            btn_frame,
            text="💾 Salvar Consumo",
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

    def get_widgets(self):
        """Retorna os campos expostos para manipulação pela view principal."""
        return {
            'combo_casa': self.combo_casa,
            'combo_mes': self.combo_mes,
            'entry_ano': self.entry_ano,
            'entry_leitura_anterior': self.entry_leitura_anterior,
            'entry_leitura_atual': self.entry_leitura_atual,
            'entry_consumo_geral': self.entry_consumo_geral,
            'entry_valor_total': self.entry_valor_total,
            'lbl_consumo_individual': self.lbl_consumo_individual,
            'lbl_proporcional': self.lbl_proporcional,
            'lbl_valor_individual': self.lbl_valor_individual,
            'btn_save': self.btn_save,
            'btn_pdf': self.btn_pdf,
            'btn_clear': self.btn_clear,
        }
