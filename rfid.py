import serial
import time
import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import scrolledtext
from datetime import datetime
import mysql.connector
from mysql.connector import Error

# =====================================================
# BANCO (já existe, não será modificado aqui)
# =====================================================
def conectar_banco():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_rfid"
        )
    except Error as e:
        print(f"[DB] Erro ao conectar: {e}")
        return None

def buscar_ferramenta_por_tag(codigo_tag):
    conn = conectar_banco()
    if not conn:
        return None, None
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT f.id_ferramentas, f.nome
            FROM tb_rfid_tags t
            JOIN tb_ferramentas f ON t.id_ferramenta = f.id_ferramentas
            WHERE t.codigo_tag = %s
            LIMIT 1
        """, (codigo_tag,))
        res = cur.fetchone()
        cur.close()
        conn.close()
        if res:
            return res[0], res[1]
        return None, None
    except Error as e:
        print(f"[DB] Erro buscar_ferramenta_por_tag: {e}")
        return None, None

def registrar_movimentacao(id_ferramenta, local, observacao=None, id_usuario=None):
    conn = conectar_banco()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO tb_movimentacoes (id_usuario, id_ferramentas, data_retirada, data_devolucao, observacao)
            VALUES (%s, %s, NOW(), NOW(), %s)
        """, (id_usuario or 1, id_ferramenta, observacao or f"Leitura de {local}"))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Error as e:
        print(f"[DB] Erro registrar_movimentacao: {e}")
        return False

def salvar_tag_no_banco(nome, codigo):
    conn = conectar_banco()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO tb_ferramentas (nome) VALUES (%s)", (nome,))
        id_ferramenta = cur.lastrowid
        cur.execute("INSERT INTO tb_rfid_tags (codigo_tag, id_ferramenta) VALUES (%s, %s)", (codigo, id_ferramenta))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Error as e:
        print(f"[DB] Erro ao salvar TAG: {e}")
        return False


# =====================================================
# VARIÁVEIS GLOBAIS
# =====================================================
porta1 = "COM5"
porta2 = "COM6"
baud = 115200
TAG_ALVO = "10000000000000000000000A"
NOME_TAG = "Chave de Fenda"
INTERVALO_EXIBICAO = 5.0

running = [False]
last_display = {"porta1": 0.0, "porta2": 0.0}
pending = {"porta1": False, "porta2": False}
pending_local = {"porta1": None, "porta2": None}
ultimo_registrado = {"Sala de Ferramentas": None, "Sala dos Tornos": None}

TAGS_CADASTRADAS = []
USUARIOS = []
USUARIO_ATUAL = [None]


# =====================================================
# FUNÇÕES DE LOGIN E CADASTRO
# =====================================================
def mostrar_login():
    for f in frame_container.winfo_children():
        f.pack_forget()
    frame_login.pack(fill="both", expand=True)

def mostrar_cadastro_usuario():
    frame_login.pack_forget()
    frame_cadastro_usuario.pack(fill="both", expand=True)

def registrar_usuario():
    nome = entrada_nome_user.get().strip()
    usuario = entrada_usuario_user.get().strip()
    senha = entrada_senha_user.get().strip()

    if not nome or not usuario or not senha:
        label_status_cadastro_user.configure(text="Preencha todos os campos!", text_color="red")
        return

    conn = conectar_banco()
    if not conn:
        label_status_cadastro_user.configure(text="Erro ao conectar com o banco!", text_color="red")
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT id_usuario FROM tb_usuario WHERE matricula = %s", (usuario,))
        if cur.fetchone():
            label_status_cadastro_user.configure(text="Usuário já existe!", text_color="red")
            cur.close()
            conn.close()
            return

        cur.execute("""
            INSERT INTO tb_usuario (nome, cargo, matricula, senha, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (nome, "Operador", usuario, senha, "Em atividade"))
        conn.commit()
        cur.close()
        conn.close()
        label_status_cadastro_user.configure(text="Cadastro realizado com sucesso!", text_color="lightgreen")

        entrada_nome_user.delete(0, tk.END)
        entrada_usuario_user.delete(0, tk.END)
        entrada_senha_user.delete(0, tk.END)

    except Error as e:
        print(f"[DB] Erro registrar_usuario: {e}")
        label_status_cadastro_user.configure(text="Erro ao salvar no banco!", text_color="red")

def login_usuario():
    usuario = entrada_usuario_login.get().strip()
    senha = entrada_senha_login.get().strip()

    if not usuario or not senha:
        label_status_login.configure(text="Preencha todos os campos!", text_color="red")
        return

    conn = conectar_banco()
    if not conn:
        label_status_login.configure(text="Erro ao conectar com o banco!", text_color="red")
        return

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM tb_usuario WHERE matricula = %s AND senha = %s", (usuario, senha))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            USUARIO_ATUAL[0] = user
            frame_login.pack_forget()
            frame_inicial.pack(fill="both", expand=True)
        else:
            label_status_login.configure(text="Usuário ou senha incorretos!", text_color="red")

    except Error as e:
        print(f"[DB] Erro login_usuario: {e}")
        label_status_login.configure(text="Erro ao consultar banco!", text_color="red")


# =====================================================
# INTERFACE INICIAL (LOGIN)
# =====================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

janela_inicial = ctk.CTk()
janela_inicial.attributes('-fullscreen', True)
janela_inicial.title("Sistema RFID com Login")

frame_container = ctk.CTkFrame(janela_inicial)
frame_container.pack(fill="both", expand=True)

# TELA DE LOGIN
frame_login = ctk.CTkFrame(frame_container)

titulo_login = ctk.CTkLabel(frame_login, text="Login de Usuário", font=("Arial", 38, "bold"))
titulo_login.pack(pady=60)

entrada_usuario_login = ctk.CTkEntry(frame_login, placeholder_text="Usuário", width=400, height=40, font=("Arial", 16))
entrada_usuario_login.pack(pady=10)

entrada_senha_login = ctk.CTkEntry(frame_login, placeholder_text="Senha", show="*", width=400, height=40, font=("Arial", 16))
entrada_senha_login.pack(pady=10)

botao_login = ctk.CTkButton(frame_login, text="Entrar", command=login_usuario, width=200, height=45, fg_color="#27ae60", hover_color="#219150")
botao_login.pack(pady=15)

botao_ir_cadastro = ctk.CTkButton(frame_login, text="Criar nova conta", command=mostrar_cadastro_usuario, width=200, height=40, fg_color="#2980b9", hover_color="#1f5f8a")
botao_ir_cadastro.pack(pady=10)

# === Botão Admin ===
botao_admin = ctk.CTkButton(frame_login, text="Entrar como Administrador", command=lambda: login_admin(), width=260, height=45, fg_color="#8e44ad", hover_color="#6c3483")
botao_admin.pack(pady=10)

label_status_login = ctk.CTkLabel(frame_login, text="", font=("Arial", 16))
label_status_login.pack(pady=10)

# TELA DE CADASTRO DE USUÁRIO
frame_cadastro_usuario = ctk.CTkFrame(frame_container)

titulo_cadastro_user = ctk.CTkLabel(frame_cadastro_usuario, text="Cadastro de Novo Usuário", font=("Arial", 32, "bold"))
titulo_cadastro_user.pack(pady=40)

entrada_nome_user = ctk.CTkEntry(frame_cadastro_usuario, placeholder_text="Nome Completo", width=400, height=40, font=("Arial", 16))
entrada_nome_user.pack(pady=10)

entrada_usuario_user = ctk.CTkEntry(frame_cadastro_usuario, placeholder_text="Usuário", width=400, height=40, font=("Arial", 16))
entrada_usuario_user.pack(pady=10)

entrada_senha_user = ctk.CTkEntry(frame_cadastro_usuario, placeholder_text="Senha", show="*", width=400, height=40, font=("Arial", 16))
entrada_senha_user.pack(pady=10)

botao_registrar_user = ctk.CTkButton(frame_cadastro_usuario, text="Registrar", command=registrar_usuario, width=200, height=45, fg_color="#27ae60", hover_color="#219150")
botao_registrar_user.pack(pady=15)

botao_voltar_login = ctk.CTkButton(frame_cadastro_usuario, text="Voltar ao Login", command=mostrar_login, width=200, height=45, fg_color="#c0392b", hover_color="#992d22")
botao_voltar_login.pack(pady=15)

label_status_cadastro_user = ctk.CTkLabel(frame_cadastro_usuario, text="", font=("Arial", 16))
label_status_cadastro_user.pack(pady=10)

# =====================================================
# ============ ÁREA DO ADMINISTRADOR ==================
# =====================================================

def login_admin():
    usuario = entrada_usuario_login.get().strip()
    senha = entrada_senha_login.get().strip()

    if not usuario or not senha:
        label_status_login.configure(text="Preencha todos os campos!", text_color="red")
        return

    conn = conectar_banco()
    if not conn:
        label_status_login.configure(text="Erro ao conectar com o banco!", text_color="red")
        return

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM tb_admin WHERE usuario = %s AND senha = %s", (usuario, senha))
        admin = cur.fetchone()
        cur.close()
        conn.close()

        if admin:
            frame_login.pack_forget()
            abrir_painel_admin()
        else:
            label_status_login.configure(text="Usuário ou senha incorretos!", text_color="red")
    except Error as e:
        print(f"[DB] Erro login_admin: {e}")
        label_status_login.configure(text="Erro ao consultar banco!", text_color="red")


def abrir_painel_admin():
    for f in frame_container.winfo_children():
        f.pack_forget()

    global frame_admin
    frame_admin = ctk.CTkFrame(frame_container)
    frame_admin.pack(fill="both", expand=True)

    titulo_admin = ctk.CTkLabel(frame_admin, text="Painel do Administrador", font=("Arial", 38, "bold"))
    titulo_admin.pack(pady=40)

    botoes_frame = ctk.CTkFrame(frame_admin)
    botoes_frame.pack(pady=10)

    botao_atualizar = ctk.CTkButton(botoes_frame, text="Atualizar Dados", command=lambda: [carregar_movimentacoes(), carregar_usuarios()],
                                    width=200, height=45, fg_color="#27ae60", hover_color="#219150")
    botao_atualizar.pack(side="left", padx=10)

    botao_voltar = ctk.CTkButton(botoes_frame, text="Sair do Painel", command=mostrar_login,
                                 width=200, height=45, fg_color="#c0392b", hover_color="#992d22")
    botao_voltar.pack(side="left", padx=10)

    label_mov = ctk.CTkLabel(frame_admin, text="Últimas 5 Movimentações", font=("Arial", 28, "bold"))
    label_mov.pack(pady=10)

    global text_mov
    text_mov = scrolledtext.ScrolledText(frame_admin, font=("Consolas", 14), bg="#A3A1A1", height=8)
    text_mov.pack(fill="x", padx=40, pady=10)

    label_users = ctk.CTkLabel(frame_admin, text="Usuários Cadastrados", font=("Arial", 28, "bold"))
    label_users.pack(pady=10)

    global text_users
    text_users = scrolledtext.ScrolledText(frame_admin, font=("Consolas", 14), bg="#A3A1A1", height=12)
    text_users.pack(fill="x", padx=40, pady=10)

    carregar_movimentacoes()
    carregar_usuarios()


def carregar_movimentacoes():
    conn = conectar_banco()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT m.id_mov, u.nome, f.nome, m.data_retirada, m.data_devolucao, m.observacao
            FROM tb_movimentacoes m
            JOIN tb_usuario u ON m.id_usuario = u.id_usuario
            JOIN tb_ferramentas f ON m.id_ferramentas = f.id_ferramentas
            ORDER BY m.data_retirada DESC
            LIMIT 5
        """)
        dados = cur.fetchall()
        cur.close()
        conn.close()

        text_mov.delete(1.0, tk.END)
        for d in dados:
            text_mov.insert(tk.END, f"ID: {d[0]} | Usuário: {d[1]} | Ferramenta: {d[2]} | Retirada: {d[3]} | Devolução: {d[4]} | Obs: {d[5]}\n")
        text_mov.insert(tk.END, "-"*100 + "\n")

    except Error as e:
        print(f"[DB] Erro carregar_movimentacoes: {e}")


def carregar_usuarios():
    conn = conectar_banco()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("SELECT id_usuario, nome, cargo, status, matricula FROM tb_usuario")
        dados = cur.fetchall()
        cur.close()
        conn.close()

        text_users.delete(1.0, tk.END)
        for d in dados:
            text_users.insert(tk.END, f"ID: {d[0]} | Nome: {d[1]} | Cargo: {d[2]} | Status: {d[3]} | Usuário: {d[4]}\n")
        text_users.insert(tk.END, "-"*100 + "\n")

    except Error as e:
        print(f"[DB] Erro carregar_usuarios: {e}")


# =====================================================
# MENU INICIAL DE USUÁRIO
# =====================================================
frame_inicial = ctk.CTkFrame(frame_container)
titulo_inicial = ctk.CTkLabel(frame_inicial, text="Bem-vindo ao Sistema RFID", font=("Arial", 38, "bold"))
titulo_inicial.pack(pady=80)

# =====================================================
# EXECUÇÃO
# =====================================================
mostrar_login()
janela_inicial.mainloop()
