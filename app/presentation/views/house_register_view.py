import tkinter as tk
from tkinter import ttk, messagebox
from app.data.models.house import Casa
from app.data.models.Tenant import Inquilino
from app.data.repositories.house_repository import CasaRepository
from app.data.repositories.tenant_repository import InquilinoRepository

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
        header_frame = tk.Frame(self, bg='#1565C0')
        header_frame.pack(fill='x')
        
        tk.Label(
            header_frame,
            text="Gerenciamento de Casas",
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
        
        # Container principal
        container = tk.Frame(self, bg='#f0f0f0')
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Botão adicionar no topo
        top_frame = tk.Frame(container, bg='#f0f0f0')
        top_frame.pack(fill='x', pady=(0, 10))
        
        tk.Button(
            top_frame,
            text="➕ Adicionar Nova Casa",
            command=self.open_add_dialog,
            bg='#4CAF50',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            relief='flat',
            cursor='hand2'
        ).pack(side='left')
        
        # Barra de busca
        search_frame = tk.Frame(container, bg='white', relief='solid', borderwidth=1)
        search_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(search_frame, text="🔍 Buscar:", bg='white', font=("Arial", 10)).pack(side='left', padx=10)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_casas())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 11), width=40)
        search_entry.pack(side='left', padx=5, pady=8)
        
        # Frame da lista com scroll
        list_container = tk.Frame(container, bg='white', relief='solid', borderwidth=1)
        list_container.pack(fill='both', expand=True)
        
        # Canvas para scroll
        self.canvas = tk.Canvas(list_container, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def load_casas(self):
        """Carrega casas na lista"""
        # Limpa frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        casas = self.casa_repo.get_all()
        
        if not casas:
            tk.Label(
                self.scrollable_frame,
                text="Nenhuma casa cadastrada ainda",
                font=("Arial", 12),
                bg='white',
                fg='gray'
            ).pack(pady=50)
            return
        
        # Header da lista
        header = tk.Frame(self.scrollable_frame, bg='#E3F2FD', height=40)
        header.pack(fill='x', padx=10, pady=(10, 0))
        
        tk.Label(header, text="Casa", bg='#E3F2FD', font=("Arial", 10, "bold"), width=20, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="Endereço", bg='#E3F2FD', font=("Arial", 10, "bold"), width=40, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="Inquilino", bg='#E3F2FD', font=("Arial", 10, "bold"), width=25, anchor='w').pack(side='left', padx=5)
        tk.Label(header, text="Ações", bg='#E3F2FD', font=("Arial", 10, "bold"), width=15, anchor='center').pack(side='left', padx=5)
        
        # Itens da lista
        for i, casa in enumerate(casas):
            self.create_casa_item(casa, i)
    
    def create_casa_item(self, casa, index):
        """Cria um item de casa na lista"""
        bg_color = '#FFFFFF' if index % 2 == 0 else '#F5F5F5'
        
        item_frame = tk.Frame(self.scrollable_frame, bg=bg_color, relief='solid', borderwidth=1)
        item_frame.pack(fill='x', padx=10, pady=2)
        
        # Nome
        tk.Label(
            item_frame,
            text=casa.nome,
            bg=bg_color,
            font=("Arial", 10),
            width=20,
            anchor='w'
        ).pack(side='left', padx=5, pady=10)
        
        # Endereço
        tk.Label(
            item_frame,
            text=casa.endereco[:50] + "..." if len(casa.endereco) > 50 else casa.endereco,
            bg=bg_color,
            font=("Arial", 10),
            width=40,
            anchor='w'
        ).pack(side='left', padx=5)
        
        # Inquilino
        inquilino_text = casa.inquilino_atual.nome_completo if casa.inquilino_atual else "Disponível"
        inquilino_color = '#4CAF50' if not casa.inquilino_atual else '#1976D2'
        tk.Label(
            item_frame,
            text=inquilino_text,
            bg=bg_color,
            fg=inquilino_color,
            font=("Arial", 10, "bold" if not casa.inquilino_atual else "normal"),
            width=25,
            anchor='w'
        ).pack(side='left', padx=5)
        
        # Botões de ação
        action_frame = tk.Frame(item_frame, bg=bg_color)
        action_frame.pack(side='left', padx=5)
        
        tk.Button(
            action_frame,
            text="✏️ Editar",
            command=lambda: self.open_edit_dialog(casa),
            bg='#2196F3',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=5
        ).pack(side='left', padx=2)
        
        tk.Button(
            action_frame,
            text="🗑️",
            command=lambda: self.delete_casa(casa.id),
            bg='#F44336',
            fg='white',
            font=("Arial", 9),
            relief='flat',
            cursor='hand2',
            padx=10,
            pady=5
        ).pack(side='left', padx=2)
    
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
        
        for i, casa in enumerate(filtered):
            self.create_casa_item(casa, i)
    
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