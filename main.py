import tkinter as tk
from tkinter import ttk
from app.presentation.views.home_view import HomeView
from app.data.database.base import DatabaseConfig

from app.data.models.Tenant import Inquilino
from app.data.models.house import Casa
from app.data.models.consumption import Consumo

class MainApplication(tk.Tk):
    """Aplicação principal com gerenciamento de telas"""
    
    def __init__(self):
        super().__init__()
        
        # Configurações da janela
        self.title("Sistema de Gestão de Aluguéis")
        self.geometry("1000x700")
        self.configure(bg='#f0f0f0')
        
        # Inicializar banco de dados
        self.db_config = DatabaseConfig()
        self.db_config.initialize()
        
        # Container principal
        self.container = tk.Frame(self, bg='#f0f0f0')
        self.container.pack(fill="both", expand=True)
        
        # Dicionário de views
        self.frames = {}
        self.current_frame = None
        
        # Iniciar com a tela home
        self.show_frame("home")
    
    def show_frame(self, frame_name, **kwargs):
        """Exibe uma tela específica"""
        # Destruir frame atual se existir
        if self.current_frame:
            self.current_frame.destroy()
        
        # Criar nova frame baseado no nome
        if frame_name == "home":
            from app.presentation.views.home_view import HomeView
            frame = HomeView(self.container, self)
        elif frame_name == "registro_casas":
            from app.presentation.views.house_register_view import HouseRegisterView
            frame = HouseRegisterView(self.container, self)
        elif frame_name == "registro_inquilinos":
            from app.presentation.views.tenant_register_view import TenantRegisterView
            frame = TenantRegisterView(self.container, self)
        elif frame_name == "gerar_conta_energia":
            from app.presentation.views.electricity_bill_view import ElectricityBillView
            frame = ElectricityBillView(self.container, self)
        else:
            return
        
        frame.pack(fill="both", expand=True)
        self.current_frame = frame
    
    def get_session(self):
        """Retorna uma sessão do banco de dados"""
        return self.db_config.get_session()


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()