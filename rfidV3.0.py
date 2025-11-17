#============= BIBLIOTECAS ============
import serial                       # Comunicação via porta serial (para ler dados do leitor RFID)
import time                         # Controle de tempo (pausas, timestamps etc.)
import threading                    # Executar múltiplas tarefas ao mesmo tempo (threads)
import tkinter as tk                # Criação da interface gráfica
import customtkinter as ctk         # Interface Gráfica
from tkinter import scrolledtext    # Área de texto com barra de rolagem
from datetime import datetime       # Trabalhar com data e hora
import mysql.connector              # Conexão com banco
from mysql.connector import Error   # Importa código de erro mysql

# =====================================================
# VARIÁVEIS GLOBAIS (únicas definições)
# =====================================================
capturando_leitura = [False]   # controle de leitura (mutável dentro de threads)
threads_leitura = []           # lista de threads de leitura
porta1 = "COM5"                # Designa a porta de comunicação 5 à variável
porta2 = "COM6"                # Designa a porta de comunicação 6 à variável
baud = 115200                  # Taxa de mudança de sinal por segundo em um canal de comunicação
USUARIO_ATUAL = [None]         # Guarda os dados do usuário logado (lista para permitir mutação dentro de funções)

# =====================================================
#                      BANCO
# =====================================================
# Função para conectar ao banco
def conectar_banco():
    try:
        return mysql.connector.connect( # Retorna conexão com o banco
            host="localhost",           # Conecta ao Servidor
            user="root",                # Usuário
            password="",                # Senha
            database="db_rfid"          # Banco
        )
    except Error as e: 
        print(f"[DB] Erro ao conectar: {e}") # Retorna o erro de conexão
        return None                          # Retorna None em caso de falha             

# Função que recebe o código da TAG e procura no banco qual ferramenta ela representa
def buscar_ferramenta_por_tag(codigo_tag):
    conn = conectar_banco() # Conecta ao banco
    if not conn:            # Se não estiver conectado, não retorna nada
        return None, None
    try:
        cur = conn.cursor()
        # Realiza a Busca no banco usando join e exibindo ferramentas associadas às tags
        cur.execute(""" 
            SELECT f.id_ferramentas, f.nome
            FROM tb_rfid_tags t
            JOIN tb_ferramentas f ON t.id_ferramenta = f.id_ferramentas
            WHERE t.codigo_tag = %s
            LIMIT 1
        """, (codigo_tag,))
        
        res = cur.fetchone() # Busca uma única linha (pois LIMIT 1)
        cur.close()          # Fecha a Conexão
        conn.close()
        
        if res:
            return res[0], res[1] # Retorna ID e nome da ferramenta ligada à TAG
            
        return None, None         # Se não encontrou, retorna vazio
        
    except Error as e:
        print(f"[DB] Erro buscar_ferramenta_por_tag: {e}") # Printa erro caso a conexão da busca, falhe
        return None, None

# Registra movimentação no banco (entrada/saída ou leitura da TAG)
def registrar_movimentacao(id_ferramenta, local, observacao=None, id_usuario=None):
    conn = conectar_banco() 
    if not conn:
        return False
    try:
        cur = conn.cursor()
        # Aqui registra data de retirada e devolução como NOW() (poderia ser ajustado se fosse controlar retiradas de verdade)
        cur.execute("""
            INSERT INTO tb_movimentacoes (id_usuario, id_ferramentas, data_retirada, data_devolucao, observacao)
            VALUES (%s, %s, NOW(), NOW(), %s)
        """, (id_usuario or 1, id_ferramenta, observacao or f"Leitura de {local}"))
        
        conn.commit() # Salva no banco
        cur.close()
        conn.close()
        return True

    except Error as e:
        print(f"[DB] Erro registrar_movimentacao: {e}")
        return False

# Função usada no CADASTRO DE TAGS — registra ferramenta + TAG associada
def salvar_tag_no_banco(nome, codigo):
    conn = conectar_banco() # Conecta ao banco
    if not conn:
        return False
    try:
        cur = conn.cursor()
        
        # Primeiro cria a ferramenta
        cur.execute("INSERT INTO tb_ferramentas (nome) VALUES (%s)", (nome,))
        id_ferramenta = cur.lastrowid # Captura o ID da ferramenta recém criada
        
        # Depois associa a TAG à ferramenta criada
        cur.execute("INSERT INTO tb_rfid_tags (codigo_tag, id_ferramenta) VALUES (%s, %s)", (codigo, id_ferramenta))
        
        
        conn.commit() # Salva no banco
        cur.close()   # Fecha a conexão
        conn.close()
        return True
        
    except Error as e:
        print(f"[DB] Erro ao salvar TAG: {e}") # Erro caso a conexão falhe
        return False

# =====================================================
# UI - configuração geral
# =====================================================

ctk.set_appearance_mode("dark")                 # Define o tema visual como "dark mode"
ctk.set_default_color_theme("dark-blue")        # Define um tema de cores azul-escuro para botões e detalhes

janela_inicial = ctk.CTk()                      # Cria a janela principal do programa
janela_inicial.attributes('-fullscreen', True)  # Coloca o programa em modo tela cheia
janela_inicial.title("Sistema RFID com Login")  # Título da janela

frame_container = ctk.CTkFrame(janela_inicial)  # Frame principal que segura as telas do sistema
frame_container.pack(fill="both", expand=True)  # Preenche toda a janela


# Definição de fontes e tamanhos fixos para manter padrão visual em todas as telas
FONTE_TITULO = ("Arial", 48, "bold") # FONTE PARA TÍTULOS DEFINIDA EM ARIAL, TAMANHO 48 E NEGRITO
FONTE_TEXTO = ("Arial", 22)          # FONTE PARA TÍTULOS DEFINIDA EM ARIAL, TAMANHO 22 
FONTE_INPUT = ("Arial", 20)          # FONTE PARA TÍTULOS DEFINIDA EM ARIAL, TAMANHO 20 

# Dimensões padrão reutilizadas em vários campos e botões
ALTURA_INPUT = 55       # TAMANHO DE INPUT DEFINIDO EM 55
LARGURA_INPUT = 500     # TAMANHO DE INPUT DEFINIDO EM 500
ALTURA_BOTAO = 60       # TAMANHO DE INPUT DEFINIDO EM 60
LARGURA_BOTAO = 280     # TAMANHO DE INPUT DEFINIDO EM 280

# =====================================================
# Funções utilitárias
# =====================================================

# Função que recebe a linha bruta lida pela serial e remove tudo que não for letra/número
def normalizar_tag(raw):
    return "".join(ch for ch in raw if ch.isalnum()).upper()
    # Isso garante que códigos como " \r\n FE A 12 3 " virem "FEA123"
    
# =====================================================
# TELA DE LOGIN / CADASTRO (mesma lógica sua)
# (mantive suas funções: mostrar_login, registrar_usuario, login_usuario, etc.)
# =====================================================

# --------------- TELA DE LOGIN ------------------

frame_login = ctk.CTkFrame(frame_container)    # Frame que representa a tela de login

# Título da tela de login
titulo_login = ctk.CTkLabel(frame_login, text="Login de Usuário", font=FONTE_TITULO)
titulo_login.pack(pady=80)

# Campo do nome/matrícula do usuário
entrada_usuario_login = ctk.CTkEntry(frame_login, placeholder_text="Usuário", width=LARGURA_INPUT, height=ALTURA_INPUT, font=FONTE_INPUT)
entrada_usuario_login.pack(pady=20)

# Campo de senha com ocultação do texto (show="*")
entrada_senha_login = ctk.CTkEntry(frame_login, placeholder_text="Senha", show="*", width=LARGURA_INPUT, height=ALTURA_INPUT, font=FONTE_INPUT)
entrada_senha_login.pack(pady=20)

# Label onde aparecem mensagens de erro como "senha incorreta"
label_status_login = ctk.CTkLabel(frame_login, text="", font=FONTE_TEXTO)
label_status_login.pack(pady=20)


# Função que troca a tela atual para a tela de login
def mostrar_login():
    # Remove qualquer outro frame que estiver na tela
    for f in frame_container.winfo_children():
        f.pack_forget()
        
    # Mostra o frame_login
    frame_login.pack(fill="both", expand=True)


# --------------- TELA DE CADASTRO DE USUÁRIO ------------------

frame_cadastro_usuario = ctk.CTkFrame(frame_container)
titulo_cadastro_user = ctk.CTkLabel(frame_cadastro_usuario, text="Cadastro de Novo Usuário", font=FONTE_TITULO)
titulo_cadastro_user.pack(pady=60)

# Nome completo da pessoa que será cadastrada
entrada_nome_user = ctk.CTkEntry(frame_cadastro_usuario, placeholder_text="Nome Completo", width=LARGURA_INPUT, height=ALTURA_INPUT, font=FONTE_INPUT)
entrada_nome_user.pack(pady=20)

# Nome de usuário / matrícula
entrada_usuario_user = ctk.CTkEntry(frame_cadastro_usuario, placeholder_text="Usuário", width=LARGURA_INPUT, height=ALTURA_INPUT, font=FONTE_INPUT)
entrada_usuario_user.pack(pady=20)

# Senha do usuário
entrada_senha_user = ctk.CTkEntry(frame_cadastro_usuario, placeholder_text="Senha", show="*", width=LARGURA_INPUT, height=ALTURA_INPUT, font=FONTE_INPUT)
entrada_senha_user.pack(pady=20)

# Label para mensagens (sucesso/erro no cadastro)
label_status_cadastro_user = ctk.CTkLabel(frame_cadastro_usuario, text="", font=FONTE_TEXTO)
label_status_cadastro_user.pack(pady=20)


# Função que troca da tela de login para a tela de cadastro de usuário
def mostrar_cadastro_usuario():
    frame_login.pack_forget()
    frame_cadastro_usuario.pack(fill="both", expand=True)

# Função responsável por inserir um novo usuário no banco de dados
def registrar_usuario():
    # Retira espaços em branco
    nome = entrada_nome_user.get().strip()
    usuario = entrada_usuario_user.get().strip()
    senha = entrada_senha_user.get().strip()
    
    # Validação simples para garantir que nenhum campo está vazio
    if not nome or not usuario or not senha:    
        label_status_cadastro_user.configure(text="Preencha todos os campos!", text_color="red")
        return
    conn = conectar_banco()
    if not conn:
        label_status_cadastro_user.configure(text="Erro ao conectar com o banco!", text_color="red")
        return
    try:
        cur = conn.cursor(dictionary=True)
        
        # Verifica se já existe alguém com a mesma matrícula
        cur.execute("SELECT id_usuario FROM tb_usuario WHERE matricula = %s", (usuario,))
        if cur.fetchone():
            label_status_cadastro_user.configure(text="Usuário já existe!", text_color="red")
            cur.close(); conn.close(); return
            
        # Salva o novo usuário com cargo padrão Operador
        cur.execute("INSERT INTO tb_usuario (nome, cargo, matricula, senha) VALUES (%s, %s, %s, %s)", (nome, "Operador", usuario, senha))
        conn.commit()
        
        # Recarrega os dados completos do usuário recém-cadastrado
        cur.execute("SELECT * FROM tb_usuario WHERE matricula = %s", (usuario,))
        novo_usuario = cur.fetchone()
        
        cur.close(); conn.close()
        
        # Salva o usuário atual na memória global
        USUARIO_ATUAL[0] = novo_usuario
        
        # Vai para o menu inicial
        mostrar_menu_inicial()
    except Error as e:
        print(f"[DB] Erro registrar_usuario: {e}")
        label_status_cadastro_user.configure(text="Erro ao salvar no banco!", text_color="red")

# Função de login do usuário normal (não admin)
def login_usuario():
    usuario = entrada_usuario_login.get().strip()
    senha = entrada_senha_login.get().strip()
    
    # Verifica se nome e senha foram preenchidos
    if not usuario or not senha:
        label_status_login.configure(text="Preencha todos os campos!", text_color="red")
        return
        
    conn = conectar_banco()
    if not conn:
        label_status_login.configure(text="Erro ao conectar com o banco!", text_color="red")
        return
        
    try:
        cur = conn.cursor(dictionary=True)
        
        # Procura o usuário com matrícula + senha
        cur.execute("SELECT * FROM tb_usuario WHERE matricula = %s AND senha = %s", (usuario, senha))
        user = cur.fetchone()
        
        cur.close(); conn.close()
        
        if user:
            # Se encontrado, salva como usuário logado e abre o menu
            USUARIO_ATUAL[0] = user
            frame_login.pack_forget()
            frame_inicial.pack(fill="both", expand=True)
        else:
            # Se matrícula/senha errados
            label_status_login.configure(text="Usuário ou senha incorretos!", text_color="red")
            
    except Error as e:
        print(f"[DB] Erro login_usuario: {e}")
        label_status_login.configure(text="Erro ao consultar banco!", text_color="red")


# Botão “Entrar”
botao_login = ctk.CTkButton(frame_login, text="Entrar", command=login_usuario, width=LARGURA_BOTAO, height=ALTURA_BOTAO, font=FONTE_TEXTO, fg_color="#27ae60")
botao_login.pack(pady=12)


# Botão “Criar nova conta”
botao_ir_cadastro = ctk.CTkButton(frame_login, text="Criar nova conta", command=mostrar_cadastro_usuario, width=LARGURA_BOTAO, height=ALTURA_BOTAO, font=FONTE_TEXTO, fg_color="#2980b9")
botao_ir_cadastro.pack(pady=8)

# Botão de voltar na tela de cadastro
botao_voltar_login = ctk.CTkButton(frame_cadastro_usuario, text="Voltar ao Login", command=mostrar_login, width=LARGURA_BOTAO, height=ALTURA_BOTAO, font=FONTE_TEXTO, fg_color="#c0392b")
botao_voltar_login.pack(pady=8)

# Botão de registrar novo usuário
botao_registrar_user = ctk.CTkButton(frame_cadastro_usuario, text="Registrar", command=registrar_usuario, width=LARGURA_BOTAO, height=ALTURA_BOTAO, font=FONTE_TEXTO, fg_color="#27ae60")
botao_registrar_user.pack(pady=8)

# =====================================================
# TELA INICIAL / MENU
# =====================================================

# Frame principal que aparece depois que o usuário faz login
frame_inicial = ctk.CTkFrame(frame_container)

# Título da tela inicial
titulo_inicial = ctk.CTkLabel(frame_inicial, text="Bem-vindo ao Sistema RFID", font=FONTE_TITULO)
titulo_inicial.pack(pady=60)

# Label que mostra o usuário logado
label_usuario = ctk.CTkLabel(frame_inicial, text="", font=("Arial", 24))
label_usuario.pack(pady=20)

# Função que atualiza o nome do usuário logado no topo da tela
def atualizar_usuario_logado():
    if USUARIO_ATUAL[0]: # Se existe um usuário logado
        label_usuario.configure(text=f"Usuário logado: {USUARIO_ATUAL[0]['nome']} ({USUARIO_ATUAL[0]['matricula']})")

# Frame que contém os botões principais do menu
botoes_frame = ctk.CTkFrame(frame_inicial)
botoes_frame.pack(pady=40)

# Botão para ir ao CADASTRO DE TAGs
botao_cadastro_tag = ctk.CTkButton(botoes_frame, text="Cadastro de TAGs", width=280, height=60, font=FONTE_TEXTO, fg_color="#2980b9", command=lambda: mostrar_cadastro()) # Muda para a tela de cadastro de TAGs
botao_cadastro_tag.grid(row=0, column=0, padx=30, pady=10)

# Botão para ir à tela de LEITURA DE RFID
botao_leitura = ctk.CTkButton(botoes_frame, text="Leitura RFID", width=280, height=60, font=FONTE_TEXTO, fg_color="#27ae60", command=lambda: mostrar_leitura()) # Muda para a tela de leitura ao vivo
botao_leitura.grid(row=0, column=1, padx=30, pady=10)

# Botão para deslogar
botao_sair = ctk.CTkButton(frame_inicial, text="Sair do Sistema", width=280, height=60, font=FONTE_TEXTO, fg_color="#c0392b", command=mostrar_login) # Retorna para tela de login
botao_sair.pack(pady=30)

# =====================================================
# CADASTRO DE TAGS (mantido quase igual)
# =====================================================

# Frame principal da tela de cadastro de TAGs
frame_cadastro = ctk.CTkFrame(frame_container)

# Título da tela
label_cadastro = ctk.CTkLabel(
    frame_cadastro,
    text="Cadastro de TAGs RFID",
    font=FONTE_TITULO
)
label_cadastro.pack(pady=40)

# Campo onde o usuário digita o nome da ferramenta
entrada_nome_tag = ctk.CTkEntry(
    frame_cadastro,
    placeholder_text="Nome da Ferramenta",
    width=500,
    height=55,
    font=FONTE_INPUT
)
entrada_nome_tag.pack(pady=12)

# Campo onde o código da TAG será preenchido automaticamente (ou digitado manualmente)
entrada_codigo_tag = ctk.CTkEntry(
    frame_cadastro,
    placeholder_text="Código da TAG",
    width=500,
    height=55,
    font=FONTE_INPUT
)
entrada_codigo_tag.pack(pady=12)

# Label de status (exibe mensagens como “TAG detectada” ou “Erro ao salvar”)
status_cadastro = ctk.CTkLabel(
    frame_cadastro,
    text="",
    font=FONTE_TEXTO
)
status_cadastro.pack(pady=12)

# Flags usadas para controlar a leitura da porta serial durante o cadastro
capturando_tag = [False]     # Se True → lendo porta serial
thread_leitura_tag = [None]  # Guarda a thread responsável pela leitura


# Função que insere o código detectado automaticamente no campo de entrada
def preencher_codigo_detectado(codigo):
    entrada_codigo_tag.delete(0, tk.END)  # Apaga o que estiver no campo
    entrada_codigo_tag.insert(0, codigo)  # Insere o novo código detectado
    status_cadastro.configure(text=f"TAG detectada: {codigo}", text_color="lightgreen")


# Função que fica rodando em uma thread separada lendo a porta serial para capturar TAGs
def ler_tag_cadastro():
    try:
        ser = serial.Serial(porta1, baud, timeout=0.1)  # Tenta abrir a porta do RFID
    except Exception as e:
        print(f"[ERRO SERIAL] {e}")
        return

    # Loop contínuo enquanto a flag estiver ativa
    while capturando_tag[0]:
        try:
            if ser.in_waiting > 0:  # Se tem dados chegando pela porta
                raw = ser.readline().decode(errors="ignore").strip()
                codigo = normalizar_tag(raw)  # Limpa caracteres estranhos

                # Apenas códigos válidos (geralmente > 5 caracteres)
                if len(codigo) > 5:
                    frame_cadastro.after(0, preencher_codigo_detectado, codigo)

            time.sleep(0.05)  # Pequena pausa para não travar CPU

        except Exception:
            time.sleep(0.05)

    ser.close()  # Fecha a porta serial ao sair da função


# Inicia a leitura automática de TAGs
def iniciar_leitura_tag():
    if not capturando_tag[0]:         # Evita iniciar duas vezes
        capturando_tag[0] = True      # Ativa flag
        thread_leitura_tag[0] = threading.Thread(
            target=ler_tag_cadastro,
            daemon=True              # Daemon = fecha junto com o programa
        )
        thread_leitura_tag[0].start()  # Inicia a thread de leitura


# Para a leitura automática de TAGs
def parar_leitura_tag():
    capturando_tag[0] = False         # Desliga flag
    if thread_leitura_tag[0]:
        thread_leitura_tag[0].join(timeout=0.5)  # Espera thread finalizar


# Função de salvar TAG no banco
def salvar_tag():
    nome = entrada_nome_tag.get().strip()
    codigo = entrada_codigo_tag.get().strip()

    # Verificação simples
    if not nome or not codigo:
        status_cadastro.configure(text="Preencha todos os campos!", text_color="red")
        return

    # Salva no banco
    if salvar_tag_no_banco(nome, codigo):
        status_cadastro.configure(text="TAG cadastrada com sucesso!", text_color="lightgreen")

        # Limpa campos
        entrada_nome_tag.delete(0, tk.END)
        entrada_codigo_tag.delete(0, tk.END)
    else:
        status_cadastro.configure(text="TAG já cadastrada!", text_color="red")


# Botão para salvar TAG no banco
botao_salvar_tag = ctk.CTkButton(
    frame_cadastro,
    text="Salvar TAG",
    command=salvar_tag,
    width=280,
    height=60,
    font=FONTE_TEXTO,
    fg_color="#27ae60"
)
botao_salvar_tag.pack(pady=10)

# Botão para voltar ao menu inicial
botao_voltar_menu = ctk.CTkButton(
    frame_cadastro,
    text="Voltar ao Menu",
    command=lambda: [parar_leitura_tag(), mostrar_menu_inicial()],
    width=280,
    height=60,
    font=FONTE_TEXTO,
    fg_color="#c0392b"
)
botao_voltar_menu.pack(pady=8)

# =====================================================
# LEITURA RFID AO VIVO (FUNCIONAL)
# =====================================================

# Frame principal da tela de leitura em tempo real
frame_leitura = ctk.CTkFrame(frame_container)

# Título da tela
titulo_leitura = ctk.CTkLabel(
    frame_leitura,
    text="Leitura de Tags RFID em Tempo Real",
    font=FONTE_TITULO
)
titulo_leitura.pack(pady=30)

# Frame que divide a tela em duas colunas (Tornos e Ferramentas)
area_leitura_frame = ctk.CTkFrame(frame_leitura, fg_color="#1c1c1c")
area_leitura_frame.pack(fill="both", expand=True, padx=40, pady=10)

# Coluna da esquerda — Sala dos Tornos
coluna_tornos = ctk.CTkFrame(area_leitura_frame)
coluna_tornos.pack(side="left", expand=True, fill="both", padx=20, pady=10)

# Coluna da direita — Sala de Ferramentas
coluna_ferramentas = ctk.CTkFrame(area_leitura_frame)
coluna_ferramentas.pack(side="left", expand=True, fill="both", padx=20, pady=10)

# Título de cada coluna
label_tornos = ctk.CTkLabel(coluna_tornos, text="Sala dos Tornos",
                            font=("Arial", 30, "bold"))
label_tornos.pack(pady=8)

label_ferramentas = ctk.CTkLabel(coluna_ferramentas, text="Sala de Ferramentas",
                                 font=("Arial", 30, "bold"))
label_ferramentas.pack(pady=8)

# Caixas de texto com rolagem onde aparecem as leituras em tempo real
texto_tornos = scrolledtext.ScrolledText(
    coluna_tornos, width=55, height=20, font=("Consolas", 14)
)
texto_tornos.pack(padx=6, pady=6, expand=True, fill="both")

texto_ferramentas = scrolledtext.ScrolledText(
    coluna_ferramentas, width=55, height=20, font=("Consolas", 14)
)
texto_ferramentas.pack(padx=6, pady=6, expand=True, fill="both")

# Label que exibe status da leitura (Ex: “Leitura em andamento...”)
status_leitura = ctk.CTkLabel(frame_leitura, text="", font=FONTE_TEXTO)
status_leitura.pack(pady=6)

# Frame que contém os botões Iniciar / Parar
botoes_leitura = ctk.CTkFrame(frame_leitura, fg_color="transparent")
botoes_leitura.pack(pady=10)

# Botão para iniciar leitura
botao_iniciar_leitura = ctk.CTkButton(
    botoes_leitura,
    text="Iniciar Leitura",
    width=280,
    height=60,
    font=FONTE_TEXTO,
    fg_color="#27ae60"
)
botao_iniciar_leitura.grid(row=0, column=0, padx=20, pady=6)

# Botão para parar leitura
botao_parar_leitura = ctk.CTkButton(
    botoes_leitura,
    text="Parar Leitura",
    width=280,
    height=60,
    font=FONTE_TEXTO,
    fg_color="#e67e22"
)
botao_parar_leitura.grid(row=0, column=1, padx=20, pady=6)

# Botão para retornar ao menu principal
botao_voltar_menu_leitura = ctk.CTkButton(
    frame_leitura,
    text="Voltar ao Menu Principal",
    width=280,
    height=60,
    font=FONTE_TEXTO,
    fg_color="#c0392b",
    command=lambda: [parar_leitura_rfid(), mostrar_menu_inicial()]
)
botao_voltar_menu_leitura.pack(pady=12)


# ------------------- FUNÇÕES RFID FUNCIONAIS -------------------

# Dicionário que guarda o último horário em que cada TAG foi registrada
# Ex: ultimo_registro_tag["AB12FC"] = 1720632704.9273
ultimo_registro_tag = {}

# Tempo mínimo em segundos para aceitar a mesma TAG novamente
INTERVALO_TAG = 3  # Evita spam caso o leitor fique travado detectando a mesma tag


# Função chamada quando uma TAG válida é lida
def registrar_leitura(porta, codigo):
    agora = time.time()

    # --------------------------------------
    # Evita registros duplicados (anti-spam)
    # --------------------------------------
    if codigo in ultimo_registro_tag and (agora - ultimo_registro_tag[codigo]) < INTERVALO_TAG:
        return  # Ignora repetições muito rápidas (menos de 3s)

    # Atualiza o timestamp da última leitura dessa TAG
    ultimo_registro_tag[codigo] = agora

    # Descobre qual ambiente está ligado à porta serial
    id_ferramenta, nome = buscar_ferramenta_por_tag(codigo)

    local = "Sala de Ferramentas" if porta == porta1 else "Sala dos Tornos"

    # Decide em qual caixa de texto escrever
    destino = texto_ferramentas if local == "Sala de Ferramentas" else texto_tornos

    data_hora = datetime.now().strftime("%H:%M:%S %d/%m/%Y")

    # ----------------------------
    # Se a tag for conhecida
    # ----------------------------
    if id_ferramenta:
        # Pega id do usuário logado (se houver)
        id_user = (
            USUARIO_ATUAL[0]['id_usuario']
            if USUARIO_ATUAL[0] and 'id_usuario' in USUARIO_ATUAL[0]
            else None
        )

        # Registra no banco a movimentação
        registrar_movimentacao(
            id_ferramenta, local, id_usuario=id_user
        )

        msg = f"[{data_hora}] {local} -> {nome} captado.\n"

    # ----------------------------
    # TAG desconhecida
    # ----------------------------
    else:
        msg = f"[{data_hora}] {local} -> TAG desconhecida captada.\n"

    # Escreve na tela
    destino.insert(tk.END, msg)
    destino.see(tk.END)  # Auto-scroll para o final da lista


# Thread que faz a leitura da porta serial continuamente
def ler_porta_serial(porta):
    try:
        ser = serial.Serial(porta, baud, timeout=0.1)
    except Exception as e:
        # Se der erro ao abrir a porta, escreve no lugar certo
        destino = texto_ferramentas if porta == porta1 else texto_tornos
        destino.insert(tk.END, f"[ERRO] Falha ao abrir {porta}: {e}\n")
        destino.see(tk.END)
        return

    # Loop enquanto o sistema estiver com leitura ativa
    while capturando_leitura[0]:
        try:
            if ser.in_waiting > 0:  # Se há bytes chegando na porta serial
                raw = ser.readline().decode(errors="ignore").strip()
                codigo = normalizar_tag(raw)

                if len(codigo) > 5:  # Códigos RFID reais têm +5 chars
                    # Atualiza GUI de forma thread-safe
                    frame_leitura.after(0, registrar_leitura, porta, codigo)

            time.sleep(0.05)  # pequena pausa evita CPU em 100%

        except Exception:
            # Qualquer erro na leitura apenas pausa
            time.sleep(0.05)

    ser.close()  # Fecha porta quando leitura é interrompida


# Inicia a leitura em ambas as portas
def iniciar_leitura_rfid():
    if capturando_leitura[0]:  # Se já está lendo, não inicia novamente
        return

    capturando_leitura[0] = True

    # Limpa as janelas de texto
    texto_tornos.delete(1.0, tk.END)
    texto_ferramentas.delete(1.0, tk.END)

    status_leitura.configure(
        text="Leitura em andamento...",
        text_color="lightgreen"
    )

    threads_leitura.clear()

    # Cria uma thread para cada porta serial
    for porta in [porta1, porta2]:
        t = threading.Thread(
            target=ler_porta_serial,
            args=(porta,),
            daemon=True
        )
        t.start()
        threads_leitura.append(t)


# Para a leitura impedindo travamento de threads
def parar_leitura_rfid():
    capturando_leitura[0] = False  # Sinaliza para parar

    # Aguarda finalização das threads com timeout
    for t in threads_leitura:
        t.join(timeout=0.5)

    status_leitura.configure(
        text="Leitura encerrada.",
        text_color="#e67e22"
    )


# Conecta botões aos comandos definidos acima
botao_iniciar_leitura.configure(command=iniciar_leitura_rfid)
botao_parar_leitura.configure(command=parar_leitura_rfid)


# =====================================================
# Funções de troca de tela (simples)
# =====================================================

def mostrar_menu_inicial():
    # Esconde todos os frames dentro do container
    for f in frame_container.winfo_children():
        f.pack_forget()
    # Mostra a tela inicial
    frame_inicial.pack(fill="both", expand=True)
    # Atualiza nome e matrícula do usuário no topo
    atualizar_usuario_logado()


def mostrar_cadastro():
    # Limpa todas as telas visíveis
    for f in frame_container.winfo_children():
        f.pack_forget()
    # Exibe tela de cadastro de TAGs
    frame_cadastro.pack(fill="both", expand=True)
    # Inicia leitura da porta RFID para capturar o código da TAG automaticamente
    iniciar_leitura_tag()


def mostrar_leitura():
    # Esconde telas anteriores
    for f in frame_container.winfo_children():
        f.pack_forget()
    # Mostra a tela de leitura RFID em tempo real
    frame_leitura.pack(fill="both", expand=True)


# =====================================================
# ===================== ADIÇÕES ADMIN ==================
# =====================================================

def login_admin():
    # Lê campos digitados e retira espaço em branco
    usuario = entrada_usuario_login.get().strip() 
    senha = entrada_senha_login.get().strip()

    # Verifica se algo ficou vazio
    if not usuario or not senha:
        label_status_login.configure(text="Preencha todos os campos!", text_color="red")
        return

    # Conecta ao banco
    conn = conectar_banco()
    if not conn:
        label_status_login.configure(text="Erro ao conectar com o banco!", text_color="red")
        return

    try:
        # Consulta tabela de administradores
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM tb_admin WHERE usuario = %s AND senha = %s",
            (usuario, senha)
        )
        admin = cur.fetchone()
        cur.close()
        conn.close()

        if admin:
            # Admin logado — NÃO mexe no USUARIO_ATUAL (só usuários comuns)
            for f in frame_container.winfo_children():
                f.pack_forget()
            abrir_painel_admin()
        else:
            label_status_login.configure(text="Usuário ou senha incorretos!", text_color="red")

    except Error as e:
        print(f"[DB] Erro login_admin: {e}")
        label_status_login.configure(text="Erro ao consultar banco!", text_color="red")



def abrir_painel_admin():
    # Remove todas as telas visíveis
    for f in frame_container.winfo_children():
        f.pack_forget()

    global frame_admin, tree_users_frame
    frame_admin = ctk.CTkFrame(frame_container)
    frame_admin.pack(fill="both", expand=True)

    # Título principal
    titulo_admin = ctk.CTkLabel(frame_admin,
                                text="Painel do Administrador",
                                font=("Arial", 38, "bold"))
    titulo_admin.pack(pady=20)

    topo_frame = ctk.CTkFrame(frame_admin)
    topo_frame.pack(pady=10)

    # Atualiza movimentações + usuários
    bot_atualizar = ctk.CTkButton(
        topo_frame,
        text="Atualizar",
        width=200,
        height=45,
        command=lambda: [carregar_movimentacoes(), carregar_usuarios()],
        fg_color="#27ae60"
    )
    bot_atualizar.pack(side="left", padx=8)

    # Volta para tela de login
    bot_voltar = ctk.CTkButton(
        topo_frame,
        text="Voltar ao Login",
        width=200,
        height=45,
        command=mostrar_login,
        fg_color="#c0392b"
    )
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

