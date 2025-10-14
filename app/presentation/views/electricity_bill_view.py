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
from app.presentation.views.widgets.header_widget import create_header
from app.presentation.views.widgets.new_bill_form_widget import NewBillForm
from app.presentation.views.widgets.history_list_widget import HistoryList

load_dotenv()


class ElectricityBillView(tk.Frame):
    """Tela de geração de conta de energia (refatorada com widgets)"""

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
        create_header(self, self.controller)

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
        """Cria aba de nova conta usando o widget NewBillForm"""
        # cria o widget de formulário e conecta callbacks para cálculo e ações
        self.new_bill_widget = NewBillForm(
            parent,
            on_casa_selected=self.on_casa_selected,
            on_calc=self.calcular_consumo,
            on_save=self.save_consumo,
            on_generate_pdf=self.gerar_pdf,
            on_clear=self.clear_form,
        )

        # expõe widgets para uso nas funções existentes
        widgets = self.new_bill_widget.get_widgets()
        self.combo_casa = widgets['combo_casa']
        self.combo_mes = widgets['combo_mes']
        self.entry_ano = widgets['entry_ano']
        self.entry_leitura_anterior = widgets['entry_leitura_anterior']
        self.entry_leitura_atual = widgets['entry_leitura_atual']
        self.entry_consumo_geral = widgets['entry_consumo_geral']
        self.entry_valor_total = widgets['entry_valor_total']
        self.lbl_consumo_individual = widgets['lbl_consumo_individual']
        self.lbl_proporcional = widgets['lbl_proporcional']
        self.lbl_valor_individual = widgets['lbl_valor_individual']
    
    def create_history_tab(self, parent):
        # utiliza o widget HistoryList
        self.history_widget = HistoryList(parent, on_filter_change=self.load_history)
        self.filter_casa = self.history_widget.filter_casa
        self.history_canvas = self.history_widget.history_canvas
        self.history_frame = self.history_widget.history_frame
    
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
                "vencimento": f"{5:02d}/{mes+1:02d}/{ano}",
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
        # Limpa frame via widget
        if hasattr(self, 'history_widget'):
            self.history_widget.clear_list()
        else:
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

        # Header and items via history widget
        if hasattr(self, 'history_widget'):
            self.history_widget.create_header()
            view_callbacks = {
                'view': self.view_consumo_detail,
                'reprint': self.reprint_pdf,
                'delete': self.delete_consumo,
            }
            for i, consumo in enumerate(consumos_todos):
                self.history_widget.add_item(consumo, i, view_callbacks)
            return

    # all rendering handled by HistoryList widget
    
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

            mes = consumo.mes
            ano = consumo.ano
            dados_pdf = {
                "logo": None,
                "inquilino": casa.inquilino_atual.nome_completo,
                "endereco": casa.endereco,
                "mes_referencia": f"{meses[mes-1]} / {ano}",
                "vencimento": f"{5:02d}/{mes+1:02d}/{ano}",
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