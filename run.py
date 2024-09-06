from app import create_app, db
from app.models import Usuario, Casa, Conta, Pagamento, Nota, ItemNota

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'Usuario': Usuario, 
        'Casa': Casa, 
        'Conta': Conta, 
        'Pagamento': Pagamento, 
        'Nota': Nota, 
        'ItemNota': ItemNota
    }

if __name__ == '__main__':
    app.run(debug=True)