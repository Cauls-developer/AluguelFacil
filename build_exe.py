import PyInstaller.__main__
import os
import shutil

print("🔨 Criando executável do AluguelFácil...")

# Limpa builds anteriores
for folder in ['build', 'dist', 'installer']:
    if os.path.exists(folder):
        shutil.rmtree(folder)

os.makedirs('installer', exist_ok=True)

# Gera o executável
PyInstaller.__main__.run([
    'main.py',
    '--name=AluguelFacil',
    '--onefile',
    '--windowed',
    '--noconfirm',
    '--add-data=.env;.',
    '--hidden-import=tkinter',
    '--hidden-import=reportlab',
    '--hidden-import=sqlalchemy',
    '--hidden-import=tkcalendar',
    '--collect-all=reportlab',
])

# Copia para pasta installer
shutil.copy2('dist/AluguelFacil.exe', 'installer/AluguelFacil.exe')

# Cria .env padrão
with open('installer/.env', 'w', encoding='utf-8') as f:
    f.write('''# Configurações AluguelFácil
LOCADOR_NOME=Nome do Proprietário
LOCADOR_CPF=000.000.000-00
LOCADOR_RG=00.000.000-0
LOCADOR_ENDERECO=Endereço Completo
TITULAR_CONTA=Nome para Recebimento
PIX=(00) 00000-0000
BANCO=Nome do Banco
''')

print("✅ Executável criado em: installer/AluguelFacil.exe")
print("✅ Configuração padrão criada em: installer/.env")