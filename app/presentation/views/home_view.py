import tkinter as tk
from tkinter import ttk, messagebox


class HomeView(tk.Frame):
    """Tela inicial otimizada com cache de widgets"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#f5f5f5')
        self.controller = controller
        self._cards_cache = []  # Cache de cards para reutilização
        
        # Construir interface apenas uma vez
        self._build_interface()
    
    def _build_interface(self):
        """Constrói a interface de forma otimizada e proporcional"""
        # Container principal sem scroll (mais leve)
        main_container = tk.Frame(self, bg='#f5f5f5')
        main_container.pack(fill='both', expand=True)
        
        # Header fixo - altura proporcional (~15% da altura)
        self._create_header(main_container)
        
        # Content com scroll apenas se necessário (~80% da altura)
        content_wrapper = tk.Frame(main_container, bg='#f5f5f5')
        content_wrapper.pack(fill='both', expand=True)
        
        # Canvas otimizado
        canvas = tk.Canvas(content_wrapper, bg='#f5f5f5', highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_wrapper, orient="vertical", command=canvas.yview)
        
        # Frame scrollável
        self.scrollable_frame = tk.Frame(canvas, bg='#f5f5f5')
        
        # Configuração otimizada do scroll
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Ajusta largura do frame ao canvas
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        self.scrollable_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Scroll com mousewheel
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Content - padding proporcional
        content = tk.Frame(self.scrollable_frame, bg='#f5f5f5')
        content.pack(fill='both', expand=True, padx=40, pady=30)
        
        # Criar cards em grid simples
        self._create_cards_grid(content)
        
        # Rodapé (~5% da altura)
        self._create_footer(self.scrollable_frame)
    
    def _create_header(self, parent):
        """Cria header fixo"""
        header = tk.Frame(parent, bg='#1565C0')
        header.pack(fill='x')
        
        tk.Label(
            header, 
            text="🏠 Sistema de Gestão de Aluguéis",
            font=("Arial", 24, "bold"),
            bg='#1565C0',
            fg='white'
        ).pack(pady=(15, 5))
        
        tk.Label(
            header,
            text="Gerencie suas propriedades, inquilinos, contratos e pagamentos",
            font=("Arial", 10),
            bg='#1565C0',
            fg='#E3F2FD'
        ).pack(pady=(0, 15))
    
    def _create_cards_grid(self, parent):
        """Cria grid de cards sem seções"""
        
        # Todos os cards em um array simples
        all_cards = [
            ('🏘️', 'Casas', 'Cadastro e gerenciamento de imóveis', '#4CAF50', 'registro_casas'),
            ('👥', 'Inquilinos', 'Cadastro e dados dos locatários', '#2196F3', 'registro_inquilinos'),
            ('📝', 'Contratos', 'Contratos de locação e renovações', '#FF9800', 'gestao_contratos'),
            ('🧾', 'Recibos', 'Gerar recibos de pagamento', '#9C27B0', 'gestao_recibos'),
            ('⚡', 'Conta de Energia', 'Geração de contas proporcionais', '#FFC107', 'gerar_conta_energia'),
            ('📊', 'Relatórios', 'Relatórios e análises financeiras', '#607D8B', None, 'Em breve')
        ]
        
        # Criar linhas de 4 cards (depois 2 na segunda linha)
        # Primeira linha: 4 cards
        row1 = tk.Frame(parent, bg='#f5f5f5')
        row1.pack(fill='x', pady=(0, 10))
        
        for i in range(4):
            icon, title, desc, color, frame = all_cards[i]
            self._create_optimized_card(row1, icon, title, desc, color, frame)
        
        # Segunda linha: 2 cards
        row2 = tk.Frame(parent, bg='#f5f5f5')
        row2.pack(fill='x', pady=(0, 10))
        
        for i in range(4, 6):
            data = all_cards[i]
            icon, title, desc, color, frame = data[:5]
            badge = data[5] if len(data) > 5 else None
            self._create_optimized_card(row2, icon, title, desc, color, frame, badge)
    
    def _create_optimized_card(self, parent, icon, title, description, color, frame_name, badge=None):
        """Cria card individual otimizado com menos bindings"""
        
        # Card container
        card = tk.Frame(parent, bg='white', relief='solid', borderwidth=1)
        card.pack(side='left', padx=8, pady=5, fill='both', expand=True)
        
        # Hover otimizado - um binding por card
        def toggle_hover(event):
            if event.type == tk.EventType.Enter:
                card.config(relief='raised', borderwidth=2)
            else:
                card.config(relief='solid', borderwidth=1)
        
        card.bind("<Enter>", toggle_hover)
        card.bind("<Leave>", toggle_hover)
        
        # Barra colorida
        tk.Frame(card, bg=color, height=4).pack(fill='x')
        
        # Conteúdo
        content = tk.Frame(card, bg='white')
        content.pack(fill='both', expand=True, padx=15, pady=12)
        
        # Header (ícone + título) - alinhado verticalmente
        card_header = tk.Frame(content, bg='white')
        card_header.pack(fill='x', pady=(0, 6))
        
        # Ícone alinhado ao centro verticalmente
        icon_label = tk.Label(card_header, text=icon, font=("Arial", 24), bg='white')
        icon_label.pack(side='left', padx=(0, 8), anchor='center')
        
        # Container do título também centralizado
        title_container = tk.Frame(card_header, bg='white')
        title_container.pack(side='left', fill='both', expand=True, anchor='center')
        
        title_frame = tk.Frame(title_container, bg='white')
        title_frame.pack(anchor='w')
        
        tk.Label(
            title_frame, text=title, font=("Arial", 13, "bold"),
            bg='white', fg='#333'
        ).pack(side='left', anchor='center')
        
        if badge:
            tk.Label(
                title_frame, text=badge, font=("Arial", 6, "bold"),
                bg='#FF5722', fg='white', padx=4, pady=1
            ).pack(side='left', padx=(5, 0), anchor='center')
        
        # Descrição
        tk.Label(
            content, text=description, font=("Arial", 9),
            bg='white', fg='#666', wraplength=250, justify='left'
        ).pack(anchor='w', pady=(0, 10))
        
        # Botão com comando otimizado
        if frame_name:
            command = lambda f=frame_name: self.controller.show_frame(f)
        else:
            command = self._show_coming_soon
        
        # Cores pré-calculadas
        dark_color = self._darken_color(color)
        
        btn = tk.Button(
            content, text="Acessar →", command=command,
            bg=color, fg='white', font=("Arial", 9, "bold"),
            relief='flat', cursor='hand2', padx=18, pady=6,
            activebackground=dark_color, activeforeground='white'
        )
        btn.pack(anchor='w')
        
        # Hover do botão - otimizado
        def btn_hover(event):
            if event.type == tk.EventType.Enter:
                btn.config(bg=dark_color)
            else:
                btn.config(bg=color)
        
        btn.bind("<Enter>", btn_hover)
        btn.bind("<Leave>", btn_hover)
    
    def _create_footer(self, parent):
        """Cria rodapé"""
        footer = tk.Frame(parent, bg='#f5f5f5')
        footer.pack(fill='x', pady=(10, 20))
        
        tk.Label(
            footer,
            text="© 2025 - Sistema de Gestão de Aluguéis | Desenvolvido para facilitar sua gestão imobiliária",
            font=("Arial", 8), bg='#f5f5f5', fg='#999'
        ).pack()
    
    @staticmethod
    def _darken_color(hex_color):
        """Escurece cor (cache de cores seria ideal)"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = int(r * 0.8), int(g * 0.8), int(b * 0.8)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _show_coming_soon(self):
        """Mensagem de funcionalidade futura"""
        messagebox.showinfo(
            "Em Breve",
            "Esta funcionalidade estará disponível em breve!\n\n" +
            "Estamos trabalhando para trazer relatórios completos:\n" +
            "• Receitas e despesas\n" +
            "• Inadimplência\n" +
            "• Ocupação de imóveis\n" +
            "• Gráficos e análises"
        )