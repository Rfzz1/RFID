import serial
import time
import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import scrolledtext
from datetime import datetime

### ADIÇÃO MYSQL ###
import mysql.connector
from mysql.connector import Error

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

def registrar_movimentacao(id_ferramenta, local, observacao=None):
    conn = conectar_banco()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO tb_movimentacoes (id_usuario, id_ferramentas, data_retirada, data_devolucao, observacao)
            VALUES (%s, %s, NOW(), NOW(), %s)
        """, (1, id_ferramenta, observacao or f"Leitura de {local}"))
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
### FIM ADIÇÃO MYSQL ###


# =========== Configurações ===========
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

# ======= FUNÇÕES =======
def formatar_msg(local):
    agora = datetime.now()
    return f"\"{NOME_TAG}\" detectada em {agora.strftime('%d/%m/%Y')} às {agora.strftime('%H:%M:%S')} na {local}"

def adicionar_historico(local, msg):
    if local == "sala de ferramentas":
        text_area1.insert(tk.END, msg + "\n")
        text_area1.see(tk.END)
    elif local == "sala dos tornos":
        text_area2.insert(tk.END, msg + "\n")
        text_area2.see(tk.END)

def normalizar_tag(raw):
    if raw is None:
        return ""
    s = "".join(ch for ch in raw if ch.isalnum())
    return s.upper()

def exibir_para_local(local):
    msg = formatar_msg(local)
    if ultimo_registrado.get(local) == msg:
        return
    ultimo_registrado[local] = msg
    adicionar_historico(local, msg)

def pending_watcher():
    while running[0]:
        now = time.time()
        for porta in ("porta1", "porta2"):
            if pending.get(porta):
                if now - last_display.get(porta, 0.0) >= INTERVALO_EXIBICAO:
                    local = pending_local.get(porta)
                    if local:
                        main_window.after(0, exibir_para_local, local)
                        last_display[porta] = now
                    pending[porta] = False
                    pending_local[porta] = None
        time.sleep(0.2)

def leitor_thread(chave_porta, nome_serial, local_label):
    global pending, pending_local, last_display
    try:
        ser = serial.Serial(nome_serial, baud, timeout=0.5)
    except Exception as e:
        def show_err():
            if chave_porta == "porta1":
                text_area1.insert(tk.END, f"Erro abrindo {nome_serial}: {e}\n")
                text_area1.see(tk.END)
            else:
                text_area2.insert(tk.END, f"Erro abrindo {nome_serial}: {e}\n")
                text_area2.see(tk.END)
        main_window.after(0, show_err)
        return

    try:
        while running[0]:
            try:
                if ser.in_waiting > 0:
                    raw = ser.readline().decode(errors="ignore").strip()
                    norm = normalizar_tag(raw)
                    if TAG_ALVO.upper() in norm:
                        ### ADIÇÃO MYSQL: busca e registra movimentação ###
                        id_ferr, nome_ferr = buscar_ferramenta_por_tag(norm)
                        if id_ferr:
                            threading.Thread(
                                target=registrar_movimentacao,
                                args=(id_ferr, local_label, f"Leitura da TAG {norm}"),
                                daemon=True
                            ).start()
                            main_window.after(0, adicionar_historico, local_label,
                                f"✅ TAG '{nome_ferr}' registrada no banco ({norm})")
                        else:
                            main_window.after(0, adicionar_historico, local_label,
                                f"⚠️ TAG não cadastrada no banco: {norm}")
                        ### FIM ADIÇÃO MYSQL ###

                        now = time.time()
                        if now - last_display.get(chave_porta, 0.0) >= INTERVALO_EXIBICAO:
                            main_window.after(0, exibir_para_local, local_label)
                            last_display[chave_porta] = now
                            pending[chave_porta] = False
                            pending_local[chave_porta] = None
                        else:
                            pending[chave_porta] = True
                            pending_local[chave_porta] = local_label
                time.sleep(0.05)
            except serial.SerialException:
                break
            except Exception:
                time.sleep(0.05)
    finally:
        try:
            ser.close()
        except:
            pass

def iniciar():
    if not running[0]:
        running[0] = True
        for p in ("porta1", "porta2"):
            pending[p] = False
            pending_local[p] = None
            last_display[p] = 0.0
        threading.Thread(target=leitor_thread, args=("porta1", porta1, "sala de ferramentas"), daemon=True).start()
        threading.Thread(target=leitor_thread, args=("porta2", porta2, "sala dos tornos"), daemon=True).start()
        threading.Thread(target=pending_watcher, daemon=True).start()
        iniciar_btn.configure(state=tk.DISABLED)
        parar_btn.configure(state=tk.NORMAL)

def parar():
    running[0] = False
    iniciar_btn.configure(state=tk.NORMAL)
    parar_btn.configure(state=tk.DISABLED)

# ======= INTERFACE =======
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

janela_inicial = ctk.CTk()
janela_inicial.attributes('-fullscreen', True)
janela_inicial.title("Sistema de Leitura UHF")

# -------- CONTAINER DE TELAS --------
frame_container = ctk.CTkFrame(janela_inicial)
frame_container.pack(fill="both", expand=True)

# ========== TELA INICIAL ==========
frame_inicial = ctk.CTkFrame(frame_container)
frame_inicial.pack(fill="both", expand=True)

label_titulo = ctk.CTkLabel(frame_inicial, text="Sistema de Leitura UHF", font=("Arial", 38, "bold"))
label_titulo.pack(pady=80)

def abrir_area_de_trabalho():
    frame_inicial.pack_forget()
    criar_area_principal()

def mostrar_cadastro():
    frame_inicial.pack_forget()
    frame_cadastro.pack(fill="both", expand=True)
    iniciar_leitura_tag()  # inicia leitura automática da tag

botao_entrar = ctk.CTkButton(frame_inicial, text="Entrar na Área de Trabalho", command=abrir_area_de_trabalho, width=250, height=50, fg_color="#2980b9", hover_color="#1f5f8a", font=("Arial", 18))
botao_entrar.pack(pady=20)

botao_cadastrar = ctk.CTkButton(frame_inicial, text="Cadastrar TAGs", command=mostrar_cadastro, width=250, height=50, fg_color="#8e44ad", hover_color="#6c3483", font=("Arial", 18))
botao_cadastrar.pack(pady=20)

botao_sair = ctk.CTkButton(frame_inicial, text="Sair", command=janela_inicial.destroy, width=200, height=40, fg_color="#c0392b", hover_color="#992d22", font=("Arial", 16))
botao_sair.pack(pady=40)

# ========== TELA DE CADASTRO ==========
frame_cadastro = ctk.CTkFrame(frame_container)

label_cadastro = ctk.CTkLabel(frame_cadastro, text="Cadastro de TAGs", font=("Arial", 32, "bold"))
label_cadastro.pack(pady=40)

label_nome = ctk.CTkLabel(frame_cadastro, text="Nome da TAG:", font=("Arial", 18))
label_nome.pack(pady=10)
entrada_nome = ctk.CTkEntry(frame_cadastro, width=400, height=40, font=("Arial", 16))
entrada_nome.pack()

label_codigo = ctk.CTkLabel(frame_cadastro, text="Código da TAG (detectado automaticamente):", font=("Arial", 18))
label_codigo.pack(pady=10)
entrada_codigo = ctk.CTkEntry(frame_cadastro, width=400, height=40, font=("Arial", 16))
entrada_codigo.pack()

label_status = ctk.CTkLabel(frame_cadastro, text="", text_color="lightgreen", font=("Arial", 16))
label_status.pack(pady=20)

capturando_tag = [False]
thread_leitura_tag = [None]

def ler_tag_cadastro():
    try:
        ser = serial.Serial(porta1, baud, timeout=0.5)
    except Exception as e:
        frame_cadastro.after(0, lambda: label_status.configure(
            text=f"Erro abrindo {porta1}: {e}", text_color="red"))
        return

    while capturando_tag[0]:
        try:
            if ser.in_waiting > 0:
                raw = ser.readline().decode(errors="ignore").strip()
                codigo = normalizar_tag(raw)
                if len(codigo) > 5:
                    frame_cadastro.after(0, preencher_codigo_detectado, codigo)
            time.sleep(0.1)
        except Exception:
            time.sleep(0.05)
    try:
        ser.close()
    except:
        pass

def preencher_codigo_detectado(codigo):
    entrada_codigo.delete(0, tk.END)
    entrada_codigo.insert(0, codigo)
    label_status.configure(text=f"TAG detectada: {codigo}", text_color="lightgreen")

def iniciar_leitura_tag():
    if not capturando_tag[0]:
        capturando_tag[0] = True
        thread_leitura_tag[0] = threading.Thread(target=ler_tag_cadastro, daemon=True)
        thread_leitura_tag[0].start()

def parar_leitura_tag():
    capturando_tag[0] = False
    time.sleep(0.1)

def salvar_tag():
    nome = entrada_nome.get().strip()
    codigo = entrada_codigo.get().strip().upper()
    if not nome or not codigo:
        label_status.configure(text="Preencha todos os campos!", text_color="red")
        return
    TAGS_CADASTRADAS.append({"nome": nome, "codigo": codigo})
    ### ADIÇÃO MYSQL ###
    sucesso = salvar_tag_no_banco(nome, codigo)
    if sucesso:
        label_status.configure(text=f"TAG '{nome}' salva no banco!", text_color="lightgreen")
    else:
        label_status.configure(text=f"Erro ao salvar no banco!", text_color="red")
    ### FIM ADIÇÃO MYSQL ###
    entrada_nome.delete(0, tk.END)
    entrada_codigo.delete(0, tk.END)

def voltar_menu():
    parar_leitura_tag()
    frame_cadastro.pack_forget()
    frame_inicial.pack(fill="both", expand=True)
    label_status.configure(text="")

botao_salvar = ctk.CTkButton(frame_cadastro, text="Salvar", command=salvar_tag,
                             width=200, height=45, fg_color="#27ae60",
                             hover_color="#219150", font=("Arial", 16))
botao_salvar.pack(pady=15)

botao_voltar = ctk.CTkButton(frame_cadastro, text="Voltar", command=voltar_menu,
                             width=200, height=45, fg_color="#c0392b",
                             hover_color="#992d22", font=("Arial", 16))
botao_voltar.pack(pady=15)

# ========== ÁREA PRINCIPAL ==========
def criar_area_principal():
    global main_window, text_area1, text_area2, iniciar_btn, parar_btn
    main_window = janela_inicial

    frame_area = ctk.CTkFrame(frame_container)
    frame_area.pack(fill="both", expand=True)

    top_frame = ctk.CTkFrame(frame_area, fg_color="#2c3e50", height=100)
    top_frame.pack(fill="x")

    iniciar_btn = ctk.CTkButton(top_frame, text="Iniciar Leitura", command=iniciar, fg_color="#27ae60", hover_color="#219150", text_color="white", font=("Arial", 16, "bold"), width=140, height=45)
    iniciar_btn.pack(side="left", padx=15, pady=25)

    parar_btn = ctk.CTkButton(top_frame, text="Parar Leitura", command=parar, fg_color="#c0392b", hover_color="#992d22", text_color="white", font=("Arial", 16, "bold"), state="disabled", width=140, height=45)
    parar_btn.pack(side="left", padx=15, pady=25)

    botao_voltar_area = ctk.CTkButton(top_frame, text="Voltar ao Menu", command=lambda: voltar_menu_area(frame_area), fg_color="#34495e", hover_color="#2c3e50", font=("Arial", 16, "bold"), width=160, height=45)
    botao_voltar_area.pack(side="right", padx=15, pady=25)

    main_frame = ctk.CTkFrame(frame_area, fg_color="#000000")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    frame1 = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=10)
    frame1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    label1 = ctk.CTkLabel(frame1, text="Sala de Ferramentas", font=("Arial", 22, "bold"), text_color="#2980b9")
    label1.pack(pady=(20, 5))
    global text_area1
    text_area1 = scrolledtext.ScrolledText(frame1, font=("Consolas", 16), bg="#A3A1A1", height=10)
    text_area1.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    frame2 = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=10)
    frame2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    label2 = ctk.CTkLabel(frame2, text="Sala dos Tornos", font=("Arial", 22, "bold"), text_color="#8e44ad")
    label2.pack(pady=(20, 5))
    global text_area2
    text_area2 = scrolledtext.ScrolledText(frame2, font=("Consolas", 16), bg="#A3A1A1", height=10)
    text_area2.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def voltar_menu_area(frame_atual):
        parar()
        frame_atual.pack_forget()
        frame_inicial.pack(fill="both", expand=True)

janela_inicial.mainloop()
