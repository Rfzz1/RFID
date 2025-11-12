#============= BIBLIOTECAS ============
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

# =========== configurações ===========
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

### ADIÇÃO MYSQL ###
def conectar_banco():
    """Conecta ao banco db_rfid"""
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',           # <=== altere se necessário
            password='',           # <=== senha do seu MySQL
            database='db_rfid'
        )
        return conexao
    except Error as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def buscar_ferramenta_por_tag(codigo_tag):
    """Retorna nome e id da ferramenta associada a uma tag RFID"""
    conexao = conectar_banco()
    if not conexao:
        return None, None
    try:
        cursor = conexao.cursor()
        query = """
            SELECT f.id_ferramentas, f.nome 
            FROM tb_ferramentas f
            JOIN tb_rfid_tags t ON f.id_ferramentas = t.id_ferramenta
            WHERE t.codigo_tag = %s
        """
        cursor.execute(query, (codigo_tag,))
        resultado = cursor.fetchone()
        cursor.close()
        conexao.close()
        if resultado:
            return resultado[0], resultado[1]
        else:
            return None, None
    except Error as e:
        print(f"Erro ao buscar ferramenta: {e}")
        return None, None

def registrar_movimentacao(id_ferramenta, local):
    """Insere registro de movimentação no banco"""
    conexao = conectar_banco()
    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        query = """
            INSERT INTO tb_movimentacoes (id_usuario, id_ferramentas, data_retirada, data_devolucao, observacao)
            VALUES (%s, %s, NOW(), NOW(), %s)
        """
        cursor.execute(query, (1, id_ferramenta, f"Leitura detectada na {local}"))
        conexao.commit()
        cursor.close()
        conexao.close()
    except Error as e:
        print(f"Erro ao registrar movimentação: {e}")

# =============== FUNÇÕES ===================
def formatar_msg(local):
    agora = datetime.now()
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M:%S")
    return f"\"{NOME_TAG}\" detectada em {data} às {hora} na {local}"

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

    ### ADIÇÃO MYSQL ###
    # Quando a TAG for exibida, faz a consulta e registra no banco
    id_ferramenta, nome_ferramenta = buscar_ferramenta_por_tag(TAG_ALVO)
    if id_ferramenta:
        registrar_movimentacao(id_ferramenta, local)
        print(f"Movimentação registrada para: {nome_ferramenta}")
    else:
        print(f"Nenhuma ferramenta encontrada para a TAG {TAG_ALVO}")

def pending_watcher():
    while running[0]:
        now = time.time()
        for porta in ("porta1", "porta2"):
            if pending.get(porta):
                if now - last_display.get(porta, 0.0) >= INTERVALO_EXIBICAO:
                    local = pending_local.get(porta)
                    if local:
                        janela.after(0, exibir_para_local, local)
                        last_display[porta] = now
                    pending[porta] = False
                    pending_local[porta] = None
        time.sleep(0.2)

def leitor_thread(chave_porta, nome_serial, local_label):
    global pending, pending_local, last_display
    try:
        ser = serial.Serial(nome_serial, baud, timeout=0.5)
    except Exception as e:
        def show_err(err=e):
            if chave_porta == "porta1":
                text_area1.insert(tk.END, f"Erro abrindo {nome_serial}: {err}\n")
                text_area1.see(tk.END)
            else:
                text_area2.insert(tk.END, f"Erro abrindo {nome_serial}: {err}\n")
                text_area2.see(tk.END)
        janela.after(0, show_err)
        return

    try:
        while running[0]:
            try:
                if ser.in_waiting > 0:
                    raw = ser.readline().decode(errors="ignore").strip()
                    norm = normalizar_tag(raw)
                    if TAG_ALVO.upper() in norm:
                        now = time.time()
                        if now - last_display.get(chave_porta, 0.0) >= INTERVALO_EXIBICAO:
                            janela.after(0, exibir_para_local, local_label)
                            last_display[chave_porta] = now
                            pending[chave_porta] = False
                            pending_local[chave_porta] = None
                        else:
                            pending[chave_porta] = True
                            pending_local[chave_porta] = local_label
                time.sleep(0.05)
            except serial.SerialException:
                break
            except Exception as e:
                print(f"Erro na thread {chave_porta}: {e}")
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

# --- Interface Gráfica (Tkinter) ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
janela = ctk.CTk()
janela.attributes('-fullscreen', True)
janela.title("Registro de leitura UHF")

top_frame = ctk.CTkFrame(janela, fg_color="#2c3e50", height=100)
top_frame.pack(fill="x")

iniciar_btn = ctk.CTkButton(top_frame,text="Iniciar Leitura", command=iniciar, fg_color="#27ae60", hover_color="#219150", text_color="white", font=ctk.CTkFont(family="Arial", size=16, weight="bold"), width=120, height=50)
iniciar_btn.pack(side="left", padx=10, pady=30)

parar_btn = ctk.CTkButton(top_frame,text="Parar Leitura",command=parar,fg_color="#c0392b",hover_color="#992d22",text_color="white",font=ctk.CTkFont(family="Arial", size=16, weight="bold"),state="disabled", width=120, height=50)
parar_btn.pack(side="left", padx=10, pady=30)

main_frame = ctk.CTkFrame(janela, fg_color="#000000")
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

frame1 = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=10)
frame1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

label1 = ctk.CTkLabel(frame1, text="Sala de Ferramentas", font=("Arial", 18, "bold"), text_color="#2980b9")
label1.pack(pady=(20, 5))

text_area1 = scrolledtext.ScrolledText(frame1, font=("Consolas", 16), bg="#A3A1A1", height=10)
text_area1.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

frame2 = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=10)
frame2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

label2 = ctk.CTkLabel(frame2, text="Sala dos Tornos", font=("Arial", 18, "bold"), text_color="#8e44ad")
label2.pack(pady=(20, 5))

text_area2 = scrolledtext.ScrolledText(frame2, font=("Consolas", 16), bg="#A3A1A1", height=10)
text_area2.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

janela.mainloop()
