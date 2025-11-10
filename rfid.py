import serial
import time
import threading
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

# --- Configurações ---
porta1 = "COM5"  # Sala de Ferramentas
porta2 = "COM6"  # Sala dos Tornos
baud = 115200

TAG_ALVO = "10000000000000000000000A"
NOME_TAG = "Chave de Fenda"

INTERVALO_EXIBICAO = 5.0  # segundos por porta

# --- Estado de execução ---
running = [False]

# controle por porta: tempo da última exibição (timestamp), pendente (bool) e local pendente
last_display = {"porta1": 0.0, "porta2": 0.0}
pending = {"porta1": False, "porta2": False}
pending_local = {"porta1": None, "porta2": None}

# evita duplicar a mesma mensagem imediatamente (guarda último (local, hora_str) exibido)
ultimo_registrado = {"sala de ferramentas": None, "sala dos tornos": None}


# --- Funções utilitárias ---
def formatar_msg(local):
    agora = datetime.now()
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M:%S")
    return f"\"{NOME_TAG}\" detectada em {data} às {hora} na {local}"


def adicionar_historico(local, msg):
    # insere na caixa correta (executado via root.after)
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


# chamada para exibir (faz verificação de duplicação rápida)
def exibir_para_local(local):
    msg = formatar_msg(local)
    # evita gravar duas vezes seguidas exatamente iguais (mesmo local, mesma string)
    if ultimo_registrado.get(local) == msg:
        return
    ultimo_registrado[local] = msg
    adicionar_historico(local, msg)


# thread que periodicamente verifica pendentes e exibe quando possível
def pending_watcher():
    while running[0]:
        now = time.time()
        for porta in ("porta1", "porta2"):
            if pending.get(porta):
                if now - last_display.get(porta, 0.0) >= INTERVALO_EXIBICAO:
                    local = pending_local.get(porta)
                    if local:
                        # agendar exibição na thread principal do Tk
                        root.after(0, exibir_para_local, local)
                        last_display[porta] = now
                    pending[porta] = False
                    pending_local[porta] = None
        time.sleep(0.2)


# função que lê os dados de uma porta (cada thread por porta chama esta)
# agora recebe: chave_logica ("porta1"/"porta2"), nome_serial ("COM5"), label_local ("sala de ferramentas")
def leitor_thread(chave_porta, nome_serial, local_label):
    global pending, pending_local, last_display
    try:
        ser = serial.Serial(nome_serial, baud, timeout=0.5)
    except Exception as e:
        # mostra erro na área correspondente
        def show_err():
            if chave_porta == "porta1":
                text_area1.insert(tk.END, f"Erro abrindo {nome_serial}: {e}\n")
                text_area1.see(tk.END)
            else:
                text_area2.insert(tk.END, f"Erro abrindo {nome_serial}: {e}\n")
                text_area2.see(tk.END)
        root.after(0, show_err)
        return

    try:
        while running[0]:
            try:
                if ser.in_waiting > 0:
                    raw = ser.readline().decode(errors="ignore").strip()
                    norm = normalizar_tag(raw)
                    if TAG_ALVO.upper() in norm:
                        now = time.time()
                        # se pode exibir imediatamente (tempo desde última exibição >= intervalo)
                        if now - last_display.get(chave_porta, 0.0) >= INTERVALO_EXIBICAO:
                            # exibir imediatamente
                            root.after(0, exibir_para_local, local_label)
                            last_display[chave_porta] = now
                            # limpa qualquer pendente anterior
                            pending[chave_porta] = False
                            pending_local[chave_porta] = None
                        else:
                            # guarda como pendente: sempre substitui pela última leitura
                            pending[chave_porta] = True
                            pending_local[chave_porta] = local_label
                # pequena pausa para não saturar a CPU
                time.sleep(0.05)
            except serial.SerialException:
                break
            except Exception:
                # ignora decodificações esquisitas e continua
                time.sleep(0.05)
    finally:
        try:
            ser.close()
        except:
            pass


# --- Controle de início/parada ---
def iniciar():
    if not running[0]:
        running[0] = True
        # limpa estado pendente e histórico temporário
        for p in ("porta1", "porta2"):
            pending[p] = False
            pending_local[p] = None
            last_display[p] = 0.0
        # threads de leitura: passamos chave lógica + nome da porta + label
        threading.Thread(target=leitor_thread, args=("porta1", porta1, "sala de ferramentas"), daemon=True).start()
        threading.Thread(target=leitor_thread, args=("porta2", porta2, "sala dos tornos"), daemon=True).start()
        # watcher de pendentes
        threading.Thread(target=pending_watcher, daemon=True).start()
        iniciar_btn.config(state=tk.DISABLED)
        parar_btn.config(state=tk.NORMAL)


def parar():
    running[0] = False
    iniciar_btn.config(state=tk.NORMAL)
    parar_btn.config(state=tk.DISABLED)


# --- GUI ---
root = tk.Tk()
root.title("Controle de Leitores UHF")

try:
    root.state('zoomed')
except:
    pass

top_frame = tk.Frame(root, bg="#2c3e50", height=60)
top_frame.pack(fill=tk.X)

iniciar_btn = tk.Button(top_frame, text="Iniciar Leitura", command=iniciar, bg="#27ae60", fg="white", font=("Arial", 14, "bold"))
iniciar_btn.pack(side=tk.LEFT, padx=10, pady=10)

parar_btn = tk.Button(top_frame, text="Parar Leitura", command=parar, bg="#c0392b", fg="white", font=("Arial", 14, "bold"), state=tk.DISABLED)
parar_btn.pack(side=tk.LEFT, padx=10, pady=10)

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

frame1 = tk.LabelFrame(main_frame, text="sala de ferramentas", font=("Arial", 16, "bold"), fg="#2980b9")
frame1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
text_area1 = scrolledtext.ScrolledText(frame1, font=("Consolas", 16), bg="#ecf0f1", height=10)
text_area1.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

frame2 = tk.LabelFrame(main_frame, text="sala dos tornos", font=("Arial", 16, "bold"), fg="#8e44ad")
frame2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
text_area2 = scrolledtext.ScrolledText(frame2, font=("Consolas", 16), bg="#fdfbfb", height=10)
text_area2.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

root.mainloop()
