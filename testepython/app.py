import mysql.connector
import customtkinter as ctk
from tkinter import messagebox

# Variáveis globais para conexão
conn = None
cursor = None

def conectar_banco():
    """Tenta conectar com o banco de dados MySQL"""
    global conn, cursor
    try:
        # Conexão com MySQL (XAMPP)
        # Porta padrão do MySQL no XAMPP é 3306
        # Usuário padrão é 'root' e senha vazia
        conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="",
            database="testepython"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM login")
        rows = cursor.fetchall()
        print("Conexão com banco MySQL estabelecida com sucesso!")
        print(f"Encontrados {len(rows)} registros na tabela login")
        return True
    except Exception as e:
        print(f"Erro ao conectar com banco MySQL: {e}")
        messagebox.showwarning("Aviso", "Não foi possível conectar com o banco de dados MySQL.\nVerifique se o XAMPP está rodando e o MySQL está ativo.")
        return False

def fazer_login():
    """Função para fazer login"""
    usuario = campo_usuario.get()
    senha = campo_senha.get()
    
    if not usuario or not senha:
        messagebox.showerror("Erro", "Preencha todos os campos!")
        return
    
    if conn and cursor:
        try:
            # Verifica se o usuário e senha existem na tabela
            cursor.execute("SELECT * FROM login WHERE usuario=%s AND senha=%s", (usuario, senha))
            if cursor.fetchone():
                messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
                # Limpa os campos após login bem-sucedido
                campo_usuario.delete(0, 'end')
                campo_senha.delete(0, 'end')
            else:
                messagebox.showerror("Erro", "Usuário ou senha incorretos!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao verificar login: {e}")
    else:
        messagebox.showwarning("Aviso", "Banco de dados não disponível!")

def abrir_janela_cadastro():
    """Abre uma nova janela para cadastro de usuários"""
    janela_cadastro = ctk.CTkToplevel()
    janela_cadastro.title("Cadastro de Novo Usuário")
    janela_cadastro.geometry("600x700")
    janela_cadastro.resizable(True, True)  # Permite redimensionamento
    janela_cadastro.minsize(500, 600)  # Tamanho mínimo
    
    # Centraliza a janela
    janela_cadastro.transient(app)
    janela_cadastro.grab_set()
    
    # Título
    titulo = ctk.CTkLabel(janela_cadastro, text="CADASTRO DE USUÁRIO", font=("Arial", 20, "bold"))
    titulo.pack(pady=20)
    
    # Frame principal com scroll
    frame_principal = ctk.CTkScrollableFrame(janela_cadastro)
    frame_principal.pack(pady=10, padx=20, fill="both", expand=True)
    
    # Nome completo
    label_nome = ctk.CTkLabel(frame_principal, text="Nome Completo:")
    label_nome.pack(pady=(10,5))
    
    campo_nome = ctk.CTkEntry(frame_principal, placeholder_text="Digite seu nome completo", width=400)
    campo_nome.pack(pady=5)
    
    # Email
    label_email = ctk.CTkLabel(frame_principal, text="Email:")
    label_email.pack(pady=(15,5))
    
    campo_email = ctk.CTkEntry(frame_principal, placeholder_text="Digite seu email", width=400)
    campo_email.pack(pady=5)
    
    # Usuário
    label_usuario_cad = ctk.CTkLabel(frame_principal, text="Nome de Usuário:")
    label_usuario_cad.pack(pady=(15,5))
    
    campo_usuario_cad = ctk.CTkEntry(frame_principal, placeholder_text="Digite um nome de usuário", width=400)
    campo_usuario_cad.pack(pady=5)
    
    # Senha
    label_senha_cad = ctk.CTkLabel(frame_principal, text="Senha:")
    label_senha_cad.pack(pady=(15,5))
    
    campo_senha_cad = ctk.CTkEntry(frame_principal, placeholder_text="Digite uma senha", show="*", width=400)
    campo_senha_cad.pack(pady=5)
    
    # Confirmar senha
    label_confirma_senha = ctk.CTkLabel(frame_principal, text="Confirmar Senha:")
    label_confirma_senha.pack(pady=(15,5))
    
    campo_confirma_senha = ctk.CTkEntry(frame_principal, placeholder_text="Confirme sua senha", show="*", width=400)
    campo_confirma_senha.pack(pady=5)
    
    # Telefone
    label_telefone = ctk.CTkLabel(frame_principal, text="Telefone:")
    label_telefone.pack(pady=(15,5))
    
    campo_telefone = ctk.CTkEntry(frame_principal, placeholder_text="Digite seu telefone (opcional)", width=400)
    campo_telefone.pack(pady=5)
    
    def salvar_cadastro():
        """Função para salvar o cadastro no banco"""
        nome = campo_nome.get().strip()
        email = campo_email.get().strip()
        usuario = campo_usuario_cad.get().strip()
        senha = campo_senha_cad.get()
        confirma_senha = campo_confirma_senha.get()
        telefone = campo_telefone.get().strip()
        
        # Validações
        if not nome or not email or not usuario or not senha or not confirma_senha:
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
            return
        
        if senha != confirma_senha:
            messagebox.showerror("Erro", "As senhas não coincidem!")
            return
        
        if len(senha) < 6:
            messagebox.showerror("Erro", "A senha deve ter pelo menos 6 caracteres!")
            return
        
        if conn and cursor:
            try:
                # Verifica se o usuário já existe na tabela login
                cursor.execute("SELECT * FROM login WHERE usuario=%s", (usuario,))
                if cursor.fetchone():
                    messagebox.showerror("Erro", "Nome de usuário já existe!")
                    return
                
                # Verifica se o email já existe na tabela cadastro
                cursor.execute("SELECT * FROM cadastro WHERE email=%s", (email,))
                if cursor.fetchone():
                    messagebox.showerror("Erro", "Email já cadastrado!")
                    return
                
                # Primeiro, insere na tabela login (usuario e senha)
                cursor.execute("INSERT INTO login (usuario, senha) VALUES (%s, %s)", (usuario, senha))
                
                # Depois, insere na tabela cadastro (apenas nome, email, telefone)
                cursor.execute("""
                    INSERT INTO cadastro (nome, email, telefone) 
                    VALUES (%s, %s, %s)
                """, (nome, email, telefone))
                
                conn.commit()
                messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
                janela_cadastro.destroy()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao cadastrar usuário: {e}")
                print(f"Erro detalhado: {e}")
                # Em caso de erro, faz rollback para não deixar dados inconsistentes
                conn.rollback()
        else:
            messagebox.showwarning("Aviso", "Banco de dados não disponível!")
    
    def cancelar_cadastro():
        """Função para cancelar o cadastro"""
        janela_cadastro.destroy()
    
    # Frame para botões
    frame_botoes = ctk.CTkFrame(frame_principal)
    frame_botoes.pack(pady=30, fill="x")
    
    # Botões
    btn_salvar = ctk.CTkButton(frame_botoes, text="Salvar Cadastro", command=salvar_cadastro, width=180, height=40)
    btn_salvar.pack(side="left", padx=20, pady=20)
    
    btn_cancelar = ctk.CTkButton(frame_botoes, text="Cancelar", command=cancelar_cadastro, width=180, height=40)
    btn_cancelar.pack(side="right", padx=20, pady=20)

# Interface gráfica principal
ctk.set_appearance_mode('dark')

app = ctk.CTk()
app.title('Sistema de Login - MySQL')
app.geometry('400x400')

# Tenta conectar com o banco
conectar_banco()

label_usuario = ctk.CTkLabel(app, text='Usuário')
label_usuario.pack(pady=10)

campo_usuario = ctk.CTkEntry(app, placeholder_text='Digite seu usuário')
campo_usuario.pack(pady=10)

label_senha = ctk.CTkLabel(app, text='Senha')
label_senha.pack(pady=10)

campo_senha = ctk.CTkEntry(app, placeholder_text='Digite sua senha', show='*')
campo_senha.pack(pady=10)

ctk.CTkButton(app, text='Login', command=fazer_login).pack(pady=10)
ctk.CTkButton(app, text='Cadastro', command=abrir_janela_cadastro).pack(pady=10)

app.mainloop()

# Fecha a conexão quando o programa terminar
if conn:
    conn.close()

