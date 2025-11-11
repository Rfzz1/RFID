#============= BIBLIOTECAS ============
import serial                    # Comunicação via porta serial (para ler dados do leitor RFID)
import time                      # Controle de tempo (pausas, timestamps etc.)
import threading                 # Executar múltiplas tarefas ao mesmo tempo (threads)
import tkinter as tk             # Criação da interface gráfica
import customtkinter as ctk      # Interface Gráfica
from tkinter import scrolledtext # Área de texto com barra de rolagem
from datetime import datetime    # Trabalhar com data e hora

# =========== Configurações ===========
porta1 = "COM5"  # Sala de Ferramentas
porta2 = "COM6"  # Sala dos Tornos
baud = 115200    # Mudanças de Sinais transmitidos por segundo am um canal de comunicação

TAG_ALVO = "10000000000000000000000A" # Declaração da TAG
NOME_TAG = "Chave de Fenda"           # Nome da TAG
INTERVALO_EXIBICAO = 5.0  # Tempo mínimo entre exibições por porta (em segundos)

# ========== Estado de execução ============
running = [False]

# ========== Controle por porta ============
last_display = {"porta1": 0.0, "porta2": 0.0}    # Guarda o timestamp da última exibição
pending = {"porta1": False, "porta2": False}     # Indica se há uma leitura pendente
pending_local = {"porta1": None, "porta2": None} # Guarda o local da leitura pendente

# === Evita duplicar a mesma mensagem imediatamente ===
ultimo_registrado = {"Sala de Ferramentas": None, "Sala dos Tornos": None} # Guarda último (local, hora_str) exibido


# =============== FUNÇÕES ===================

# --- Função para formatar mensagem ---
def formatar_msg(local):
    agora = datetime.now()            # Data e Hora atual
    data = agora.strftime("%d/%m/%Y") # Data Formatada em D/M/Y
    hora = agora.strftime("%H:%M:%S") # Hora Formatada em H/M/S
    return f"\"{NOME_TAG}\" detectada em {data} às {hora} na {local}" # Retorno da leitura do RFID formatada

# --- Função para Registrar Histórico das Movimentações ---
def adicionar_historico(local, msg):
    if local == "sala de ferramentas":
        text_area1.insert(tk.END, msg + "\n") # Insere a mensagem
        text_area1.see(tk.END)                # Rola automaticamente até a última linha
    elif local == "sala dos tornos":
        text_area2.insert(tk.END, msg + "\n") # Insere a mensagem
        text_area2.see(tk.END)                # Rola automaticamente até a última linha

# --- Função que limpa o valor lido da porta serial ---
def normalizar_tag(raw):
    if raw is None:
        return ""
    s = "".join(ch for ch in raw if ch.isalnum()) # Mantém apenas letras e números
    return s.upper()                              # Converte tudo para maiúsculo

# --- Função que faz verificação dupla de leitura ---
def exibir_para_local(local):
    msg = formatar_msg(local)
    if ultimo_registrado.get(local) == msg: # Se for igual à última exibida, ignora
        return
    ultimo_registrado[local] = msg          # Atualiza a última mensagem
    adicionar_historico(local, msg)         # Mostra no histórico

# --- Thread que periodicamente verifica pendentes e exibe quando possível ---
def pending_watcher():
    while running[0]: # Roda enquanto o sistema estiver ativo
        now = time.time()
        for porta in ("porta1", "porta2"):
            if pending.get(porta): # Se há algo pendente
                # Verifica se o tempo mínimo já passou
                if now - last_display.get(porta, 0.0) >= INTERVALO_EXIBICAO:
                    local = pending_local.get(porta)
                    if local:
                        # Executa exibição na thread principal do Tkinter
                        janela.after(0, exibir_para_local, local)
                        last_display[porta] = now
                    # Limpa o estado pendente
                    pending[porta] = False
                    pending_local[porta] = None
        time.sleep(0.2) # Limpa o estado pendente


# --- Thread responsável por ler dados de uma porta serial ---
def leitor_thread(chave_porta, nome_serial, local_label):
    global pending, pending_local, last_display
    try:
        # Tenta abrir a porta serial
        ser = serial.Serial(nome_serial, baud, timeout=0.5)
    except Exception as e:
        # Se der erro, exibe a mensagem na área correspondente
        def show_err():
            if chave_porta == "porta1":
                text_area1.insert(tk.END, f"Erro abrindo {nome_serial}: {e}\n")
                text_area1.see(tk.END)
            else:
                text_area2.insert(tk.END, f"Erro abrindo {nome_serial}: {e}\n")
                text_area2.see(tk.END)
        janela.after(0, show_err)
        return

    try:
        # Loop principal de leitura
        while running[0]:
            try:
                if ser.in_waiting > 0: # Se há dados disponíveis na porta
                    raw = ser.readline().decode(errors="ignore").strip() # Lê e decodifica a linha
                    norm = normalizar_tag(raw) # Normaliza o conteúdo lido
                    if TAG_ALVO.upper() in norm: # Se a TAG alvo foi detectada
                        now = time.time()
                        # Verifica se já passou o intervalo de exibição
                        if now - last_display.get(chave_porta, 0.0) >= INTERVALO_EXIBICAO:
                            # Exibe imediatamente
                            janela.after(0, exibir_para_local, local_label)
                            last_display[chave_porta] = now
                            # Limpa pendências
                            pending[chave_porta] = False
                            pending_local[chave_porta] = None
                        else:
                            # Se ainda não passou tempo suficiente, marca como pendente
                            pending[chave_porta] = True
                            pending_local[chave_porta] = local_label
                time.sleep(0.05)  # Evita sobrecarregar a CPU
            except serial.SerialException:
                break # Sai do loop se houver erro de conexão
            except Exception:
                # Ignora erros eventuais de leitura/decodificação
                time.sleep(0.05)
    finally:
        # Fecha a porta ao encerrar
        try:
            ser.close()
        except:
            pass


# --- Controle de início/parada ---
def iniciar():
    if not running[0]:
        running[0] = True # Liga o sistema
        # Reseta variáveis de controle
        for p in ("porta1", "porta2"):
            pending[p] = False
            pending_local[p] = None
            last_display[p] = 0.0
        # Cria threads para cada leitor e o verificador de pendências
        threading.Thread(target=leitor_thread, args=("porta1", porta1, "sala de ferramentas"), daemon=True).start()
        threading.Thread(target=leitor_thread, args=("porta2", porta2, "sala dos tornos"), daemon=True).start()
        threading.Thread(target=pending_watcher, daemon=True).start()
        # Atualiza os botões
        iniciar_btn.config(state=tk.DISABLED)
        parar_btn.config(state=tk.NORMAL)

# --- Para a leitura --
def parar():
    running[0] = False
    iniciar_btn.config(state=tk.NORMAL)
    parar_btn.config(state=tk.DISABLED)


# --- Interface Gráfica (Tkinter) ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
janela = ctk.CTk()
janela.attributes('-fullscreen', True)
janela.title("Registro de leitura UHF")


# --- Barra superior com botões ---
top_frame = ctk.CTkFrame(janela, fg_color="#2c3e50", height=100)
top_frame.pack(fill="x")

iniciar_btn = ctk.CTkButton(top_frame,text="Iniciar Leitura", command=iniciar, fg_color="#27ae60", hover_color="#219150", text_color="white", font=ctk.CTkFont(family="Arial", size=14, weight="bold"), width=120, height=40)
iniciar_btn.pack(side="left", padx=10, pady=30)

parar_btn = ctk.CTkButton(top_frame,text="Parar Leitura",command=parar,fg_color="#c0392b",hover_color="#992d22",text_color="white",font=ctk.CTkFont(family="Arial", size=14, weight="bold"),state="disabled", width=120, height=40)
parar_btn.pack(side="left", padx=10, pady=30)

# --- Área principal (duas janelas de texto lado a lado) ---
main_frame = ctk.CTkFrame(janela, fg_color="#000000")
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# --- Sala de Ferramentas ---
frame1 = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=10)
frame1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

label1 = ctk.CTkLabel(frame1, text="Sala de Ferramentas", font=("Arial", 18, "bold"), text_color="#2980b9")
label1.pack(pady=(20, 5))

text_area1 = scrolledtext.ScrolledText(frame1, font=("Consolas", 16), bg="#A3A1A1", height=10)
text_area1.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# --- Sala dos Tornos ---
frame2 = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=10)
frame2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

label2 = ctk.CTkLabel(frame2, text="Sala dos Tornos", font=("Arial", 18, "bold"), text_color="#8e44ad")
label2.pack(pady=(10, 5))

text_area2 = scrolledtext.ScrolledText(frame2, font=("Consolas", 16), bg="#A3A1A1", height=10)
text_area2.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


# --- Loop principal da interface ---
janela.mainloop()
