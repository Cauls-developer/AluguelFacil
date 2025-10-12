import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.data.models.consumption import Consumo
from app.data.repositories.house_repository import CasaRepository
from app.data.repositories.consumption_repository import ConsumoRepository
from app.domain.eletricity_bill.eletricity_bill_entity import EletricityBill
from app.presentation.usecases.generate_pdf_usecase import gerar_conta_inquilino

load_dotenv()

class ElectricityBillView(tk.Frame):
    """Tela de geração de conta de energia"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#f0f0f0')
        self.controller = controller
        self.session = controller.get_session()
        self.casa_repo = CasaRepository(self.session)
        self.consumo_repo = ConsumoRepository(self.session)
        
        # Inicializar variáveis
        self.casas_dict = {}
        
        self.create_widgets()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self, bg='#1565C0')
        header_frame.pack(fill='x')
        
        tk.Label(
            header_frame,
            text="Contas de Energia",
            font=("Arial", 20, "bold"),
            bg='#1565C0',
            fg='white'
        ).pack(pady=15)
        
        tk.Button(
            header_frame,
            text="← Voltar",
            command=lambda: self.controller.show_frame("home"),
            bg='#0D47A1',
            fg='white',
            font=("Arial", 10),
            relief='flat',
            cursor='hand2'
        ).place(x=10, y=10)
        
        # Container principal com abas
        container = tk.Frame(self, bg='#f0f0f0')
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Notebook para abas
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill='both', expand=True)
        
        # Aba 1: Nova Conta
        tab_new = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab_new, text="  📝 Nova Conta  ")
        
        # Aba 2: Histórico
        tab_history = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab_history, text="  📊 Histórico & Reimprimir  ")
        
        # Criar as abas (histórico primeiro para criar filter_casa)
        self.create_history_tab(tab_history)
        self.create_new_bill_tab(tab_new)
        
        # Carregar casas depois que tudo está criado
        self.load_casas()
    
    def create_new_bill_tab(self, parent):
        """Cria aba de nova conta"""
        # Scroll
        canvas = tk.Canvas(parent, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Conteúdo
        content = tk.Frame(scrollable_frame, bg='white')
        content.pack(fill='both', expand=True, padx=40, pady=30)
        
        # Título
        tk.Label(content, text="Registrar Novo Consumo", font=("Arial", 16, "bold"), bg='white', fg='#1565C0').pack(anchor='w', pady=(0, 20))
        
        # Casa
        tk.Label(content, text="Selecione a Casa:*", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(10, 5))
        self.combo_casa = ttk.Combobox(content, font=("Arial", 11), width=60, state='readonly')
        self.combo_casa.pack(fill='x', pady=(0, 15))
        self.combo_casa.bind('<<ComboboxSelected>>', self.on_casa_selected)
        
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
        
        # Separador
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
        self.entry_leitura_atual.bind('<KeyRelease>', self.calcular_consumo)
        
        right_readings = tk.Frame(readings_frame, bg='white')
        right_readings.pack(side='left', fill='x', expand=True)
        
        tk.Label(right_readings, text="Consumo Geral do Local (kWh):*", bg='white', font=("Arial", 11)).pack(anchor='w')
        self.entry_consumo_geral = tk.Entry(right_readings, font=("Arial", 11))
        self.entry_consumo_geral.pack(fill='x', pady=(5, 0))
        self.entry_consumo_geral.bind('<KeyRelease>', self.calcular_consumo)
        
        tk.Label(right_readings, text="Valor Total da Conta (R$):*", bg='white', font=("Arial", 11)).pack(anchor='w', pady=(15, 0))
        self.entry_valor_total = tk.Entry(right_readings, font=("Arial", 11))
        self.entry_valor_total.pack(fill='x', pady=(5, 0))
        self.entry_valor_total.bind('<KeyRelease>', self.calcular_consumo)
        
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
        
        tk.Button(
            btn_frame,
            text="💾 Salvar Consumo",
            command=self.save_consumo,
            bg='#4CAF50',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            cursor='hand2',
            padx=30,
            pady=12
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="📄 Gerar PDF",
            command=self.gerar_pdf,
            bg='#2196F3',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            cursor='hand2',
            padx=30,
            pady=12
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="🗑️ Limpar",
            command=self.clear_form,
            bg='#FF9800',
            fg='white',
            font=("Arial", 12, "bold"),
            relief='flat',
            cursor='hand2',
            padx=30,
            pady=12
        ).pack(side='left', padx=5)
    
    def create_history_tab(self, parent):
        """Cria aba de histórico"""
        container = tk.Frame(parent, bg='white')
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(container, text="Histórico de Contas", font=("Arial", 16, "bold"), bg='white', fg='#1565C0').pack(anchor='w', pady=(0, 15))
        
        # Filtros
        filter_frame = tk.Frame(container, bg='#F5F5F5', relief='solid', borderwidth=1)
        filter_frame.pack(fill='x', pady=(0, 15))
        
        filter_content = tk.Frame(filter_frame, bg='#F5F5F5')
        filter_content.pack(fill='x', padx=15, pady=15)
        
        tk.Label(filter_content, text="Filtrar por Casa:", bg='#F5F5F5', font=("Arial", 10)).pack(side='left', padx=(0, 10))
        self.filter_casa = ttk.Combobox(filter_content, font=("Arial", 10), width=40, state='readonly')
        self.filter_casa.pack(side='left', padx=5)
        self.filter_casa.bind('<<ComboboxSelected>>', lambda e: self.load_history())
        
        tk.Button(
            filter_content,
            text="🔄 Atualizar",
            command=self.load_history,
            bg='#2196F3',
            fg='white',
            font=("Arial", 10),
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=5
        ).pack(side='left', padx=10)
        
        # Lista com scroll
        list_container = tk.Frame(container, bg='white', relief='solid', borderwidth=1)
        list_container.pack(fill='both', expand=True)
        
        # Canvas
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
        
        # Carregar histórico
        # Não carrega automaticamente, só quando load_casas() for chamado
    
    def load_casas(self):
        """Carrega casas nos comboboxes"""
        casas = self.casa_repo.get_all()
        self.casas_dict = {f"{c.nome} - {c.endereco}": c for c in casas}
        
        # Combo da nova conta
        if hasattr(self, 'combo_casa'):
            self.combo_casa['values'] = list(self.casas_dict.keys())
        
        # Combo do filtro
        if hasattr(self, 'filter_casa'):
            self.filter_casa['values'] = ['Todas'] + list(self.casas_dict.keys())
            self.filter_casa.set('Todas')
            # Agora carrega o histórico
            self.load_history()
    
    def on_casa_selected(self, event):
        """Quando uma casa é selecionada"""
        casa_selecionada = self.combo_casa.get()
        if casa_selecionada:
            casa = self.casas_dict[casa_selecionada]
            
            # Preenche leitura anterior com último consumo
            ultimo = self.consumo_repo.get_ultimo_consumo(casa.id)
            if ultimo:
                self.entry_leitura_anterior.delete(0, 'end')
                self.entry_leitura_anterior.insert(0, str(ultimo.consumo_mes_atual))
    
    def calcular_consumo(self, event=None):
        """Calcula automaticamente os valores"""
        try:
            leitura_ant = float(self.entry_leitura_anterior.get() or 0)
            leitura_atual = float(self.entry_leitura_atual.get() or 0)
            consumo_geral = float(self.entry_consumo_geral.get() or 0)
            valor_total = float(self.entry_valor_total.get() or 0)
            
            if leitura_atual > 0 and consumo_geral > 0 and valor_total > 0:
                calc = EletricityBill(leitura_ant, leitura_atual, consumo_geral, valor_total)
                
                self.lbl_consumo_individual.config(text=f"Consumo Individual: {calc.personalConsumption:.2f} kWh")
                self.lbl_proporcional.config(text=f"Percentual: {calc.personalproportionalConsumption:.2f}%")
                self.lbl_valor_individual.config(text=f"Valor a Pagar: R$ {calc.personalcost:.2f}")
        except ValueError:
            pass
    
    def save_consumo(self):
        """Salva o consumo no banco de dados"""
        casa_selecionada = self.combo_casa.get()
        if not casa_selecionada:
            messagebox.showerror("Erro", "Selecione uma casa!")
            return
        
        try:
            casa = self.casas_dict[casa_selecionada]
            mes = self.combo_mes.current() + 1
            ano = int(self.entry_ano.get())
            leitura_ant = float(self.entry_leitura_anterior.get())
            leitura_atual = float(self.entry_leitura_atual.get())
            consumo_geral = float(self.entry_consumo_geral.get())
            valor_total = float(self.entry_valor_total.get())
            
            calc = EletricityBill(leitura_ant, leitura_atual, consumo_geral, valor_total)
            
            consumo_existente = self.consumo_repo.get_by_casa_e_periodo(casa.id, mes, ano)
            
            if consumo_existente:
                if not messagebox.askyesno("Confirmar", "Já existe um consumo para este período. Deseja atualizar?"):
                    return
                consumo_existente.consumo_mes_anterior = leitura_ant
                consumo_existente.consumo_mes_atual = leitura_atual
                consumo_existente.valor_conta = valor_total
                consumo_existente.consumo_individual_proporcional = calc.personalcost
                self.consumo_repo.update(consumo_existente)
            else:
                novo_consumo = Consumo(
                    casa_id=casa.id,
                    mes=mes,
                    ano=ano,
                    consumo_mes_anterior=leitura_ant,
                    consumo_mes_atual=leitura_atual,
                    valor_conta=valor_total,
                    consumo_individual_proporcional=calc.personalcost
                )
                self.consumo_repo.create(novo_consumo)
            
            messagebox.showinfo("Sucesso", "Consumo salvo com sucesso!")
            self.load_history()
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro nos dados: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
    
    def gerar_pdf(self):
        """Gera o PDF da conta de energia"""
        casa_selecionada = self.combo_casa.get()
        if not casa_selecionada:
            messagebox.showerror("Erro", "Selecione uma casa!")
            return
        
        try:
            casa = self.casas_dict[casa_selecionada]
            
            if not casa.inquilino_atual:
                messagebox.showerror("Erro", "Esta casa não possui inquilino!")
                return
            
            mes = self.combo_mes.current() + 1
            ano = int(self.entry_ano.get())
            leitura_ant = float(self.entry_leitura_anterior.get())
            leitura_atual = float(self.entry_leitura_atual.get())
            valor_total = float(self.entry_valor_total.get())
            consumo_geral = float(self.entry_consumo_geral.get())
            
            calc = EletricityBill(leitura_ant, leitura_atual, consumo_geral, valor_total)
            
            # Histórico
            historico_consumos = self.consumo_repo.get_consumos_por_casa(casa.id)
            historico_lista = []
            for h in historico_consumos[-6:]:
                historico_lista.append({
                    'mes': f"{h.mes:02d}/{h.ano}",
                    'valor': h.consumo_diferenca
                })
            
            dados_pdf = {
                "logo": None,
                "inquilino": casa.inquilino_atual.nome_completo,
                "endereco": casa.endereco,
                "mes_referencia": f"{self.combo_mes.get()} / {ano}",
                "vencimento": "15/03/2025",
                "leituras": [
                    {"data": "Anterior", "leitura": leitura_ant},
                    {"data": "Atual", "leitura": leitura_atual}
                ],
                "consumo_total": calc.personalConsumption,
                "itens_financeiros": [
                    ["Energia Elétrica", f"{calc.personalcost:.2f}"],
                ],
                "total": calc.personalcost,
                "banco": "Mercado Pago LTDA",
                "titular_pix": "Lucas Diego Santos da Silva",
                "chave_pix": "(71) 99999-9999",
                "historico_consumo": historico_lista if historico_lista else [
                    {"mes": f"{mes:02d}/{ano}", "valor": calc.personalConsumption}
                ],
            }
            
            arquivo = gerar_conta_inquilino(dados_pdf)
            messagebox.showinfo("Sucesso", f"PDF gerado com sucesso!\n{arquivo}")
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro nos dados: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {str(e)}")
    
    def clear_form(self):
        """Limpa o formulário"""
        self.combo_casa.set('')
        self.entry_leitura_anterior.delete(0, 'end')
        self.entry_leitura_atual.delete(0, 'end')
        self.entry_consumo_geral.delete(0, 'end')
        self.entry_valor_total.delete(0, 'end')
        self.lbl_consumo_individual.config(text="Consumo Individual: - kWh")
        self.lbl_proporcional.config(text="Percentual: - %")
        self.lbl_valor_individual.config(text="Valor a Pagar: R$ 0,00")
    
    def load_history(self):
        """Carrega histórico de consumos"""
        # Limpa frame
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        # Filtra por casa se selecionada
        filter_value = self.filter_casa.get()
        
        if filter_value == 'Todas':
            casas = self.casa_repo.get_all()
            consumos_todos = []
            for casa in casas:
                consumos = self.consumo_repo.get_consumos_por_casa(casa.id)
                for c in consumos:
                    c.casa_obj = casa
                    consumos_todos.append(c)
            consumos_todos.sort(key=lambda x: (x.ano, x.mes), reverse=True)
        else:
            casa = self.casas_dict.get(filter_value)
            if casa:
                consumos_todos = self.consumo_repo.get_consumos_por_casa(casa.id)
                for c in consumos_todos:
                    c.casa_obj = casa
            else:
                consumos_todos = []
        
        if not consumos_todos:
            tk.Label(
                self.history_frame,
                text="Nenhum registro encontrado",
                font=("Arial", 12),
                bg='white',
                fg='gray'
            ).pack(pady=50)
            return
        
        # Header
        header = tk.Frame(self.history_frame, bg='#E3F2FD', height=40)
        header.pack(fill='x', padx=10, pady=(10, 0))
        
        tk.Label(header, text="Período", bg='#E3F2FD', font=("Arial", 10, "bold"), width=12, anchor='center').pack(side='left', padx=5)
        tk.Label(header, text="Casa", bg='#E3F2FD', font=("Arial", 10, "bold"), width=20, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="Inquilino", bg='#E3F2FD', font=("Arial", 10, "bold"), width=20, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="Consumo", bg='#E3F2FD', font=("Arial", 10, "bold"), width=10, anchor='center').pack(side='left', padx=5)
        tk.Label(header, text="Valor", bg='#E3F2FD', font=("Arial", 10, "bold"), width=12, anchor='center').pack(side='left', padx=5)
        tk.Label(header, text="Ações", bg='#E3F2FD', font=("Arial", 10, "bold"), width=20, anchor='center').pack(side='left', padx=5)
        
        # Items
        for i, consumo in enumerate(consumos_todos):
            self.create_history_item(consumo, i)
    
    def create_history_item(self, consumo, index):
        """Cria item do histórico"""
        bg_color = '#FFFFFF' if index % 2 == 0 else '#F5F5F5'
        
        item_frame = tk.Frame(self.history_frame, bg=bg_color, relief='solid', borderwidth=1)
        item_frame.pack(fill='x', padx=10, pady=2)
        
        # Período
        periodo = f"{consumo.mes:02d}/{consumo.ano}"
        tk.Label(item_frame, text=periodo, bg=bg_color, font=("Arial", 10, "bold"), width=12, anchor='center').pack(side='left', padx=5, pady=10)
        
        # Casa
        casa_nome = consumo.casa_obj.nome if hasattr(consumo, 'casa_obj') else consumo.casa.nome
        tk.Label(item_frame, text=casa_nome, bg=bg_color, font=("Arial", 10), width=20, anchor='w').pack(side='left', padx=5)
        
        # Inquilino
        inquilino_nome = "-"
        if hasattr(consumo, 'casa_obj') and consumo.casa_obj.inquilino_atual:
            inquilino_nome = consumo.casa_obj.inquilino_atual.nome_completo[:20]
        elif consumo.casa.inquilino_atual:
            inquilino_nome = consumo.casa.inquilino_atual.nome_completo[:20]
        tk.Label(item_frame, text=inquilino_nome, bg=bg_color, font=("Arial", 10), width=20, anchor='w').pack(side='left', padx=5)
        
        # Consumo
        consumo_valor = consumo.consumo_diferenca
        tk.Label(item_frame, text=f"{consumo_valor:.1f} kWh", bg=bg_color, font=("Arial", 10), width=10, anchor='center').pack(side='left', padx=5)
        
        # Valor
        valor = consumo.consumo_individual_proporcional if consumo.consumo_individual_proporcional else 0
        tk.Label(item_frame, text=f"R$ {valor:.2f}", bg=bg_color, font=("Arial", 10, "bold"), fg='#2E7D32', width=12, anchor='center').pack(side='left', padx=5)
        
        # Botões
        action_frame = tk.Frame(item_frame, bg=bg_color)
        action_frame.pack(side='left', padx=5)
        
        tk.Button(
            action_frame,
            text="👁️ Ver",
            command=lambda: self.view_consumo_detail(consumo),
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
            command=lambda: self.reprint_pdf(consumo),
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
            command=lambda: self.delete_consumo(consumo.id),
            bg='#F44336',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            cursor='hand2',
            padx=8,
            pady=5
        ).pack(side='left', padx=2)
    
    def view_consumo_detail(self, consumo):
        """Visualiza detalhes do consumo"""
        dialog = tk.Toplevel(self)
        dialog.title("Detalhes do Consumo")
        dialog.geometry("500x550")
        dialog.configure(bg='white')
        dialog.transient(self)
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (550 // 2)
        dialog.geometry(f"500x550+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg='#9C27B0')
        header.pack(fill='x')
        tk.Label(header, text="📊 Detalhes do Consumo", font=("Arial", 16, "bold"), bg='#9C27B0', fg='white').pack(pady=15)
        
        # Content
        content = tk.Frame(dialog, bg='white')
        content.pack(fill='both', expand=True, padx=30, pady=20)
        
        def add_field(label, value):
            tk.Label(content, text=label, bg='white', font=("Arial", 10, "bold"), fg='#666').pack(anchor='w', pady=(10, 2))
            tk.Label(content, text=value, bg='#F5F5F5', font=("Arial", 11), relief='solid', borderwidth=1, anchor='w', padx=10, pady=8).pack(fill='x')
        
        casa = consumo.casa_obj if hasattr(consumo, 'casa_obj') else consumo.casa
        inquilino = casa.inquilino_atual.nome_completo if casa.inquilino_atual else "Sem inquilino"
        
        add_field("Período:", f"{consumo.mes:02d}/{consumo.ano}")
        add_field("Casa:", casa.nome)
        add_field("Endereço:", casa.endereco)
        add_field("Inquilino:", inquilino)
        add_field("Leitura Anterior:", f"{consumo.consumo_mes_anterior:.2f} kWh")
        add_field("Leitura Atual:", f"{consumo.consumo_mes_atual:.2f} kWh")
        add_field("Consumo Total:", f"{consumo.consumo_diferenca:.2f} kWh")
        add_field("Valor da Conta:", f"R$ {consumo.valor_conta:.2f}")
        add_field("Valor Individual:", f"R$ {consumo.consumo_individual_proporcional:.2f}" if consumo.consumo_individual_proporcional else "R$ 0,00")
        
        # Botão fechar
        tk.Button(
            dialog,
            text="✖️ Fechar",
            command=dialog.destroy,
            bg='#9E9E9E',
            fg='white',
            font=("Arial", 11, "bold"),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10
        ).pack(pady=20)
    
    def reprint_pdf(self, consumo):
        """Reimprime PDF de um consumo antigo"""
        try:
            casa = consumo.casa_obj if hasattr(consumo, 'casa_obj') else consumo.casa
            
            if not casa.inquilino_atual:
                messagebox.showerror("Erro", "Esta casa não possui inquilino!")
                return
            
            # Recalcula os valores
            calc = EletricityBill(
                consumo.consumo_mes_anterior,
                consumo.consumo_mes_atual,
                consumo.consumo_diferenca,  # Usando diferença como consumo geral aproximado
                consumo.valor_conta
            )
            
            # Histórico
            historico_consumos = self.consumo_repo.get_consumos_por_casa(casa.id)
            historico_lista = []
            for h in historico_consumos[-6:]:
                historico_lista.append({
                    'mes': f"{h.mes:02d}/{h.ano}",
                    'valor': h.consumo_diferenca
                })
            
            meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                     'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            
            titular_pix = os.getenv("TITULAR_CONTA", "Seu Nome Aqui")
            chave_pix = os.getenv("PIX", "sua-chave-aqui")
            banco = os.getenv("BANCO", "Seu Banco Aqui")

            dados_pdf = {
                "logo": None,
                "inquilino": casa.inquilino_atual.nome_completo,
                "endereco": casa.endereco,
                "mes_referencia": f"{meses[consumo.mes-1]} / {consumo.ano}",
                "vencimento": "15/03/2025",
                "leituras": [
                    {"data": "Anterior", "leitura": consumo.consumo_mes_anterior},
                    {"data": "Atual", "leitura": consumo.consumo_mes_atual}
                ],
                "consumo_total": consumo.consumo_diferenca,
                "itens_financeiros": [
                    ["Energia Elétrica", f"{consumo.consumo_individual_proporcional:.2f}" if consumo.consumo_individual_proporcional else "0.00"],
                ],
                "total": consumo.consumo_individual_proporcional if consumo.consumo_individual_proporcional else 0,
                "banco": banco,
                "titular_pix": titular_pix,
                "chave_pix": chave_pix,
                "historico_consumo": historico_lista,
            }
            
            arquivo = gerar_conta_inquilino(dados_pdf)
            messagebox.showinfo("Sucesso", f"PDF reimpresso com sucesso!\n{arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {str(e)}")
    
    def delete_consumo(self, consumo_id):
        """Exclui um registro de consumo"""
        if messagebox.askyesno("Confirmar Exclusão", "Deseja realmente excluir este registro?\n\nEsta ação não pode ser desfeita."):
            try:
                self.consumo_repo.delete(consumo_id)
                messagebox.showinfo("Sucesso", "Registro excluído!")
                self.load_history()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {str(e)}")