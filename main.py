import tkinter as tk
from app.data.database.base import DatabaseConfig


class RentalManagementApp(tk.Tk):
    """Aplicação principal de gerenciamento de aluguéis"""
    
    def __init__(self):
        super().__init__()
        
        # Configurações da janela
        self.title("Sistema de Gestão de Aluguéis")
        self.geometry("1200x800")
        self.state('zoomed')  # Maximizar janela no Windows
        
        # Configurar banco de dados
        self.db_config = DatabaseConfig()
        self.db_config.initialize()
        
        # Container para as views
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        # Dicionário de frames
        self.frames = {}
        
        # Mostrar tela inicial
        self.show_frame("home")
    
    def show_frame(self, frame_name):
        """Mostra o frame especificado, criando-o se necessário"""
        # Se o frame já existe, apenas mostra
        if frame_name in self.frames:
            frame = self.frames[frame_name]
            frame.tkraise()
            return
        
        # Senão, cria o frame sob demanda
        frame = None
        
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
        
        elif frame_name == "gestao_contratos":
            from app.presentation.views.contract_view import ContractView
            frame = ContractView(self.container, self)
        
        else:
            print(f"Frame '{frame_name}' não encontrado!")
            return
        
        # Armazena e posiciona o frame
        if frame:
            self.frames[frame_name] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)
            frame.tkraise()
    
    def get_session(self):
        """Retorna uma nova sessão do banco de dados"""
        return self.db_config.get_session()


if __name__ == "__main__":
    app = RentalManagementApp()
    app.mainloop()