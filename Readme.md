# Sistema de Gestão de Aluguéis

Este é um sistema de gestão de aluguéis desenvolvido em Python usando o framework Flask. O sistema permite o gerenciamento de casas, inquilinos, contas de água e luz, pagamentos e emissão de notas.

## Funcionalidades

- Cadastro e gerenciamento de usuários (inquilinos e administradores)
- Cadastro e gerenciamento de casas
- Registro de contas de água e luz
- Emissão de notas de aluguel
- Registro de pagamentos
- Geração de relatórios de inadimplência
- Envio automático de e-mails com notas

## Requisitos

- Python 3.8+
- Flask
- SQLAlchemy
- Flask-WTF
- ReportLab
- (outras dependências conforme necessário)

## Instalação

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/sistema-gestao-alugueis.git
   cd sistema-gestao-alugueis
   ```

2. Crie um ambiente virtual e ative-o:
   ```
   python -m venv venv
   source venv/bin/activate  # No Windows use `venv\Scripts\activate`
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   Crie um arquivo `.env` na raiz do projeto e adicione:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=sua_chave_secreta_aqui
   DATABASE_URI=sqlite:///seu_banco_de_dados.db
   EMAIL_REMETENTE=seu_email@gmail.com
   EMAIL_SENHA=sua_senha_de_app
   ```

5. Inicialize o banco de dados:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. Execute o aplicativo:
   ```
   flask run
   ```

O aplicativo estará disponível em `http://localhost:5000`.

## Estrutura do Projeto

- `app/`: Diretório principal do aplicativo
  - `models.py`: Definições dos modelos de dados
  - `views.py`: Rotas e lógica de visualização
  - `forms.py`: Definições de formulários
  - `utils.py`: Funções utilitárias
- `static/`: Arquivos estáticos (CSS, JS, imagens)
- `templates/`: Templates HTML
- `migrations/`: Migrações do banco de dados
- `config.py`: Configurações do aplicativo
- `run.py`: Script para executar o aplicativo

## Uso

1. Acesse o sistema através do navegador
2. Faça login como administrador
3. Adicione casas e registre inquilinos
4. Registre contas de água e luz
5. Emita notas de aluguel
6. Registre pagamentos
7. Gere relatórios conforme necessário

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para submeter pull requests.

## Licença

Este projeto está licenciado sob a licença MIT.