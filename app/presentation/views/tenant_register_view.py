import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.data.models.Tenant import Inquilino
from app.data.repositories.tenant_repository import InquilinoRepository
from app.presentation.views.widgets.header_widget import create_header
from app.presentation.views.widgets.tenant_list_widget import TenantListWidget

class TenantRegisterView(tk.Frame):
    """Tela de registro e gerenciamento de inquilinos"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#f0f0f0')
        self.controller = controller
        self.session = controller.get_session()
        self.inquilino_repo = InquilinoRepository(self.session)
        
        self.create_widgets()
        self.load_inquilinos()
    
    def create_widgets(self):
        # Header
        create_header(self, self.controller, title="Gerenciamento de Inquilinos")
        # Tenant list widget
        self.tenant_list = TenantListWidget(self, on_add=self.open_add_dialog, on_view=self.open_view_dialog, on_edit=self.open_edit_dialog, on_delete=self.delete_inquilino)
        # expose search var used by filter and bind change to filter handler
        self.search_var = self.tenant_list.search_var
        self.search_var.trace('w', lambda *args: self.filter_inquilinos())
        self.canvas = self.tenant_list.canvas
        self.scrollable_frame = self.tenant_list.scrollable_frame
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def load_inquilinos(self):
        """Carrega inquilinos na lista"""
        inquilinos = self.inquilino_repo.get_all()
        self.tenant_list.set_items(inquilinos)
    
    # item rendering delegated to TenantListWidget
    
    def filter_inquilinos(self):
        """Filtra inquilinos pela busca"""
        search_term = self.search_var.get().lower()
        inquilinos = self.inquilino_repo.get_all()
        filtered = [i for i in inquilinos if 
                   search_term in i.nome_completo.lower() or 
                   search_term in i.cpf or
                   search_term in i.telefone]
        self.tenant_list.set_items(filtered)
    
    def open_view_dialog(self, inquilino):
        """Abre diálogo de visualização"""
        dialog = tk.Toplevel(self)
        dialog.title("Detalhes do Inquilino")
        dialog.geometry("450x500")
        dialog.configure(bg='white')
        dialog.transient(self)
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"450x500+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg='#9C27B0')
        header.pack(fill='x')
        tk.Label(header, text="👁️ Detalhes do Inquilino", font=("Arial", 16, "bold"), bg='#9C27B0', fg='white').pack(pady=15)
        
        # Content
        content = tk.Frame(dialog, bg='white')
        content.pack(fill='both', expand=True, padx=30, pady=20)
        
        def add_field(label, value):
            tk.Label(content, text=label, bg='white', font=("Arial", 10, "bold"), fg='#666').pack(anchor='w', pady=(10, 2))
            tk.Label(content, text=value, bg='#F5F5F5', font=("Arial", 11), relief='solid', borderwidth=1, anchor='w', padx=10, pady=8).pack(fill='x')
        
        add_field("Nome Completo:", inquilino.nome_completo)
        add_field("CPF:", inquilino.cpf)
        add_field("Data de Nascimento:", inquilino.data_nascimento.strftime('%d/%m/%Y'))
        add_field("Telefone:", inquilino.telefone)
        add_field("Fiador:", inquilino.nome_fiador if inquilino.nome_fiador else "Sem fiador")
        
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
    
    def open_add_dialog(self):
        """Abre diálogo para adicionar inquilino"""
        dialog = tk.Toplevel(self)
        dialog.title("Adicionar Inquilino")
        dialog.geometry("550x550")
        dialog.configure(bg='white')
        dialog.transient(self)
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (550 // 2)
        dialog.geometry(f"550x550+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg='#4CAF50')
        header.pack(fill='x')
        tk.Label(header, text="➕ Novo Inquilino", font=("Arial", 16, "bold"), bg='#4CAF50', fg='white').pack(pady=15)
        
        # Form
        form = tk.Frame(dialog, bg='white')
        form.pack(fill='both', expand=True, padx=30, pady=20)
        
        tk.Label(form, text="Nome Completo:*", bg='white', font=("Arial", 10)).pack(anchor='w', pady=(5, 0))
        entry_nome = tk.Entry(form, font=("Arial", 11), width=50)
        entry_nome.pack(fill='x', pady=(5, 10))
        
        tk.Label(form, text="CPF:* (formato: 000.000.000-00)", bg='white', font=("Arial", 10)).pack(anchor='w')
        entry_cpf = tk.Entry(form, font=("Arial", 11), width=50)
        entry_cpf.pack(fill='x', pady=(5, 10))
        
        tk.Label(form, text="Data de Nascimento:* (formato: DD/MM/AAAA)", bg='white', font=("Arial", 10)).pack(anchor='w')
        entry_data = tk.Entry(form, font=("Arial", 11), width=50)
        entry_data.pack(fill='x', pady=(5, 10))
        
        tk.Label(form, text="Telefone:* (formato: (00) 00000-0000)", bg='white', font=("Arial", 10)).pack(anchor='w')
        entry_telefone = tk.Entry(form, font=("Arial", 11), width=50)
        entry_telefone.pack(fill='x', pady=(5, 10))
        
        tk.Label(form, text="Nome do Fiador (Opcional):", bg='white', font=("Arial", 10)).pack(anchor='w')
        entry_fiador = tk.Entry(form, font=("Arial", 11), width=50)
        entry_fiador.pack(fill='x', pady=(5, 20))
        
        # Botões
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        def save():
            nome = entry_nome.get().strip()
            cpf = entry_cpf.get().strip()
            data_str = entry_data.get().strip()
            telefone = entry_telefone.get().strip()
            fiador = entry_fiador.get().strip()
            
            if not all([nome, cpf, data_str, telefone]):
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios (*)!")
                return
            
            if not self.validate_cpf(cpf):
                messagebox.showerror("Erro", "CPF inválido!")
                return
            
            try:
                data_nasc = datetime.strptime(data_str, '%d/%m/%Y').date()
            except:
                messagebox.showerror("Erro", "Data inválida! Use DD/MM/AAAA")
                return
            
            try:
                novo = Inquilino(
                    nome_completo=nome,
                    cpf=cpf,
                    data_nascimento=data_nasc,
                    telefone=telefone,
                    nome_fiador=fiador if fiador else None
                )
                self.inquilino_repo.create(novo)
                messagebox.showinfo("Sucesso", "Inquilino cadastrado!")
                dialog.destroy()
                self.load_inquilinos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro: {str(e)}")
        
        tk.Button(btn_frame, text="💾 Salvar", command=save, bg='#4CAF50', fg='white', font=("Arial", 11, "bold"), relief='flat', cursor='hand2', padx=20, pady=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text="❌ Cancelar", command=dialog.destroy, bg='#9E9E9E', fg='white', font=("Arial", 11, "bold"), relief='flat', cursor='hand2', padx=20, pady=10).pack(side='left', padx=5)
    
    def open_edit_dialog(self, inquilino):
        """Abre diálogo para editar inquilino"""
        dialog = tk.Toplevel(self)
        dialog.title("Editar Inquilino")
        dialog.geometry("550x550")
        dialog.configure(bg='white')
        dialog.transient(self)
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (550 // 2)
        dialog.geometry(f"550x550+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg='#FF9800')
        header.pack(fill='x')
        tk.Label(header, text="✏️ Editar Inquilino", font=("Arial", 16, "bold"), bg='#FF9800', fg='white').pack(pady=15)
        
        # Form
        form = tk.Frame(dialog, bg='white')
        form.pack(fill='both', expand=True, padx=30, pady=20)
        
        tk.Label(form, text="Nome Completo:*", bg='white', font=("Arial", 10)).pack(anchor='w', pady=(5, 0))
        entry_nome = tk.Entry(form, font=("Arial", 11), width=50)
        entry_nome.insert(0, inquilino.nome_completo)
        entry_nome.pack(fill='x', pady=(5, 10))
        
        tk.Label(form, text="CPF:*", bg='white', font=("Arial", 10)).pack(anchor='w')
        entry_cpf = tk.Entry(form, font=("Arial", 11), width=50)
        entry_cpf.insert(0, inquilino.cpf)
        entry_cpf.pack(fill='x', pady=(5, 10))
        
        tk.Label(form, text="Data de Nascimento:*", bg='white', font=("Arial", 10)).pack(anchor='w')
        entry_data = tk.Entry(form, font=("Arial", 11), width=50)
        entry_data.insert(0, inquilino.data_nascimento.strftime('%d/%m/%Y'))
        entry_data.pack(fill='x', pady=(5, 10))
        
        tk.Label(form, text="Telefone:*", bg='white', font=("Arial", 10)).pack(anchor='w')
        entry_telefone = tk.Entry(form, font=("Arial", 11), width=50)
        entry_telefone.insert(0, inquilino.telefone)
        entry_telefone.pack(fill='x', pady=(5, 10))
        
        tk.Label(form, text="Nome do Fiador:", bg='white', font=("Arial", 10)).pack(anchor='w')
        entry_fiador = tk.Entry(form, font=("Arial", 11), width=50)
        if inquilino.nome_fiador:
            entry_fiador.insert(0, inquilino.nome_fiador)
        entry_fiador.pack(fill='x', pady=(5, 20))
        
        # Botões
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        def update():
            nome = entry_nome.get().strip()
            cpf = entry_cpf.get().strip()
            data_str = entry_data.get().strip()
            telefone = entry_telefone.get().strip()
            fiador = entry_fiador.get().strip()
            
            if not all([nome, cpf, data_str, telefone]):
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
                return
            
            if not self.validate_cpf(cpf):
                messagebox.showerror("Erro", "CPF inválido!")
                return
            
            try:
                data_nasc = datetime.strptime(data_str, '%d/%m/%Y').date()
            except:
                messagebox.showerror("Erro", "Data inválida!")
                return
            
            try:
                inquilino.nome_completo = nome
                inquilino.cpf = cpf
                inquilino.data_nascimento = data_nasc
                inquilino.telefone = telefone
                inquilino.nome_fiador = fiador if fiador else None
                self.inquilino_repo.update(inquilino)
                messagebox.showinfo("Sucesso", "Inquilino atualizado!")
                dialog.destroy()
                self.load_inquilinos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro: {str(e)}")
        
        tk.Button(btn_frame, text="💾 Atualizar", command=update, bg='#FF9800', fg='white', font=("Arial", 11, "bold"), relief='flat', cursor='hand2', padx=20, pady=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text="❌ Cancelar", command=dialog.destroy, bg='#9E9E9E', fg='white', font=("Arial", 11, "bold"), relief='flat', cursor='hand2', padx=20, pady=10).pack(side='left', padx=5)
    
    def delete_inquilino(self, inquilino_id):
        """Exclui um inquilino"""
        if messagebox.askyesno("Confirmar Exclusão", "Deseja realmente excluir este inquilino?\n\nEsta ação não pode ser desfeita."):
            try:
                self.inquilino_repo.delete(inquilino_id)
                messagebox.showinfo("Sucesso", "Inquilino excluído!")
                self.load_inquilinos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro: {str(e)}")
    
    def validate_cpf(self, cpf):
        """Validação básica de CPF"""
        cpf = cpf.replace('.', '').replace('-', '').replace(' ', '')
        return len(cpf) == 11 and cpf.isdigit()