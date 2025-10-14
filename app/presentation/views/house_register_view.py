import tkinter as tk
from tkinter import ttk, messagebox
from app.data.models.house import Casa
from app.data.models.Tenant import Inquilino
from app.data.repositories.house_repository import CasaRepository
from app.data.repositories.tenant_repository import InquilinoRepository
from app.presentation.views.widgets.header_widget import create_header
from app.presentation.views.widgets.house_list_widget import HouseListWidget

class HouseRegisterView(tk.Frame):
    """Tela de registro e gerenciamento de casas"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#f0f0f0')
        self.controller = controller
        self.session = controller.get_session()
        self.casa_repo = CasaRepository(self.session)
        self.inquilino_repo = InquilinoRepository(self.session)
        
        self.create_widgets()
        self.load_casas()
    
    def create_widgets(self):
        # Header
        create_header(self, self.controller, title="Gerenciamento de Casas")

        # House list widget
        self.house_list = HouseListWidget(self, on_add=self.open_add_dialog, on_edit=self.open_edit_dialog, on_delete=self.delete_casa)
        self.search_var = self.house_list.search_var
        self.search_var.trace('w', lambda *args: self.filter_casas())
        self.canvas = self.house_list.canvas
        self.scrollable_frame = self.house_list.scrollable_frame
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def load_casas(self):
        """Carrega casas na lista"""
        casas = self.casa_repo.get_all()
        self.house_list.set_items(casas)  # items handled by widget
    
    # create_casa_item removed — rendering delegated to HouseListWidget
    
    def filter_casas(self):
        """Filtra casas pela busca"""
        search_term = self.search_var.get().lower()
        
        # Limpa frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        casas = self.casa_repo.get_all()
        filtered = [c for c in casas if 
                   search_term in c.nome.lower() or 
                   search_term in c.endereco.lower() or
                   (c.inquilino_atual and search_term in c.inquilino_atual.nome_completo.lower())]
        
        if not filtered:
            tk.Label(
                self.scrollable_frame,
                text="Nenhuma casa encontrada",
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
        
        self.house_list.set_items(filtered)  # items handled by widget
    
    def open_add_dialog(self):
        """Abre diálogo para adicionar casa"""
        dialog = tk.Toplevel(self)
        dialog.title("Adicionar Casa")
        dialog.geometry("500x400")
        dialog.configure(bg='white')
        dialog.transient(self)
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"500x400+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg='#4CAF50')
        header.pack(fill='x')
        tk.Label(header, text="➕ Nova Casa", font=("Arial", 16, "bold"), bg='#4CAF50', fg='white').pack(pady=15)
        
        # Form
        form = tk.Frame(dialog, bg='white')
        form.pack(fill='both', expand=True, padx=30, pady=20)
        
        tk.Label(form, text="Nome da Casa:*", bg='white', font=("Arial", 10)).pack(anchor='w', pady=(10, 0))
        entry_nome = tk.Entry(form, font=("Arial", 11), width=45)
        entry_nome.pack(fill='x', pady=(5, 10))
        
        tk.Label(form, text="Endereço Completo:*", bg='white', font=("Arial", 10)).pack(anchor='w')
        entry_endereco = tk.Entry(form, font=("Arial", 11), width=45)
        entry_endereco.pack(fill='x', pady=(5, 10))
        
        tk.Label(form, text="Inquilino (Opcional):", bg='white', font=("Arial", 10)).pack(anchor='w')
        
        inquilinos = self.inquilino_repo.get_all()
        inquilinos_dict = {f"{i.nome_completo} (CPF: {i.cpf})": i.id for i in inquilinos}
        
        combo_inquilino = ttk.Combobox(form, font=("Arial", 11), width=43, state='readonly')
        combo_inquilino['values'] = ['Nenhum'] + list(inquilinos_dict.keys())
        combo_inquilino.set('Nenhum')
        combo_inquilino.pack(fill='x', pady=(5, 20))
        
        # Botões
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        def save():
            nome = entry_nome.get().strip()
            endereco = entry_endereco.get().strip()
            
            if not nome or not endereco:
                messagebox.showerror("Erro", "Preencha nome e endereço!")
                return
            
            inquilino_sel = combo_inquilino.get()
            inquilino_id = inquilinos_dict.get(inquilino_sel) if inquilino_sel != 'Nenhum' else None
            
            try:
                nova_casa = Casa(nome=nome, endereco=endereco, inquilino_id=inquilino_id)
                self.casa_repo.create(nova_casa)
                messagebox.showinfo("Sucesso", "Casa cadastrada com sucesso!")
                dialog.destroy()
                self.load_casas()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        
        tk.Button(
            btn_frame,
            text="💾 Salvar Casa",
            command=save,
            bg='#4CAF50',
            fg='white',
            font=("Arial", 11, "bold"),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame,
            text="❌ Cancelar",
            command=dialog.destroy,
            bg='#9E9E9E',
            fg='white',
            font=("Arial", 11, "bold"),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10
        ).pack(side='left', padx=5)
    
    def open_edit_dialog(self, casa):
        """Abre diálogo para editar casa"""
        dialog = tk.Toplevel(self)
        dialog.title("Editar Casa")
        dialog.geometry("500x400")
        dialog.configure(bg='white')
        dialog.transient(self)
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"500x400+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg='#FF9800')
        header.pack(fill='x')
        tk.Label(header, text="✏️ Editar Casa", font=("Arial", 16, "bold"), bg='#FF9800', fg='white').pack(pady=15)
        
        # Form
        form = tk.Frame(dialog, bg='white')
        form.pack(fill='both', expand=True, padx=30, pady=20)
        
        tk.Label(form, text="Nome da Casa:*", bg='white', font=("Arial", 10)).pack(anchor='w', pady=(10, 0))
        entry_nome = tk.Entry(form, font=("Arial", 11), width=45)
        entry_nome.insert(0, casa.nome)
        entry_nome.pack(fill='x', pady=(5, 10))
        
        tk.Label(form, text="Endereço Completo:*", bg='white', font=("Arial", 10)).pack(anchor='w')
        entry_endereco = tk.Entry(form, font=("Arial", 11), width=45)
        entry_endereco.insert(0, casa.endereco)
        entry_endereco.pack(fill='x', pady=(5, 10))
        
        tk.Label(form, text="Inquilino:", bg='white', font=("Arial", 10)).pack(anchor='w')
        
        inquilinos = self.inquilino_repo.get_all()
        inquilinos_dict = {f"{i.nome_completo} (CPF: {i.cpf})": i.id for i in inquilinos}
        
        combo_inquilino = ttk.Combobox(form, font=("Arial", 11), width=43, state='readonly')
        combo_inquilino['values'] = ['Nenhum'] + list(inquilinos_dict.keys())
        
        if casa.inquilino_id:
            for key, value in inquilinos_dict.items():
                if value == casa.inquilino_id:
                    combo_inquilino.set(key)
                    break
        else:
            combo_inquilino.set('Nenhum')
        
        combo_inquilino.pack(fill='x', pady=(5, 20))
        
        # Botões
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(fill='x', padx=30, pady=(0, 20))
        
        def update():
            nome = entry_nome.get().strip()
            endereco = entry_endereco.get().strip()
            
            if not nome or not endereco:
                messagebox.showerror("Erro", "Preencha nome e endereço!")
                return
            
            inquilino_sel = combo_inquilino.get()
            inquilino_id = inquilinos_dict.get(inquilino_sel) if inquilino_sel != 'Nenhum' else None
            
            try:
                casa.nome = nome
                casa.endereco = endereco
                casa.inquilino_id = inquilino_id
                self.casa_repo.update(casa)
                messagebox.showinfo("Sucesso", "Casa atualizada com sucesso!")
                dialog.destroy()
                self.load_casas()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar: {str(e)}")
        
        tk.Button(
            btn_frame,
            text="💾 Atualizar",
            command=update,
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
            text="❌ Cancelar",
            command=dialog.destroy,
            bg='#9E9E9E',
            fg='white',
            font=("Arial", 11, "bold"),
            relief='flat',
            cursor='hand2',
            padx=20,
            pady=10
        ).pack(side='left', padx=5)
    
    def delete_casa(self, casa_id):
        """Exclui uma casa"""
        if messagebox.askyesno("Confirmar Exclusão", "Deseja realmente excluir esta casa?\n\nEsta ação não pode ser desfeita."):
            try:
                self.casa_repo.delete(casa_id)
                messagebox.showinfo("Sucesso", "Casa excluída com sucesso!")
                self.load_casas()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {str(e)}")