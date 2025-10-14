import tkinter as tk

def create_header(parent, controller, title="Contas de Energia"):
    """Cria o header reutilizável usado nas telas de contas."""
    header_frame = tk.Frame(parent, bg='#1565C0')
    header_frame.pack(fill='x')

    tk.Label(
        header_frame,
        text=title,
        font=("Arial", 20, "bold"),
        bg='#1565C0',
        fg='white'
    ).pack(pady=15)

    tk.Button(
        header_frame,
        text="← Voltar",
        command=lambda: controller.show_frame("home"),
        bg='#0D47A1',
        fg='white',
        font=("Arial", 10),
        relief='flat',
        cursor='hand2'
    ).place(x=10, y=10)

    return header_frame
