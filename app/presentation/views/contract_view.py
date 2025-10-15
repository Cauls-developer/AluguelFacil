import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    # Fallback se dateutil não estiver instalado
    def relativedelta(months=0):
        return timedelta(days=30*months)

from app.data.models.contract import Contrato
from app.data.repositories.contract_repository import ContratoRepository
from app.data.repositories.house_repository import CasaRepository
from app.data.repositories.tenant_repository import InquilinoRepository
from app.presentation.usecases.generate_contract_pdf_usecase import gerar_contrato_locacao
from app.presentation.views.widgets.header_widget import create_header
from app.presentation.views.widgets.new_contract_form_widget import NewContractForm
from app.presentation.views.widgets.contract_list_widget import ContractListWidget

load_dotenv()


class ContractView(tk.Frame):
    """Tela de gerenciamento de contratos de locação"""

    def __init__(self, parent, controller):
        super().__init__(parent, bg='#f0f0f0')
        self.controller = controller
        self.session = controller.get_session()
        self.contrato_repo = ContratoRepository(self.session)
        self.casa_repo = CasaRepository(self.session)
        self.inquilino_repo = InquilinoRepository(self.session)

        # Dicionários para mapear seleções
        self.casas_dict = {}
        self.inquilinos_dict = {}

        self.create_widgets()
    
    def create_widgets(self):
        # Header
        create_header(self, self.controller, title="Gerenciamento de Contratos")

        # Container principal com abas
        container = tk.Frame(self, bg='#f0f0f0')
        container.pack(fill='both', expand=True, padx=20, pady=20)

        # Notebook para abas
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill='both', expand=True)

        # Aba 1: Novo Contrato
        tab_new = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab_new, text="  📝 Novo Contrato  ")

        # Aba 2: Lista de Contratos
        tab_list = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab_list, text="  📋 Contratos Cadastrados  ")

        # Criar as abas
        self.create_new_contract_tab(tab_new)
        self.create_list_tab(tab_list)

        # Carregar dados
        self.load_casas()
        self.load_inquilinos()
        self.load_contratos()
    
    def create_new_contract_tab(self, parent):
        """Cria aba de novo contrato usando o widget NewContractForm"""
        self.new_contract_widget = NewContractForm(
            parent,
            on_save=self.save_contrato,
            on_generate_pdf=self.gerar_pdf_contrato,
            on_clear=self.clear_form,
        )

        # Expõe widgets para uso nas funções existentes
        widgets = self.new_contract_widget.get_widgets()
        self.combo_casa = widgets['combo_casa']
        self.combo_inquilino = widgets['combo_inquilino']
        self.entry_valor_aluguel = widgets['entry_valor_aluguel']
        self.entry_dia_pagamento = widgets['entry_dia_pagamento']
        self.entry_caucao = widgets['entry_caucao']
        self.entry_seguro_fianca = widgets['entry_seguro_fianca']
        self.date_inicio = widgets['date_inicio']
        self.date_fim = widgets['date_fim']
        self.entry_duracao = widgets['entry_duracao']
        self.entry_multa_atraso = widgets['entry_multa_atraso']
        self.entry_juros_dia = widgets['entry_juros_dia']
        self.entry_multa_rescisao = widgets['entry_multa_rescisao']
        self.text_observacoes = widgets['text_observacoes']
        
        # O widget já configura os binds automaticamente, não precisa fazer aqui
    
    def create_list_tab(self, parent):
        """Cria aba de lista de contratos"""
        self.contract_list = ContractListWidget(
            parent,
            on_add=lambda: self.notebook.select(0),
            on_view=self.view_contrato_detail,
            on_edit=self.edit_contrato,
            on_end=self.end_contrato,
            on_generate_pdf=self.reprint_pdf
        )

        # Expõe os filtros
        self.filter_status = self.contract_list.filter_status
        self.filter_casa = self.contract_list.filter_casa
        self.search_var = self.contract_list.search_var

        # Bind dos filtros
        self.filter_status.bind('<<ComboboxSelected>>', lambda e: self.filter_contratos())
        self.filter_casa.bind('<<ComboboxSelected>>', lambda e: self.filter_contratos())
        self.search_var.trace('w', lambda *args: self.filter_contratos())
    
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
    
    def load_inquilinos(self):
        """Carrega inquilinos no combobox"""
        inquilinos = self.inquilino_repo.get_all()
        self.inquilinos_dict = {f"{i.nome_completo} (CPF: {i.cpf})": i for i in inquilinos}
        
        if hasattr(self, 'combo_inquilino'):
            self.combo_inquilino['values'] = list(self.inquilinos_dict.keys())
    
    def load_contratos(self):
        """Carrega todos os contratos na lista"""
        contratos = self.contrato_repo.get_all()
        if hasattr(self, 'contract_list'):
            self.contract_list.set_items(contratos)
    
    def filter_contratos(self):
        """Filtra contratos com base nos critérios selecionados"""
        status_filter = self.filter_status.get()
        casa_filter = self.filter_casa.get()
        search_term = self.search_var.get().lower()
        
        # Busca base
        contratos = self.contrato_repo.get_all()
        
        # Filtro por status
        if status_filter != 'Todos':
            contratos = [c for c in contratos if c.status_descricao == status_filter]
        
        # Filtro por casa
        if casa_filter != 'Todas':
            casa = self.casas_dict.get(casa_filter)
            if casa:
                contratos = [c for c in contratos if c.casa_id == casa.id]
        
        # Filtro por inquilino (busca)
        if search_term:
            contratos = [c for c in contratos if search_term in c.inquilino.nome_completo.lower()]
        
        self.contract_list.set_items(contratos)
    
    def calcular_data_fim(self, event=None):
        """Calcula automaticamente a data de fim baseada no início e duração"""
        try:
            duracao = int(self.entry_duracao.get() or 12)
            data_inicio = self.date_inicio.get_date()
            data_fim = data_inicio + relativedelta(months=duracao)
            self.date_fim.set_date(data_fim)
        except ValueError:
            pass
    
    def save_contrato(self):
        """Salva o contrato no banco de dados"""
        casa_selecionada = self.combo_casa.get()
        inquilino_selecionado = self.combo_inquilino.get()
        
        if not casa_selecionada or not inquilino_selecionado:
            messagebox.showerror("Erro", "Selecione casa e inquilino!")
            return
        
        try:
            casa = self.casas_dict[casa_selecionada]
            inquilino = self.inquilinos_dict[inquilino_selecionado]
            
            # Coleta dados
            valor_aluguel = float(self.entry_valor_aluguel.get())
            dia_pagamento = int(self.entry_dia_pagamento.get())
            caucao = float(self.entry_caucao.get() or 0)
            seguro_fianca = float(self.entry_seguro_fianca.get() or 0)
            data_inicio = self.date_inicio.get_date()
            data_fim = self.date_fim.get_date()
            duracao = int(self.entry_duracao.get())
            multa_atraso = float(self.entry_multa_atraso.get())
            juros_dia = float(self.entry_juros_dia.get())
            multa_rescisao = int(self.entry_multa_rescisao.get())
            observacoes = self.text_observacoes.get("1.0", tk.END).strip()
            
            # Validações
            if dia_pagamento < 1 or dia_pagamento > 31:
                messagebox.showerror("Erro", "Dia de pagamento deve estar entre 1 e 31!")
                return
            
            if data_fim <= data_inicio:
                messagebox.showerror("Erro", "Data de fim deve ser posterior à data de início!")
                return
            
            # Verifica se já existe contrato ativo para esta casa
            contrato_existente = self.contrato_repo.get_contrato_ativo_casa(casa.id)
            if contrato_existente:
                if not messagebox.askyesno("Confirmar", 
                    "Já existe um contrato ativo para esta casa. Deseja encerrá-lo e criar um novo?"):
                    return
                self.contrato_repo.encerrar_contrato(contrato_existente.id)
            
            # Cria novo contrato
            novo_contrato = Contrato(
                casa_id=casa.id,
                inquilino_id=inquilino.id,
                valor_aluguel=valor_aluguel,
                dia_pagamento=dia_pagamento,
                data_inicio=data_inicio,
                data_fim=data_fim,
                duracao_meses=duracao,
                valor_caucao=caucao if caucao > 0 else None,
                valor_seguro_fianca=seguro_fianca if seguro_fianca > 0 else None,
                multa_atraso_percentual=multa_atraso,
                juros_dia_percentual=juros_dia,
                multa_rescisao_meses=multa_rescisao,
                ativo=1,
                observacoes=observacoes if observacoes else None
            )
            
            self.contrato_repo.create(novo_contrato)
            
            # Atualiza o inquilino_id da casa
            casa.inquilino_id = inquilino.id
            self.casa_repo.update(casa)
            
            messagebox.showinfo("Sucesso", "Contrato cadastrado com sucesso!")
            self.clear_form()
            self.load_contratos()
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro nos dados: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
    
    def gerar_pdf_contrato(self):
        """Gera o PDF do contrato"""
        casa_selecionada = self.combo_casa.get()
        inquilino_selecionado = self.combo_inquilino.get()
        
        if not casa_selecionada or not inquilino_selecionado:
            messagebox.showerror("Erro", "Selecione casa e inquilino!")
            return
        
        try:
            casa = self.casas_dict[casa_selecionada]
            inquilino = self.inquilinos_dict[inquilino_selecionado]
            
            # Coleta dados do formulário
            valor_aluguel = float(self.entry_valor_aluguel.get())
            dia_pagamento = int(self.entry_dia_pagamento.get())
            caucao = float(self.entry_caucao.get() or 0)
            seguro_fianca = float(self.entry_seguro_fianca.get() or 0)
            data_inicio = self.date_inicio.get_date()
            data_fim = self.date_fim.get_date()
            duracao = int(self.entry_duracao.get())
            multa_atraso = float(self.entry_multa_atraso.get())
            juros_dia = float(self.entry_juros_dia.get())
            multa_rescisao = int(self.entry_multa_rescisao.get())
            
            # Dados do locador (via .env)
            locador_nome = os.getenv("LOCADOR_NOME", "Seu Nome")
            locador_rg = os.getenv("LOCADOR_RG", "00.000.000-00")
            locador_cpf = os.getenv("LOCADOR_CPF", "000.000.000-00")
            locador_endereco = os.getenv("LOCADOR_ENDERECO", "Seu Endereço")
            
            # Prepara dados para o PDF
            dados_pdf = {
                "locador": {
                    "nome": locador_nome,
                    "nacionalidade": "brasileiro(a)",
                    "estado_civil": "casado(a)",
                    "profissao": "comerciante",
                    "rg": locador_rg,
                    "cpf": locador_cpf,
                    "endereco": locador_endereco
                },
                "locatario": {
                    "nome": inquilino.nome_completo,
                    "nacionalidade": "brasileiro(a)",
                    "estado_civil": "solteiro(a)",
                    "profissao": "profissional",
                    "data_nascimento": inquilino.data_nascimento,
                    "rg": "00.000.000-00",  # Você pode adicionar estes campos no modelo Inquilino
                    "cpf": inquilino.cpf,
                    "endereco": "Endereço do inquilino"
                },
                "imovel": {
                    "descricao_completa": self._gerar_descricao_imovel(casa),
                    "endereco_completo": casa.endereco
                },
                "valores": {
                    "aluguel": valor_aluguel,
                    "caucao": caucao,
                    "seguro_fianca": seguro_fianca,
                    "dia_pagamento": dia_pagamento
                },
                "datas": {
                    "inicio": data_inicio,
                    "fim": data_fim,
                    "duracao_meses": duracao
                },
                "multas": {
                    "atraso_percentual": multa_atraso,
                    "juros_dia": juros_dia,
                    "rescisao_meses": multa_rescisao
                }
            }
            
            arquivo = gerar_contrato_locacao(dados_pdf)
            messagebox.showinfo("Sucesso", f"Contrato PDF gerado com sucesso!\n{arquivo}")
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Erro nos dados: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {str(e)}")
    
    def _gerar_descricao_imovel(self, casa):
        """Gera descrição completa do imóvel para o contrato"""
        descricao = "01 (uma) sala, "
        
        if casa.numero_quartos:
            if casa.numero_quartos == 1:
                descricao += "01 (um) quarto, "
            else:
                descricao += f"0{casa.numero_quartos} ({self._numero_extenso(casa.numero_quartos)}) quartos, "
        else:
            descricao += "quartos, "
        
        descricao += "01 (uma) cozinha, 01 (uma) área de serviço e 01 (um) banheiro"
        return descricao
    
    def _numero_extenso(self, num):
        """Converte número em extenso (simplificado)"""
        extenso = {1: 'um', 2: 'dois', 3: 'três', 4: 'quatro', 5: 'cinco'}
        return extenso.get(num, str(num))
    
    def clear_form(self):
        """Limpa o formulário"""
        self.combo_casa.set('')
        self.combo_inquilino.set('')
        self.entry_valor_aluguel.delete(0, 'end')
        self.entry_dia_pagamento.delete(0, 'end')
        self.entry_dia_pagamento.insert(0, "25")
        self.entry_caucao.delete(0, 'end')
        self.entry_seguro_fianca.delete(0, 'end')
        self.entry_duracao.delete(0, 'end')
        self.entry_duracao.insert(0, "12")
        self.entry_multa_atraso.delete(0, 'end')
        self.entry_multa_atraso.insert(0, "10.0")
        self.entry_juros_dia.delete(0, 'end')
        self.entry_juros_dia.insert(0, "0.33")
        self.entry_multa_rescisao.delete(0, 'end')
        self.entry_multa_rescisao.insert(0, "3")
        self.text_observacoes.delete("1.0", tk.END)
    
    def view_contrato_detail(self, contrato):
        """Visualiza detalhes do contrato"""
        dialog = tk.Toplevel(self)
        dialog.title("Detalhes do Contrato")
        dialog.geometry("600x700")
        dialog.configure(bg='white')
        dialog.transient(self)
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f"600x700+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg='#9C27B0')
        header.pack(fill='x')
        tk.Label(header, text="📋 Detalhes do Contrato", font=("Arial", 16, "bold"), bg='#9C27B0', fg='white').pack(pady=15)
        
        # Content com scroll
        canvas = tk.Canvas(dialog, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg='white')
        
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=30, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        def add_field(label, value):
            tk.Label(content, text=label, bg='white', font=("Arial", 10, "bold"), fg='#666').pack(anchor='w', pady=(10, 2))
            tk.Label(content, text=value, bg='#F5F5F5', font=("Arial", 11), relief='solid', borderwidth=1, anchor='w', padx=10, pady=8).pack(fill='x')
        
        # Informações do contrato
        add_field("Status:", contrato.status_descricao)
        add_field("Casa:", contrato.casa.nome)
        add_field("Endereço:", contrato.casa.endereco)
        add_field("Inquilino:", contrato.inquilino.nome_completo)
        add_field("CPF do Inquilino:", contrato.inquilino.cpf)
        add_field("Telefone:", contrato.inquilino.telefone)
        add_field("Valor do Aluguel:", f"R$ {contrato.valor_aluguel:.2f}")
        add_field("Dia de Pagamento:", str(contrato.dia_pagamento))
        add_field("Data de Início:", contrato.data_inicio.strftime('%d/%m/%Y'))
        add_field("Data de Fim:", contrato.data_fim.strftime('%d/%m/%Y'))
        add_field("Duração:", f"{contrato.duracao_meses} meses")
        
        if contrato.valor_caucao:
            add_field("Valor da Caução:", f"R$ {contrato.valor_caucao:.2f}")
        if contrato.valor_seguro_fianca:
            add_field("Seguro Fiança:", f"R$ {contrato.valor_seguro_fianca:.2f}")
        
        add_field("Multa por Atraso:", f"{contrato.multa_atraso_percentual}%")
        add_field("Juros ao Dia:", f"{contrato.juros_dia_percentual}%")
        add_field("Multa por Rescisão:", f"{contrato.multa_rescisao_meses} meses")
        
        if contrato.observacoes:
            add_field("Observações:", contrato.observacoes)
        
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
    
    def edit_contrato(self, contrato):
        """Editar contrato existente"""
        dialog = tk.Toplevel(self)
        dialog.title("Editar Contrato")
        dialog.geometry("700x800")
        dialog.configure(bg='white')
        dialog.transient(self)
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (dialog.winfo_screenheight() // 2) - (800 // 2)
        dialog.geometry(f"700x800+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg='#FF9800')
        header.pack(fill='x')
        tk.Label(
            header, 
            text="✏️ Editar Contrato", 
            font=("Arial", 16, "bold"), 
            bg='#FF9800', 
            fg='white'
        ).pack(pady=15)
        
        # Content com scroll
        canvas = tk.Canvas(dialog, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg='white')
        
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=30, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # Campos do formulário
        # Casa (não editável)
        tk.Label(content, text="Casa:", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(10, 5))
        lbl_casa = tk.Label(
            content, 
            text=f"{contrato.casa.nome} - {contrato.casa.endereco}", 
            bg='#F5F5F5', 
            font=("Arial", 11),
            relief='solid',
            borderwidth=1,
            anchor='w',
            padx=10,
            pady=8
        )
        lbl_casa.pack(fill='x', pady=(0, 15))
        
        # Inquilino (não editável)
        tk.Label(content, text="Inquilino:", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        lbl_inquilino = tk.Label(
            content,
            text=f"{contrato.inquilino.nome_completo} (CPF: {contrato.inquilino.cpf})",
            bg='#F5F5F5',
            font=("Arial", 11),
            relief='solid',
            borderwidth=1,
            anchor='w',
            padx=10,
            pady=8
        )
        lbl_inquilino.pack(fill='x', pady=(0, 15))
        
        # Valor do Aluguel
        tk.Label(content, text="Valor do Aluguel (R$):*", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        entry_valor = tk.Entry(content, font=("Arial", 11))
        entry_valor.insert(0, f"{contrato.valor_aluguel:.2f}")
        entry_valor.pack(fill='x', pady=(0, 15))
        
        # Dia de Pagamento
        tk.Label(content, text="Dia de Pagamento (1-31):*", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        entry_dia = tk.Entry(content, font=("Arial", 11))
        entry_dia.insert(0, str(contrato.dia_pagamento))
        entry_dia.pack(fill='x', pady=(0, 15))
        
        # Caução
        tk.Label(content, text="Valor da Caução (R$):", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        entry_caucao = tk.Entry(content, font=("Arial", 11))
        entry_caucao.insert(0, f"{contrato.valor_caucao:.2f}" if contrato.valor_caucao else "0.00")
        entry_caucao.pack(fill='x', pady=(0, 15))
        
        # Seguro Fiança
        tk.Label(content, text="Valor Seguro Fiança (R$):", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        entry_seguro = tk.Entry(content, font=("Arial", 11))
        entry_seguro.insert(0, f"{contrato.valor_seguro_fianca:.2f}" if contrato.valor_seguro_fianca else "0.00")
        entry_seguro.pack(fill='x', pady=(0, 15))
        
        # Datas
        tk.Label(content, text="Data de Início:*", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        try:
            from tkcalendar import DateEntry
            date_inicio = DateEntry(
                content,
                font=("Arial", 11),
                width=25,
                background='#FF9800',
                foreground='white',
                borderwidth=2,
                date_pattern='dd/mm/yyyy'
            )
            date_inicio.set_date(contrato.data_inicio)
        except ImportError:
            date_inicio = tk.Entry(content, font=("Arial", 11))
            date_inicio.insert(0, contrato.data_inicio.strftime('%d/%m/%Y'))
        date_inicio.pack(fill='x', pady=(0, 15))
        
        tk.Label(content, text="Data de Fim:*", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        try:
            from tkcalendar import DateEntry
            date_fim = DateEntry(
                content,
                font=("Arial", 11),
                width=25,
                background='#FF9800',
                foreground='white',
                borderwidth=2,
                date_pattern='dd/mm/yyyy'
            )
            date_fim.set_date(contrato.data_fim)
        except ImportError:
            date_fim = tk.Entry(content, font=("Arial", 11))
            date_fim.insert(0, contrato.data_fim.strftime('%d/%m/%Y'))
        date_fim.pack(fill='x', pady=(0, 15))
        
        # Duração
        tk.Label(content, text="Duração (meses):*", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        entry_duracao = tk.Entry(content, font=("Arial", 11))
        entry_duracao.insert(0, str(contrato.duracao_meses))
        entry_duracao.pack(fill='x', pady=(0, 15))
        
        # Multas
        tk.Label(content, text="Multa por Atraso (%):", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        entry_multa_atraso = tk.Entry(content, font=("Arial", 11))
        entry_multa_atraso.insert(0, str(contrato.multa_atraso_percentual))
        entry_multa_atraso.pack(fill='x', pady=(0, 15))
        
        tk.Label(content, text="Juros ao Dia (%):", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        entry_juros = tk.Entry(content, font=("Arial", 11))
        entry_juros.insert(0, str(contrato.juros_dia_percentual))
        entry_juros.pack(fill='x', pady=(0, 15))
        
        tk.Label(content, text="Multa por Rescisão (meses):", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        entry_rescisao = tk.Entry(content, font=("Arial", 11))
        entry_rescisao.insert(0, str(contrato.multa_rescisao_meses))
        entry_rescisao.pack(fill='x', pady=(0, 15))
        
        # Observações
        tk.Label(content, text="Observações:", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        text_obs = tk.Text(content, font=("Arial", 10), height=4, width=60, wrap='word')
        if contrato.observacoes:
            text_obs.insert("1.0", contrato.observacoes)
        text_obs.pack(fill='x', pady=(0, 15))
        
        # Status
        tk.Label(content, text="Status do Contrato:", bg='white', font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 5))
        var_ativo = tk.IntVar(value=contrato.ativo)
        check_ativo = tk.Checkbutton(
            content,
            text="Contrato Ativo",
            variable=var_ativo,
            font=("Arial", 11),
            bg='white'
        )
        check_ativo.pack(anchor='w', pady=(0, 20))
        
        # Função para salvar
        def salvar_edicao():
            try:
                # Validações
                valor_aluguel = float(entry_valor.get())
                dia_pagamento = int(entry_dia.get())
                
                if dia_pagamento < 1 or dia_pagamento > 31:
                    messagebox.showerror("Erro", "Dia de pagamento deve estar entre 1 e 31!")
                    return
                
                # Atualiza o contrato
                contrato.valor_aluguel = valor_aluguel
                contrato.dia_pagamento = dia_pagamento
                contrato.valor_caucao = float(entry_caucao.get() or 0)
                contrato.valor_seguro_fianca = float(entry_seguro.get() or 0)
                
                # Datas
                try:
                    contrato.data_inicio = date_inicio.get_date()
                    contrato.data_fim = date_fim.get_date()
                except:
                    from datetime import datetime
                    contrato.data_inicio = datetime.strptime(date_inicio.get(), '%d/%m/%Y').date()
                    contrato.data_fim = datetime.strptime(date_fim.get(), '%d/%m/%Y').date()
                
                contrato.duracao_meses = int(entry_duracao.get())
                contrato.multa_atraso_percentual = float(entry_multa_atraso.get())
                contrato.juros_dia_percentual = float(entry_juros.get())
                contrato.multa_rescisao_meses = int(entry_rescisao.get())
                contrato.observacoes = text_obs.get("1.0", tk.END).strip() or None
                contrato.ativo = var_ativo.get()
                
                # Salva no banco
                self.contrato_repo.update(contrato)
                
                messagebox.showinfo("Sucesso", "Contrato atualizado com sucesso!")
                dialog.destroy()
                self.load_contratos()
                
            except ValueError as e:
                messagebox.showerror("Erro", f"Erro nos dados: {str(e)}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        
        # Botões
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        tk.Button(
            btn_frame,
            text="💾 Salvar Alterações",
            command=salvar_edicao,
            bg='#FF9800',
            fg='white',
            font=("Arial", 11, "bold"),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="✖️ Cancelar",
            command=dialog.destroy,
            bg='#9E9E9E',
            fg='white',
            font=("Arial", 11, "bold"),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10
        ).pack(side='left', padx=5)
    
    def end_contrato(self, contrato_id):
        """Encerra um contrato"""
        if messagebox.askyesno("Confirmar Encerramento", 
            "Deseja realmente encerrar este contrato?\n\nEsta ação marcará o contrato como encerrado."):
            try:
                self.contrato_repo.encerrar_contrato(contrato_id)
                messagebox.showinfo("Sucesso", "Contrato encerrado!")
                self.load_contratos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao encerrar: {str(e)}")
    
    def reprint_pdf(self, contrato):
        """Reimprime PDF de um contrato existente"""
        try:
            # Similar ao gerar_pdf_contrato, mas usando dados do contrato
            casa = contrato.casa
            inquilino = contrato.inquilino
            
            locador_nome = os.getenv("LOCADOR_NOME", "Seu Nome")
            locador_rg = os.getenv("LOCADOR_RG", "00.000.000-00")
            locador_cpf = os.getenv("LOCADOR_CPF", "000.000.000-00")
            locador_endereco = os.getenv("LOCADOR_ENDERECO", "Seu Endereço")
            
            dados_pdf = {
                "locador": {
                    "nome": locador_nome,
                    "nacionalidade": "brasileiro(a)",
                    "estado_civil": "casado(a)",
                    "profissao": "comerciante",
                    "rg": locador_rg,
                    "cpf": locador_cpf,
                    "endereco": locador_endereco
                },
                "locatario": {
                    "nome": inquilino.nome_completo,
                    "nacionalidade": "brasileiro(a)",
                    "estado_civil": "solteiro(a)",
                    "profissao": "profissional",
                    "data_nascimento": inquilino.data_nascimento,
                    "rg": "00.000.000-00",
                    "cpf": inquilino.cpf,
                    "endereco": "Endereço do inquilino"
                },
                "imovel": {
                    "descricao_completa": self._gerar_descricao_imovel(casa),
                    "endereco_completo": casa.endereco
                },
                "valores": {
                    "aluguel": contrato.valor_aluguel,
                    "caucao": contrato.valor_caucao or 0,
                    "seguro_fianca": contrato.valor_seguro_fianca or 0,
                    "dia_pagamento": contrato.dia_pagamento
                },
                "datas": {
                    "inicio": contrato.data_inicio,
                    "fim": contrato.data_fim,
                    "duracao_meses": contrato.duracao_meses
                },
                "multas": {
                    "atraso_percentual": contrato.multa_atraso_percentual,
                    "juros_dia": contrato.juros_dia_percentual,
                    "rescisao_meses": contrato.multa_rescisao_meses
                }
            }
            
            arquivo = gerar_contrato_locacao(dados_pdf)
            messagebox.showinfo("Sucesso", f"Contrato PDF reimpresso com sucesso!\n{arquivo}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {str(e)}")