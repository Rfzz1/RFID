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
# VARIÁVEIS GLOBAIS (únicas definições)
# =====================================================
capturando_leitura = [False]   # controle de leitura (mutável dentro de threads)
threads_leitura = []           # lista de threads de leitura
porta1 = "COM5"
porta2 = "COM6"
baud = 115200
USUARIO_ATUAL = [None]

# =====================================================
# BANCO (sem alterações)
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
# UI - configuração geral
# =====================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

janela_inicial = ctk.CTk()
janela_inicial.attributes('-fullscreen', True)
janela_inicial.title("Sistema RFID com Login")

frame_container = ctk.CTkFrame(janela_inicial)
frame_container.pack(fill="both", expand=True)

# fontes e tamanhos
FONTE_TITULO = ("Arial", 48, "bold")
FONTE_TEXTO = ("Arial", 22)
FONTE_INPUT = ("Arial", 20)
ALTURA_INPUT = 55
LARGURA_INPUT = 500
ALTURA_BOTAO = 60
LARGURA_BOTAO = 280

# =====================================================
# Funções utilitárias
# =====================================================
def normalizar_tag(raw):
    return "".join(ch for ch in raw if ch.isalnum()).upper()

# =====================================================
# TELA DE LOGIN / CADASTRO (mesma lógica sua)
# (mantive suas funções: mostrar_login, registrar_usuario, login_usuario, etc.)
# =====================================================

# -- tela login
frame_login = ctk.CTkFrame(frame_container)
titulo_login = ctk.CTkLabel(frame_login, text="Login de Usuário", font=FONTE_TITULO)
titulo_login.pack(pady=80)
entrada_usuario_login = ctk.CTkEntry(frame_login, placeholder_text="Usuário", width=LARGURA_INPUT, height=ALTURA_INPUT, font=FONTE_INPUT)
entrada_usuario_login.pack(pady=20)
entrada_senha_login = ctk.CTkEntry(frame_login, placeholder_text="Senha", show="*", width=LARGURA_INPUT, height=ALTURA_INPUT, font=FONTE_INPUT)
entrada_senha_login.pack(pady=20)
label_status_login = ctk.CTkLabel(frame_login, text="", font=FONTE_TEXTO)
label_status_login.pack(pady=20)

def mostrar_login():
    for f in frame_container.winfo_children():
        f.pack_forget()
    frame_login.pack(fill="both", expand=True)

# -- tela cadastro usuário (resumida)
frame_cadastro_usuario = ctk.CTkFrame(frame_container)
titulo_cadastro_user = ctk.CTkLabel(frame_cadastro_usuario, text="Cadastro de Novo Usuário", font=FONTE_TITULO)
titulo_cadastro_user.pack(pady=60)
entrada_nome_user = ctk.CTkEntry(frame_cadastro_usuario, placeholder_text="Nome Completo", width=LARGURA_INPUT, height=ALTURA_INPUT, font=FONTE_INPUT)
entrada_nome_user.pack(pady=20)
entrada_usuario_user = ctk.CTkEntry(frame_cadastro_usuario, placeholder_text="Usuário", width=LARGURA_INPUT, height=ALTURA_INPUT, font=FONTE_INPUT)
entrada_usuario_user.pack(pady=20)
entrada_senha_user = ctk.CTkEntry(frame_cadastro_usuario, placeholder_text="Senha", show="*", width=LARGURA_INPUT, height=ALTURA_INPUT, font=FONTE_INPUT)
entrada_senha_user.pack(pady=20)
label_status_cadastro_user = ctk.CTkLabel(frame_cadastro_usuario, text="", font=FONTE_TEXTO)
label_status_cadastro_user.pack(pady=20)

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
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id_usuario FROM tb_usuario WHERE matricula = %s", (usuario,))
        if cur.fetchone():
            label_status_cadastro_user.configure(text="Usuário já existe!", text_color="red")
            cur.close(); conn.close(); return
        cur.execute("INSERT INTO tb_usuario (nome, cargo, matricula, senha) VALUES (%s, %s, %s, %s)", (nome, "Operador", usuario, senha))
        conn.commit()
        cur.execute("SELECT * FROM tb_usuario WHERE matricula = %s", (usuario,))
        novo_usuario = cur.fetchone()
        cur.close(); conn.close()
        USUARIO_ATUAL[0] = novo_usuario
        mostrar_menu_inicial()
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
        cur.close(); conn.close()
        if user:
            USUARIO_ATUAL[0] = user
            frame_login.pack_forget()
            frame_inicial.pack(fill="both", expand=True)
        else:
            label_status_login.configure(text="Usuário ou senha incorretos!", text_color="red")
    except Error as e:
        print(f"[DB] Erro login_usuario: {e}")
        label_status_login.configure(text="Erro ao consultar banco!", text_color="red")

# botões de login/cadastro
botao_login = ctk.CTkButton(frame_login, text="Entrar", command=login_usuario, width=LARGURA_BOTAO, height=ALTURA_BOTAO, font=FONTE_TEXTO, fg_color="#27ae60")
botao_login.pack(pady=12)
botao_ir_cadastro = ctk.CTkButton(frame_login, text="Criar nova conta", command=mostrar_cadastro_usuario, width=LARGURA_BOTAO, height=ALTURA_BOTAO, font=FONTE_TEXTO, fg_color="#2980b9")
botao_ir_cadastro.pack(pady=8)
botao_voltar_login = ctk.CTkButton(frame_cadastro_usuario, text="Voltar ao Login", command=mostrar_login, width=LARGURA_BOTAO, height=ALTURA_BOTAO, font=FONTE_TEXTO, fg_color="#c0392b")
botao_voltar_login.pack(pady=8)
botao_registrar_user = ctk.CTkButton(frame_cadastro_usuario, text="Registrar", command=registrar_usuario, width=LARGURA_BOTAO, height=ALTURA_BOTAO, font=FONTE_TEXTO, fg_color="#27ae60")
botao_registrar_user.pack(pady=8)

# =====================================================
# TELA INICIAL / MENU
# =====================================================
frame_inicial = ctk.CTkFrame(frame_container)
titulo_inicial = ctk.CTkLabel(frame_inicial, text="Bem-vindo ao Sistema RFID", font=FONTE_TITULO)
titulo_inicial.pack(pady=60)
label_usuario = ctk.CTkLabel(frame_inicial, text="", font=("Arial", 24))
label_usuario.pack(pady=20)

def atualizar_usuario_logado():
    if USUARIO_ATUAL[0]:
        label_usuario.configure(text=f"Usuário logado: {USUARIO_ATUAL[0]['nome']} ({USUARIO_ATUAL[0]['matricula']})")

botoes_frame = ctk.CTkFrame(frame_inicial)
botoes_frame.pack(pady=40)
botao_cadastro_tag = ctk.CTkButton(botoes_frame, text="Cadastro de TAGs", width=280, height=60, font=FONTE_TEXTO, fg_color="#2980b9", command=lambda: mostrar_cadastro())
botao_cadastro_tag.grid(row=0, column=0, padx=30, pady=10)
botao_leitura = ctk.CTkButton(botoes_frame, text="Leitura RFID", width=280, height=60, font=FONTE_TEXTO, fg_color="#27ae60", command=lambda: mostrar_leitura())
botao_leitura.grid(row=0, column=1, padx=30, pady=10)
botao_sair = ctk.CTkButton(frame_inicial, text="Sair do Sistema", width=280, height=60, font=FONTE_TEXTO, fg_color="#c0392b", command=mostrar_login)
botao_sair.pack(pady=30)

# =====================================================
# CADASTRO DE TAGS (mantido quase igual)
# =====================================================
frame_cadastro = ctk.CTkFrame(frame_container)
label_cadastro = ctk.CTkLabel(frame_cadastro, text="Cadastro de TAGs RFID", font=FONTE_TITULO)
label_cadastro.pack(pady=40)
entrada_nome_tag = ctk.CTkEntry(frame_cadastro, placeholder_text="Nome da Ferramenta", width=500, height=55, font=FONTE_INPUT)
entrada_nome_tag.pack(pady=12)
entrada_codigo_tag = ctk.CTkEntry(frame_cadastro, placeholder_text="Código da TAG", width=500, height=55, font=FONTE_INPUT)
entrada_codigo_tag.pack(pady=12)
status_cadastro = ctk.CTkLabel(frame_cadastro, text="", font=FONTE_TEXTO)
status_cadastro.pack(pady=12)

capturando_tag = [False]
thread_leitura_tag = [None]

def preencher_codigo_detectado(codigo):
    entrada_codigo_tag.delete(0, tk.END)
    entrada_codigo_tag.insert(0, codigo)
    status_cadastro.configure(text=f"TAG detectada: {codigo}", text_color="lightgreen")

def ler_tag_cadastro():
    try:
        ser = serial.Serial(porta1, baud, timeout=0.1)
    except Exception as e:
        print(f"[ERRO SERIAL] {e}")
        return
    while capturando_tag[0]:
        try:
            if ser.in_waiting > 0:
                raw = ser.readline().decode(errors="ignore").strip()
                codigo = normalizar_tag(raw)
                if len(codigo) > 5:
                    frame_cadastro.after(0, preencher_codigo_detectado, codigo)
            time.sleep(0.05)
        except Exception:
            time.sleep(0.05)
    ser.close()

def iniciar_leitura_tag():
    if not capturando_tag[0]:
        capturando_tag[0] = True
        thread_leitura_tag[0] = threading.Thread(target=ler_tag_cadastro, daemon=True)
        thread_leitura_tag[0].start()

def parar_leitura_tag():
    capturando_tag[0] = False
    if thread_leitura_tag[0]:
        thread_leitura_tag[0].join(timeout=0.5)

def salvar_tag():
    nome = entrada_nome_tag.get().strip()
    codigo = entrada_codigo_tag.get().strip()
    if not nome or not codigo:
        status_cadastro.configure(text="Preencha todos os campos!", text_color="red"); return
    if salvar_tag_no_banco(nome, codigo):
        status_cadastro.configure(text="TAG cadastrada com sucesso!", text_color="lightgreen")
        entrada_nome_tag.delete(0, tk.END); entrada_codigo_tag.delete(0, tk.END)
    else:
        status_cadastro.configure(text="TAG já cadastrada!", text_color="red")

botao_salvar_tag = ctk.CTkButton(frame_cadastro, text="Salvar TAG", command=salvar_tag, width=280, height=60, font=FONTE_TEXTO, fg_color="#27ae60")
botao_salvar_tag.pack(pady=10)
botao_voltar_menu = ctk.CTkButton(frame_cadastro, text="Voltar ao Menu", command=lambda: [parar_leitura_tag(), mostrar_menu_inicial()], width=280, height=60, font=FONTE_TEXTO, fg_color="#c0392b")
botao_voltar_menu.pack(pady=8)

# =====================================================
# LEITURA RFID AO VIVO (FUNCIONAL)
# =====================================================
frame_leitura = ctk.CTkFrame(frame_container)
titulo_leitura = ctk.CTkLabel(frame_leitura, text="Leitura de Tags RFID em Tempo Real", font=FONTE_TITULO)
titulo_leitura.pack(pady=30)

area_leitura_frame = ctk.CTkFrame(frame_leitura, fg_color="#1c1c1c")
area_leitura_frame.pack(fill="both", expand=True, padx=40, pady=10)

coluna_tornos = ctk.CTkFrame(area_leitura_frame)
coluna_tornos.pack(side="left", expand=True, fill="both", padx=20, pady=10)
coluna_ferramentas = ctk.CTkFrame(area_leitura_frame)
coluna_ferramentas.pack(side="left", expand=True, fill="both", padx=20, pady=10)

label_tornos = ctk.CTkLabel(coluna_tornos, text="Sala dos Tornos", font=("Arial", 30, "bold"))
label_tornos.pack(pady=8)
label_ferramentas = ctk.CTkLabel(coluna_ferramentas, text="Sala de Ferramentas", font=("Arial", 30, "bold"))
label_ferramentas.pack(pady=8)

texto_tornos = scrolledtext.ScrolledText(coluna_tornos, width=55, height=20, font=("Consolas", 14))
texto_tornos.pack(padx=6, pady=6, expand=True, fill="both")
texto_ferramentas = scrolledtext.ScrolledText(coluna_ferramentas, width=55, height=20, font=("Consolas", 14))
texto_ferramentas.pack(padx=6, pady=6, expand=True, fill="both")

status_leitura = ctk.CTkLabel(frame_leitura, text="", font=FONTE_TEXTO)
status_leitura.pack(pady=6)

botoes_leitura = ctk.CTkFrame(frame_leitura, fg_color="transparent")
botoes_leitura.pack(pady=10)

botao_iniciar_leitura = ctk.CTkButton(botoes_leitura, text="Iniciar Leitura", width=280, height=60, font=FONTE_TEXTO, fg_color="#27ae60")
botao_iniciar_leitura.grid(row=0, column=0, padx=20, pady=6)
botao_parar_leitura = ctk.CTkButton(botoes_leitura, text="Parar Leitura", width=280, height=60, font=FONTE_TEXTO, fg_color="#e67e22")
botao_parar_leitura.grid(row=0, column=1, padx=20, pady=6)
botao_voltar_menu_leitura = ctk.CTkButton(frame_leitura, text="Voltar ao Menu Principal", width=280, height=60, font=FONTE_TEXTO, fg_color="#c0392b", command=lambda: [parar_leitura_rfid(), mostrar_menu_inicial()])
botao_voltar_menu_leitura.pack(pady=12)

# ------------------- FUNÇÕES RFID FUNCIONAIS -------------------

ultimo_registro_tag = {}  # dicionário: {codigo_tag: timestamp_último_registro}
INTERVALO_TAG = 3  # segundos entre leituras válidas da mesma tag

def registrar_leitura(porta, codigo):
    agora = time.time()

    # Impede registro duplicado da mesma tag em curto intervalo
    if codigo in ultimo_registro_tag and (agora - ultimo_registro_tag[codigo]) < INTERVALO_TAG:
        return  # ignora leitura repetida

    # Atualiza timestamp da tag
    ultimo_registro_tag[codigo] = agora

    # Determina local e destino do texto
    id_ferramenta, nome = buscar_ferramenta_por_tag(codigo)
    local = "Sala de Ferramentas" if porta == porta1 else "Sala dos Tornos"
    destino = texto_ferramentas if local == "Sala de Ferramentas" else texto_tornos

    # Data e hora formatadas
    data_hora = datetime.now().strftime("%H:%M:%S %d/%m/%Y")

    # Registra no banco e mostra na tela
    if id_ferramenta:
        id_user = USUARIO_ATUAL[0]['id_usuario'] if USUARIO_ATUAL[0] and 'id_usuario' in USUARIO_ATUAL[0] else None
        registrar_movimentacao(id_ferramenta, local, id_usuario=id_user)
        msg = f"[{data_hora}] {local} -> {nome} captado.\n"
    else:
        msg = f"[{data_hora}] {local} -> TAG desconhecida captada.\n"

    destino.insert(tk.END, msg)
    destino.see(tk.END)


def ler_porta_serial(porta):
    try:
        ser = serial.Serial(porta, baud, timeout=0.1)
    except Exception as e:
        destino = texto_ferramentas if porta == porta1 else texto_tornos
        destino.insert(tk.END, f"[ERRO] Falha ao abrir {porta}: {e}\n")
        destino.see(tk.END)
        return

    while capturando_leitura[0]:
        try:
            if ser.in_waiting > 0:
                raw = ser.readline().decode(errors="ignore").strip()
                codigo = normalizar_tag(raw)
                if len(codigo) > 5:
                    frame_leitura.after(0, registrar_leitura, porta, codigo)
            time.sleep(0.05)
        except Exception:
            time.sleep(0.05)
    ser.close()

def iniciar_leitura_rfid():
    if capturando_leitura[0]:
        return
    capturando_leitura[0] = True
    texto_tornos.delete(1.0, tk.END)
    texto_ferramentas.delete(1.0, tk.END)
    status_leitura.configure(text="Leitura em andamento...", text_color="lightgreen")
    threads_leitura.clear()
    for porta in [porta1, porta2]:
        t = threading.Thread(target=ler_porta_serial, args=(porta,), daemon=True)
        t.start()
        threads_leitura.append(t)

def parar_leitura_rfid():
    capturando_leitura[0] = False
    for t in threads_leitura:
        t.join(timeout=0.5)
    status_leitura.configure(text="Leitura encerrada.", text_color="#e67e22")

botao_iniciar_leitura.configure(command=iniciar_leitura_rfid)
botao_parar_leitura.configure(command=parar_leitura_rfid)

# =====================================================
# Funções de troca de tela (simples)
# =====================================================
def mostrar_menu_inicial():
    for f in frame_container.winfo_children():
        f.pack_forget()
    frame_inicial.pack(fill="both", expand=True)
    atualizar_usuario_logado()

def mostrar_cadastro():
    for f in frame_container.winfo_children():
        f.pack_forget()
    frame_cadastro.pack(fill="both", expand=True)
    iniciar_leitura_tag()

def mostrar_leitura():
    for f in frame_container.winfo_children():
        f.pack_forget()
    frame_leitura.pack(fill="both", expand=True)

# =====================================================
# ===================== ADIÇÕES ADMIN ==================
# (tudo adicionado aqui — sem tocar no código acima)
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
            # não altera USUARIO_ATUAL (admin separado), apenas mostra painel admin
            for f in frame_container.winfo_children():
                f.pack_forget()
            abrir_painel_admin()
        else:
            label_status_login.configure(text="Usuário ou senha incorretos!", text_color="red")
    except Error as e:
        print(f"[DB] Erro login_admin: {e}")
        label_status_login.configure(text="Erro ao consultar banco!", text_color="red")


def abrir_painel_admin():
    for f in frame_container.winfo_children():
        f.pack_forget()

    global frame_admin, tree_users_frame
    frame_admin = ctk.CTkFrame(frame_container)
    frame_admin.pack(fill="both", expand=True)

    titulo_admin = ctk.CTkLabel(frame_admin, text="Painel do Administrador", font=("Arial", 38, "bold"))
    titulo_admin.pack(pady=20)

    # topo: botoes
    topo_frame = ctk.CTkFrame(frame_admin)
    topo_frame.pack(pady=10)

    bot_atualizar = ctk.CTkButton(topo_frame, text="Atualizar", width=200, height=45, command=lambda: [carregar_movimentacoes(), carregar_usuarios()], fg_color="#27ae60")
    bot_atualizar.pack(side="left", padx=8)

    bot_voltar = ctk.CTkButton(topo_frame, text="Voltar ao Login", width=200, height=45, command=mostrar_login, fg_color="#c0392b")
    bot_voltar.pack(side="left", padx=8)

    # area movimentacoes
    label_mov = ctk.CTkLabel(frame_admin, text="Últimas 5 Movimentações", font=("Arial", 26, "bold"))
    label_mov.pack(pady=8)

    global text_mov_admin
    text_mov_admin = scrolledtext.ScrolledText(frame_admin, font=("Consolas", 13), bg="#A3A1A1", height=8)
    text_mov_admin.pack(fill="x", padx=30, pady=6)

    # area usuarios
    label_users = ctk.CTkLabel(frame_admin, text="Usuários Cadastrados", font=("Arial", 26, "bold"))
    label_users.pack(pady=8)

    tree_users_frame = ctk.CTkFrame(frame_admin)
    tree_users_frame.pack(fill="both", expand=False, padx=30, pady=6)

    # container com botões de ação abaixo da lista
    actions_frame = ctk.CTkFrame(frame_admin)
    actions_frame.pack(pady=10)

    bot_edit = ctk.CTkButton(actions_frame, text="Editar Usuário Selecionado", command=abrir_edicao_usuario, width=240, height=48, fg_color="#2980b9")
    bot_edit.pack(side="left", padx=8)

    bot_delete = ctk.CTkButton(actions_frame, text="Deletar Usuário Selecionado", command=deletar_usuario_selecionado, width=240, height=48, fg_color="#e74c3c")
    bot_delete.pack(side="left", padx=8)

    carregar_movimentacoes()
    carregar_usuarios()


def carregar_movimentacoes():
    conn = conectar_banco()
    if not conn:
        text_mov_admin.delete(1.0, tk.END)
        text_mov_admin.insert(tk.END, "Erro de conexão com o banco\n")
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT m.id_mov, u.nome, f.nome, m.data_retirada, m.data_devolucao, m.observacao
            FROM tb_movimentacoes m
            LEFT JOIN tb_usuario u ON m.id_usuario = u.id_usuario
            LEFT JOIN tb_ferramentas f ON m.id_ferramentas = f.id_ferramentas
            ORDER BY m.data_retirada DESC
            LIMIT 5
        """)
        dados = cur.fetchall()
        cur.close()
        conn.close()

        text_mov_admin.delete(1.0, tk.END)
        if not dados:
            text_mov_admin.insert(tk.END, "Sem movimentações.\n")
            return
        for d in dados:
            data_ret = d[3].strftime("%d/%m/%Y %H:%M:%S") if d[3] else "-"
            data_dev = d[4].strftime("%d/%m/%Y %H:%M:%S") if d[4] else "-"
            text_mov_admin.insert(tk.END, f"ID:{d[0]}  Usuário:{d[1] or '-'}  Ferramenta:{d[2] or '-'}\n Retirada:{data_ret}  Devolução:{data_dev}\n Obs:{d[5] or '-'}\n\n")
    except Error as e:
        print(f"[DB] Erro carregar_movimentacoes: {e}")
        text_mov_admin.delete(1.0, tk.END)
        text_mov_admin.insert(tk.END, "Erro ao carregar movimentações\n")


def carregar_usuarios():
    conn = conectar_banco()
    if not conn:
        return
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id_usuario, nome, cargo, status, matricula FROM tb_usuario ORDER BY id_usuario")
        dados = cur.fetchall()
        cur.close()
        conn.close()

        # limpar frame anterior
        for w in tree_users_frame.winfo_children():
            w.destroy()

        if not dados:
            lbl = ctk.CTkLabel(tree_users_frame, text="Nenhum usuário cadastrado", font=("Arial", 16))
            lbl.pack(pady=6)
            return

        # criar uma listagem simples com seleção
        global listbox_users
        listbox_users = tk.Listbox(tree_users_frame, font=("Consolas", 14), height=10)
        scrollbar = tk.Scrollbar(tree_users_frame, orient="vertical", command=listbox_users.yview)
        listbox_users.config(yscrollcommand=scrollbar.set)
        listbox_users.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # popular listbox
        for u in dados:
            display = f"{u['id_usuario']:>3} | {u['nome'][:30]:30} | {u['cargo'] or '-':12} | {u['status'] or '-':12} | {u['matricula']}"
            listbox_users.insert(tk.END, display)

        # guardar mapping id por índice (útil para edições)
        global usuarios_cache
        usuarios_cache = {idx: u for idx, u in enumerate(dados)}

    except Error as e:
        print(f"[DB] Erro carregar_usuarios: {e}")


def abrir_edicao_usuario():
    # pega seleção
    try:
        sel = listbox_users.curselection()
        if not sel:
            tk.messagebox.showinfo("Editar usuário", "Selecione um usuário na lista.")
            return
        idx = sel[0]
        usuario = usuarios_cache.get(idx)
    except Exception:
        tk.messagebox.showinfo("Editar usuário", "Seleção inválida.")
        return

    # janela de edição simples (CTk toplevel)
    topo = tk.Toplevel(janela_inicial)
    topo.title("Editar Usuário")
    topo.geometry("480x300")
    frame_e = ctk.CTkFrame(topo)
    frame_e.pack(fill="both", expand=True, padx=16, pady=16)

    lbl_nome = ctk.CTkLabel(frame_e, text=f"Nome: {usuario['nome']}", font=("Arial", 14))
    lbl_nome.pack(pady=6)

    entry_cargo = ctk.CTkEntry(frame_e, placeholder_text="Cargo (ex: Operador)", width=420)
    entry_cargo.insert(0, usuario.get('cargo') or "")
    entry_cargo.pack(pady=6)

    entry_status = ctk.CTkOptionMenu(frame_e, values=["Em atividade", "Desligado"])
    entry_status.set(usuario.get('status') or "Em atividade")
    entry_status.pack(pady=6)

    lbl_info = ctk.CTkLabel(frame_e, text="Clique em Salvar para atualizar cargo/status", font=("Arial", 12))
    lbl_info.pack(pady=8)

    def salvar_edicao():
        novo_cargo = entry_cargo.get().strip()
        novo_status = entry_status.get()
        conn = conectar_banco()
        if not conn:
            tk.messagebox.showerror("Erro", "Falha ao conectar ao banco")
            return
        try:
            cur = conn.cursor()
            cur.execute("UPDATE tb_usuario SET cargo = %s, status = %s WHERE id_usuario = %s", (novo_cargo, novo_status, usuario['id_usuario']))
            conn.commit()
            cur.close(); conn.close()
            topo.destroy()
            carregar_usuarios()
            tk.messagebox.showinfo("Sucesso", "Usuário atualizado.")
        except Error as e:
            tk.messagebox.showerror("Erro", f"Falha ao atualizar: {e}")

    bot_salvar = ctk.CTkButton(frame_e, text="Salvar", command=salvar_edicao, fg_color="#27ae60", width=160)
    bot_salvar.pack(pady=10)

def deletar_usuario_selecionado():
    try:
        sel = listbox_users.curselection()
        if not sel:
            tk.messagebox.showinfo("Deletar usuário", "Selecione um usuário na lista.")
            return
        idx = sel[0]
        usuario = usuarios_cache.get(idx)
    except Exception:
        tk.messagebox.showinfo("Deletar usuário", "Seleção inválida.")
        return

    confirm = tk.messagebox.askyesno("Confirmar exclusão", f"Deseja excluir o usuário '{usuario['nome']}' (matrícula {usuario['matricula']})?")
    if not confirm:
        return

    conn = conectar_banco()
    if not conn:
        tk.messagebox.showerror("Erro", "Falha ao conectar ao banco")
        return
    try:
        cur = conn.cursor()
        # opcional: remover movimentações relacionadas? aqui apenas exclui usuário
        cur.execute("DELETE FROM tb_usuario WHERE id_usuario = %s", (usuario['id_usuario'],))
        conn.commit()
        cur.close(); conn.close()
        carregar_usuarios()
        tk.messagebox.showinfo("Sucesso", "Usuário excluído.")
    except Error as e:
        tk.messagebox.showerror("Erro", f"Falha ao excluir: {e}")

# botão de login admin (adicionado sem alterar linhas anteriores)
botao_admin_login = ctk.CTkButton(frame_login, text="Entrar como Administrador", command=login_admin, width=LARGURA_BOTAO, height=ALTURA_BOTAO, fg_color="#8e44ad")
botao_admin_login.pack(pady=6)

# =====================================================
# INÍCIO DO PROGRAMA
# =====================================================
mostrar_login()
janela_inicial.mainloop()

