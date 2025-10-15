import tkinter as tk
from tkinter import messagebox
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from app.data.database.base import DatabaseConfig, Base


def get_app_data_dir():
    """Retorna o diretório de dados do aplicativo"""
    if getattr(sys, 'frozen', False):
        # Executável - usa AppData do usuário
        appdata = os.environ.get('APPDATA')
        if appdata:
            app_folder = Path(appdata) / 'AluguelFacil'
        else:
            app_folder = Path.home() / '.aluguel_facil'
        
        app_folder.mkdir(parents=True, exist_ok=True)
        return app_folder
    else:
        # Desenvolvimento - usa pasta atual
        return Path.cwd()


def get_env_path():
    """Retorna o caminho do arquivo .env"""
    data_dir = get_app_data_dir()
    env_path = data_dir / '.env'
    
    # Se não existe, cria um padrão
    if not env_path.exists():
        print("📝 Criando arquivo de configuração padrão...")
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write('''# ===== CONFIGURAÇÕES DO ALUGUEL FÁCIL =====
# Edite este arquivo com seus dados

# Dados do Proprietário
LOCADOR_NOME=Seu Nome Completo
LOCADOR_CPF=000.000.000-00
LOCADOR_RG=00.000.000-0
LOCADOR_ENDERECO=Seu Endereço Completo

# Dados Bancários para Recebimento
TITULAR_CONTA=Seu Nome
PIX=(00) 00000-0000
BANCO=Nome do Banco

# ===== NÃO EDITAR ABAIXO =====
# Configurações do sistema
''')
        print(f"✅ Arquivo .env criado em: {env_path}")
        print("⚠️  Configure seus dados antes de usar o sistema!")
    
    return env_path


def open_data_folder():
    """Abre a pasta de dados do aplicativo"""
    data_dir = get_app_data_dir()
    
    try:
        if sys.platform == 'win32':
            os.startfile(data_dir)
        elif sys.platform == 'darwin':  # macOS
            import subprocess
            subprocess.run(['open', data_dir])
        else:  # Linux
            import subprocess
            subprocess.run(['xdg-open', data_dir])
        return True
    except Exception as e:
        print(f"❌ Erro ao abrir pasta: {e}")
        return False


class RentalManagementApp(tk.Tk):
    """Aplicação principal de gerenciamento de aluguéis"""
    
    def __init__(self):
        super().__init__()
        
        # Carrega configurações do .env
        env_path = get_env_path()
        load_dotenv(dotenv_path=env_path)
        print(f"📄 Configurações carregadas de: {env_path}")
        
        # Configurações da janela
        self.title("Sistema de Gestão de Aluguéis - AluguelFácil v1.0")
        self.iconbitmap(default='')  # Remove ícone padrão (pode adicionar um customizado)
        
        # Configurar estilo
        self.configure(bg='#f5f5f5')
        
        # Centralizar janela
        window_width = 1280
        window_height = 820
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Tamanho mínimo
        self.minsize(1024, 700)
        
        # Configurar banco de dados
        print("\n" + "="*60)
        print("🚀 Iniciando AluguelFácil...")
        print("="*60)
        
        try:
            self.db_config = DatabaseConfig()
            self.db_config.initialize()
            
            # Importa todos os modelos
            from app.data.models.house import Casa
            from app.data.models.Tenant import Inquilino
            from app.data.models.consumption import Consumo
            from app.data.models.contract import Contrato
            from app.data.models.receipt import Recibo
            
            # Cria todas as tabelas
            Base.metadata.create_all(self.db_config.engine)
            
            db_location = self.db_config.get_database_location()
            print(f"📊 Banco de dados: {db_location}")
            print("✅ Sistema inicializado com sucesso!")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"❌ ERRO ao inicializar banco de dados: {e}")
            messagebox.showerror(
                "Erro Fatal",
                f"Não foi possível inicializar o banco de dados:\n\n{str(e)}\n\n"
                "O programa será encerrado."
            )
            self.destroy()
            return
        
        # Criar menu
        self.create_menu()
        
        # Container para as views
        self.container = tk.Frame(self, bg='#f5f5f5')
        self.container.pack(fill="both", expand=True)
        
        # Dicionário de frames
        self.frames = {}
        
        # Mostrar tela inicial
        self.show_frame("home")
        
        # Verificar se é primeira execução
        self.check_first_run()
    
    def create_menu(self):
        """Cria a barra de menu"""
        menubar = tk.Menu(self)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="🏠 Início", command=lambda: self.show_frame("home"))
        file_menu.add_separator()
        file_menu.add_command(label="📂 Abrir Pasta de Dados", command=self.open_data_folder_menu)
        file_menu.add_command(label="⚙️ Configurações", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Sair", command=self.quit_app)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="ℹ️ Sobre", command=self.show_about)
        help_menu.add_command(label="📍 Localização dos Dados", command=self.show_data_location)
        help_menu.add_command(label="💾 Fazer Backup", command=self.show_backup_info)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        
        self.config(menu=menubar)
    
    def open_data_folder_menu(self):
        """Abre a pasta de dados via menu"""
        if not open_data_folder():
            messagebox.showerror(
                "Erro",
                "Não foi possível abrir a pasta de dados.\n\n"
                f"Abra manualmente: {get_app_data_dir()}"
            )
    
    def open_settings(self):
        """Abre o arquivo de configurações"""
        env_path = get_env_path()
        
        try:
            if sys.platform == 'win32':
                os.startfile(env_path)
            else:
                messagebox.showinfo(
                    "Configurações",
                    f"Edite o arquivo:\n\n{env_path}\n\n"
                    "Reinicie o programa após salvar as alterações."
                )
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir as configurações:\n{e}")
    
    def show_about(self):
        """Mostra informações sobre o sistema"""
        messagebox.showinfo(
            "Sobre o AluguelFácil",
            "AluguelFácil v1.0.0\n\n"
            "Sistema completo de gestão de aluguéis\n\n"
            "Desenvolvido com Python e Tkinter\n"
            "© 2025 - Todos os direitos reservados\n\n"
            "Funcionalidades:\n"
            "✓ Gestão de Imóveis\n"
            "✓ Cadastro de Inquilinos\n"
            "✓ Contratos de Locação\n"
            "✓ Recibos de Pagamento\n"
            "✓ Contas de Energia\n"
            "✓ Geração de PDFs"
        )
    
    def show_data_location(self):
        """Mostra a localização dos dados"""
        data_dir = get_app_data_dir()
        db_path = data_dir / 'casas_consumo.db'
        env_path = data_dir / '.env'
        pdf_path = data_dir / 'PDFs'
        
        messagebox.showinfo(
            "Localização dos Dados",
            f"📂 Pasta principal:\n{data_dir}\n\n"
            f"📊 Banco de dados:\n{db_path}\n\n"
            f"⚙️ Configurações:\n{env_path}\n\n"
            f"📄 PDFs gerados:\n{pdf_path}\n\n"
            "💡 Dica: Faça backup regular da pasta principal!"
        )
    
    def show_backup_info(self):
        """Mostra instruções de backup"""
        data_dir = get_app_data_dir()
        
        result = messagebox.askyesno(
            "Backup dos Dados",
            "Para fazer backup dos seus dados:\n\n"
            "1. Feche o AluguelFácil\n"
            "2. Copie toda a pasta:\n"
            f"   {data_dir}\n"
            "3. Cole em um local seguro\n"
            "   (Nuvem, HD externo, etc.)\n\n"
            "Deseja abrir a pasta agora para fazer o backup?"
        )
        
        if result:
            open_data_folder()
    
    def check_first_run(self):
        """Verifica se é a primeira execução e mostra guia"""
        env_path = get_env_path()
        
        # Lê o .env para verificar se está com valores padrão
        with open(env_path, 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        if 'Seu Nome Completo' in env_content or 'Seu Nome' in env_content:
            # Primeira execução - mostra guia
            result = messagebox.showinfo(
                "Bem-vindo ao AluguelFácil! 🎉",
                "Obrigado por usar o AluguelFácil!\n\n"
                "⚠️ IMPORTANTE - Primeira Execução:\n\n"
                "Antes de usar o sistema, você precisa configurar\n"
                "seus dados pessoais no arquivo de configuração.\n\n"
                "Clique em OK para abrir as configurações.\n\n"
                "Configure:\n"
                "• Seu nome e documentos\n"
                "• Dados bancários\n"
                "• Chave PIX\n\n"
                "Depois reinicie o programa."
            )
            
            # Abre as configurações
            self.open_settings()
    
    def quit_app(self):
        """Encerra o aplicativo com confirmação"""
        result = messagebox.askyesno(
            "Sair",
            "Deseja realmente sair do AluguelFácil?",
            icon='question'
        )
        if result:
            print("\n👋 Encerrando AluguelFácil...")
            self.destroy()
    
    def show_frame(self, frame_name):
        """Mostra o frame especificado, criando-o se necessário"""
        # Se o frame já existe, apenas mostra
        if frame_name in self.frames:
            frame = self.frames[frame_name]
            frame.tkraise()
            return
        
        # Senão, cria o frame sob demanda
        frame = None
        
        try:
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

            elif frame_name == "gestao_recibos":
                from app.presentation.views.receipt_view import ReceiptView
                frame = ReceiptView(self.container, self)

            else:
                print(f"⚠️  Frame '{frame_name}' não encontrado!")
                messagebox.showwarning("Aviso", f"Tela '{frame_name}' não encontrada!")
                return
            
        except Exception as e:
            print(f"❌ Erro ao criar frame '{frame_name}': {e}")
            messagebox.showerror(
                "Erro",
                f"Não foi possível abrir a tela:\n\n{str(e)}"
            )
            return
        
        # Armazena e posiciona o frame
        if frame:
            self.frames[frame_name] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)
            frame.tkraise()
    
    def get_session(self):
        """Retorna uma nova sessão do banco de dados"""
        return self.db_config.get_session()


def main():
    """Função principal"""
    try:
        app = RentalManagementApp()
        app.mainloop()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        messagebox.showerror(
            "Erro Fatal",
            f"O programa encontrou um erro fatal:\n\n{str(e)}\n\n"
            "O programa será encerrado."
        )


if __name__ == "__main__":
    main()