import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from app.data.models.receipt import Recibo
from app.data.repositories.receipt_repository import ReciboRepository
from app.data.repositories.house_repository import CasaRepository
from app.data.repositories.tenant_repository import InquilinoRepository
from app.presentation.usecases.generate_receipt_pdf_usecase import gerar_recibo_pagamento
from app.presentation.views.widgets.header_widget import create_header
from app.presentation.views.widgets.new_receipt_form_widget import NewReceiptForm
from app.presentation.views.widgets.receipt_list_widget import ReceiptListWidget

load_dotenv()


class ReceiptView(tk.Frame):
    """Tela de gerenciamento de recibos de pagamento"""

    def __init__(self, parent, controller):
        super().__init__(parent, bg='#f0f0f0')
        self.controller = controller
        self.session = controller.get_session()
        self.recibo_repo = ReciboRepository(self.session)
        self.casa_repo = CasaRepository(self.session)
        self.inquilino_repo = InquilinoRepository(self.session)

        # Dicionários para mapear seleções
        self.casas_dict = {}
        self.inquilinos_dict = {}

        self.create_widgets()

    def create_widgets(self):
        # Header
        create_header(self, self.controller, title="Gerenciamento de Recibos")

        # Container principal com abas
        container = tk.Frame(self, bg='#f0f0f0')
        container.pack(fill='both', expand=True, padx=20, pady=20)

        # Notebook para abas
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill='both', expand=True)

        # Aba 1: Novo Recibo
        tab_new = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab_new, text="  🧾 Novo Recibo  ")

        # Aba 2: Lista de Recibos
        tab_list = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab_list, text="  📋 Recibos Cadastrados  ")

        # Criar as abas
        self.create_new_receipt_tab(tab_new)
        self.create_list_tab(tab_list)

        # Carregar dados
        self.load_casas()
        self.load_inquilinos()
        self.load_recibos()
        
        # Preencher dados do recebedor com dados do .env
        self.entry_nome_recebedor.delete(0, 'end')
        self.entry_nome_recebedor.insert(0, os.getenv("LOCADOR_NOME", ""))
        self.entry_cpf_recebedor.delete(0, 'end')
        self.entry_cpf_recebedor.insert(0, os.getenv("LOCADOR_CPF", ""))

    def create_new_receipt_tab(self, parent):
        """Cria aba de novo recibo usando o widget NewReceiptForm"""
        self.new_receipt_widget = NewReceiptForm(
            parent,
            on_save=self.save_recibo,
            on_generate_pdf=self.gerar_pdf_recibo,
            on_clear=self.clear_form,
        )

        # Expõe widgets para uso nas funções existentes
        widgets = self.new_receipt_widget.get_widgets()
        self.combo_tipo = widgets['combo_tipo']
        self.combo_casa = widgets['combo_casa']
        self.combo_inquilino = widgets['combo_inquilino']
        self.entry_nome_pagador = widgets['entry_nome_pagador']
        self.entry_cpf_pagador = widgets['entry_cpf_pagador']
        self.entry_nome_recebedor = widgets['entry_nome_recebedor']
        self.entry_cpf_recebedor = widgets['entry_cpf_recebedor']
        self.entry_valor = widgets['entry_valor']
        self.entry_referente = widgets['entry_referente']
        self.text_descricao = widgets['text_descricao']
        self.date_pagamento = widgets['date_pagamento']
        self.combo_forma_pag = widgets['combo_forma_pag']
        self.text_observacoes = widgets['text_observacoes']

        # Bind para auto-preencher ao selecionar inquilino
        self.combo_inquilino.bind('<<ComboboxSelected>>', self.on_inquilino_selected)

    def create_list_tab(self, parent):
        """Cria aba de lista de recibos"""
        self.receipt_list = ReceiptListWidget(
            parent,
            on_add=lambda: self.notebook.select(0),
            on_view=self.view_recibo_detail,
            on_reprint=self.reprint_pdf,
            on_delete=self.delete_recibo
        )

        # Expõe os filtros
        self.filter_tipo = self.receipt_list.filter_tipo
        self.search_var = self.receipt_list.search_var

        # Bind dos filtros
        self.filter_tipo.bind('<<ComboboxSelected>>', lambda e: self.filter_recibos())
        self.search_var.trace('w', lambda *args: self.filter_recibos())

    def load_casas(self):
        """Carrega casas nos comboboxes"""
        casas = self.casa_repo.get_all()
        self.casas_dict = {f"{c.nome} - {c.endereco}": c for c in casas}

        if hasattr(self, 'combo_casa'):
            self.combo_casa['values'] = ['Nenhuma'] + list(self.casas_dict.keys())
            self.combo_casa.set('Nenhuma')

    def load_inquilinos(self):
        """Carrega inquilinos no combobox"""
        inquilinos = self.inquilino_repo.get_all()
        self.inquilinos_dict = {f"{i.nome_completo} (CPF: {i.cpf})": i for i in inquilinos}

        if hasattr(self, 'combo_inquilino'):
            self.combo_inquilino['values'] = ['Nenhum'] + list(self.inquilinos_dict.keys())
            self.combo_inquilino.set('Nenhum')

    def load_recibos(self):
        """Carrega todos os recibos na lista"""
        recibos = self.recibo_repo.get_all()
        if hasattr(self, 'receipt_list'):
            self.receipt_list.set_items(recibos)

    def filter_recibos(self):
        """Filtra recibos com base nos critérios selecionados"""
        tipo_filter = self.filter_tipo.get()
        search_term = self.search_var.get().lower()

        # Busca base
        recibos = self.recibo_repo.get_all()

        # Filtro por tipo
        if tipo_filter != 'Todos':
            tipo_map = {
                'Aluguel': 'aluguel',
                'Conta de Energia': 'energia',
                'Serviço Prestado': 'servico',
                'Outros': 'outros'
            }
            tipo_busca = tipo_map.get(tipo_filter, tipo_filter.lower())
            recibos = [r for r in recibos if r.tipo_recibo == tipo_busca]

        # Filtro por pagador (busca)
        if search_term:
            recibos = [r for r in recibos if search_term in r.nome_pagador.lower()]

        self.receipt_list.set_items(recibos)

    def on_inquilino_selected(self, event=None):
        """Auto-preenche dados ao selecionar inquilino"""
        inquilino_selecionado = self.combo_inquilino.get()

        if inquilino_selecionado and inquilino_selecionado != 'Nenhum':
            inquilino = self.inquilinos_dict[inquilino_selecionado]

            # Preenche nome e CPF
            self.entry_nome_pagador.delete(0, 'end')
            self.entry_nome_pagador.insert(0, inquilino.nome_completo)

            self.entry_cpf_pagador.delete(0, 'end')
            self.entry_cpf_pagador.insert(0, inquilino.cpf)

    def save_recibo(self):
        """Salva o recibo no banco de dados"""
        try:
            # Coleta dados
            tipo_map = {
                'Aluguel': 'aluguel',
                'Conta de Energia': 'energia',
                'Serviço Prestado': 'servico',
                'Outros': 'outros'
            }
            tipo_recibo = tipo_map.get(self.combo_tipo.get(), 'outros')

            casa_selecionada = self.combo_casa.get()
            casa_id = self.casas_dict[casa_selecionada].id if casa_selecionada != 'Nenhuma' else None

            inquilino_selecionado = self.combo_inquilino.get()
            inquilino_id = self.inquilinos_dict[inquilino_selecionado].id if inquilino_selecionado != 'Nenhum' else None

            nome_pagador = self.entry_nome_pagador.get().strip()
            cpf_pagador = self.entry_cpf_pagador.get().strip() or None
            nome_recebedor = self.entry_nome_recebedor.get().strip()
            cpf_recebedor = self.entry_cpf_recebedor.get().strip() or None
            
            # Validação de valor
            try:
                valor = float(self.entry_valor.get())
                if valor <= 0:
                    messagebox.showerror("Erro", "O valor deve ser maior que zero!")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido!")
                return
            
            referente_a = self.entry_referente.get().strip()
            
            # CORREÇÃO: Descrição não pode ser None, usa texto padrão se vazio
            descricao_raw = self.text_descricao.get("1.0", tk.END).strip()
            descricao = descricao_raw if descricao_raw else f"Pagamento referente a {referente_a}"

            try:
                data_pagamento = self.date_pagamento.get_date()
            except:
                data_pagamento = datetime.strptime(self.date_pagamento.get(), '%d/%m/%Y').date()

            forma_map = {
                'Dinheiro': 'dinheiro',
                'PIX': 'pix',
                'Transferência Bancária': 'transferencia',
                'Cheque': 'cheque',
                'Cartão': 'cartao'
            }
            forma_pagamento = forma_map.get(self.combo_forma_pag.get(), 'dinheiro')

            observacoes = self.text_observacoes.get("1.0", tk.END).strip() or None

            # Validações
            if not nome_pagador or not nome_recebedor or not referente_a:
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
                return

            # Cria novo recibo
            novo_recibo = Recibo(
                tipo_recibo=tipo_recibo,
                casa_id=casa_id,
                inquilino_id=inquilino_id,
                nome_pagador=nome_pagador,
                cpf_pagador=cpf_pagador,
                nome_recebedor=nome_recebedor,
                cpf_recebedor=cpf_recebedor,
                valor=valor,
                descricao=descricao,  # Sempre terá um valor válido
                referente_a=referente_a,
                data_pagamento=data_pagamento,
                forma_pagamento=forma_pagamento,
                observacoes=observacoes
            )

            self.recibo_repo.create(novo_recibo)

            messagebox.showinfo("Sucesso", "Recibo salvo com sucesso!")
            self.clear_form()
            self.load_recibos()

        except ValueError as e:
            messagebox.showerror("Erro", f"Erro nos dados: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")

    def gerar_pdf_recibo(self):
        """Gera o PDF do recibo"""
        try:
            nome_pagador = self.entry_nome_pagador.get().strip()
            cpf_pagador = self.entry_cpf_pagador.get().strip() or None
            nome_recebedor = self.entry_nome_recebedor.get().strip()
            cpf_recebedor = self.entry_cpf_recebedor.get().strip() or None
            valor = float(self.entry_valor.get())
            referente_a = self.entry_referente.get().strip()
            descricao_raw = self.text_descricao.get("1.0", tk.END).strip()
            descricao = descricao_raw if descricao_raw else None

            try:
                data_pagamento = self.date_pagamento.get_date()
            except:
                data_pagamento = datetime.strptime(self.date_pagamento.get(), '%d/%m/%Y').date()

            forma_pagamento = self.combo_forma_pag.get()
            observacoes = self.text_observacoes.get("1.0", tk.END).strip() or None

            # Validações
            if not nome_pagador or not nome_recebedor or not referente_a:
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
                return

            # Gera número do recibo (pode ser melhorado)
            ultimo_recibo = self.recibo_repo.get_all()
            numero_recibo = len(ultimo_recibo) + 1

            # Cria um objeto Recibo temporário para usar o método valor_extenso
            recibo_temp = Recibo(
                tipo_recibo='temp',
                nome_pagador=nome_pagador,
                nome_recebedor=nome_recebedor,
                valor=valor,
                referente_a=referente_a,
                descricao=descricao or f"Pagamento referente a {referente_a}",
                data_pagamento=data_pagamento
            )

            # Prepara dados para o PDF
            dados_pdf = {
                "numero_recibo": f"{numero_recibo:06d}",
                "valor": valor,
                "valor_extenso": recibo_temp.valor_extenso,
                "nome_pagador": nome_pagador,
                "cpf_pagador": cpf_pagador,
                "nome_recebedor": nome_recebedor,
                "cpf_recebedor": cpf_recebedor,
                "referente_a": referente_a,
                "descricao": descricao,
                "data_pagamento": data_pagamento,
                "forma_pagamento": forma_pagamento,
                "observacoes": observacoes
            }

            arquivo = gerar_recibo_pagamento(dados_pdf)
            messagebox.showinfo("Sucesso", f"Recibo PDF gerado com sucesso!\n{arquivo}")

        except ValueError as e:
            messagebox.showerror("Erro", f"Erro nos dados: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {str(e)}")

    def clear_form(self):
        """Limpa o formulário"""
        self.combo_tipo.set('Aluguel')
        self.combo_casa.set('Nenhuma')
        self.combo_inquilino.set('Nenhum')
        self.entry_nome_pagador.delete(0, 'end')
        self.entry_cpf_pagador.delete(0, 'end')
        self.entry_valor.delete(0, 'end')
        self.entry_referente.delete(0, 'end')
        self.text_descricao.delete("1.0", tk.END)
        self.combo_forma_pag.set('Dinheiro')
        self.text_observacoes.delete("1.0", tk.END)
        
        # Restaura dados do recebedor
        self.entry_nome_recebedor.delete(0, 'end')
        self.entry_nome_recebedor.insert(0, os.getenv("LOCADOR_NOME", ""))
        self.entry_cpf_recebedor.delete(0, 'end')
        self.entry_cpf_recebedor.insert(0, os.getenv("LOCADOR_CPF", ""))

    def view_recibo_detail(self, recibo):
        """Visualiza detalhes do recibo"""
        dialog = tk.Toplevel(self)
        dialog.title("Detalhes do Recibo")
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
        tk.Label(header, text="🧾 Detalhes do Recibo", font=("Arial", 16, "bold"), bg='#9C27B0', fg='white').pack(pady=15)

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

        # Informações do recibo
        add_field("Número do Recibo:", f"#{recibo.id}")
        add_field("Tipo:", recibo.tipo_recibo.title())
        add_field("Valor:", f"R$ {recibo.valor:.2f}")
        add_field("Pagador:", recibo.nome_pagador)
        if recibo.cpf_pagador:
            add_field("CPF do Pagador:", recibo.cpf_pagador)
        add_field("Recebedor:", recibo.nome_recebedor)
        if recibo.cpf_recebedor:
            add_field("CPF do Recebedor:", recibo.cpf_recebedor)
        add_field("Referente a:", recibo.referente_a)
        if recibo.descricao:
            add_field("Descrição:", recibo.descricao)
        add_field("Data do Pagamento:", recibo.data_pagamento.strftime('%d/%m/%Y'))
        add_field("Data de Emissão:", recibo.data_emissao.strftime('%d/%m/%Y'))
        if recibo.forma_pagamento:
            add_field("Forma de Pagamento:", recibo.forma_pagamento.title())
        if recibo.observacoes:
            add_field("Observações:", recibo.observacoes)

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

    def reprint_pdf(self, recibo):
        """Reimprime PDF de um recibo existente"""
        try:
            dados_pdf = {
                "numero_recibo": f"{recibo.id:06d}",
                "valor": recibo.valor,
                "valor_extenso": recibo.valor_extenso,
                "nome_pagador": recibo.nome_pagador,
                "cpf_pagador": recibo.cpf_pagador,
                "nome_recebedor": recibo.nome_recebedor,
                "cpf_recebedor": recibo.cpf_recebedor,
                "referente_a": recibo.referente_a,
                "descricao": recibo.descricao,
                "data_pagamento": recibo.data_pagamento,
                "forma_pagamento": recibo.forma_pagamento,
                "observacoes": recibo.observacoes
            }

            arquivo = gerar_recibo_pagamento(dados_pdf)
            messagebox.showinfo("Sucesso", f"Recibo PDF reimpresso com sucesso!\n{arquivo}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {str(e)}")

    def delete_recibo(self, recibo_id):
        """Exclui um recibo"""
        if messagebox.askyesno("Confirmar Exclusão",
            "Deseja realmente excluir este recibo?\n\nEsta ação não pode ser desfeita."):
            try:
                self.recibo_repo.delete(recibo_id)
                messagebox.showinfo("Sucesso", "Recibo excluído!")
                self.load_recibos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {str(e)}")