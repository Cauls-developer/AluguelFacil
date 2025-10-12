import tkinter as tk
from tkinter import ttk

class HomeView(tk.Frame):
    """Tela inicial com menu principal"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, bg='#f0f0f0')
        self.controller = controller
        
        # Título
        title = tk.Label(
            self, 
            text="Sistema de Gestão de Aluguéis",
            font=("Arial", 28, "bold"),
            bg='#f0f0f0',
            fg='#0D47A1'
        )
        title.pack(pady=50)
        
        # Subtítulo
        subtitle = tk.Label(
            self,
            text="Selecione uma opção abaixo",
            font=("Arial", 14),
            bg='#f0f0f0',
            fg='#555'
        )
        subtitle.pack(pady=10)
        
        # Frame para os botões
        button_frame = tk.Frame(self, bg='#f0f0f0')
        button_frame.pack(pady=40)
        
        # Estilo dos botões
        button_style = {
            'font': ("Arial", 12, "bold"),
            'width': 30,
            'height': 2,
            'bg': '#1565C0',
            'fg': 'white',
            'activebackground': '#0D47A1',
            'activeforeground': 'white',
            'relief': 'flat',
            'cursor': 'hand2'
        }
        
        # Botão Registro de Casas
        btn_casas = tk.Button(
            button_frame,
            text="📋 Registro de Casas",
            command=lambda: controller.show_frame("registro_casas"),
            **button_style
        )
        btn_casas.pack(pady=15)
        
        # Botão Registro de Inquilinos
        btn_inquilinos = tk.Button(
            button_frame,
            text="👤 Registro de Inquilinos",
            command=lambda: controller.show_frame("registro_inquilinos"),
            **button_style
        )
        btn_inquilinos.pack(pady=15)
        
        # Botão Gerar Conta de Energia
        btn_conta = tk.Button(
            button_frame,
            text="⚡ Gerar Conta de Energia",
            command=lambda: controller.show_frame("gerar_conta_energia"),
            **button_style
        )
        btn_conta.pack(pady=15)
        
        # Rodapé
        footer = tk.Label(
            self,
            text="© 2025 - Sistema de Gestão de Aluguéis",
            font=("Arial", 9),
            bg='#f0f0f0',
            fg='#999'
        )
        footer.pack(side='bottom', pady=20)