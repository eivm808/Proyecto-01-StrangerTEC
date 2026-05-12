import tkinter as tk
import random
import time
import serial
import json
import threading
from PIL import Image, ImageTk

# ---- Serial ------------------------------------------------------

ser = serial.Serial('COM4', 115200, timeout=1)

# ---- Configuracion tiempo ----------------------------------------

unidad = 0.2
raya = unidad * 3
pausa_letra = unidad * 7
pausa_palabra = unidad * 10

# ---- Diccionario -------------------------------------------------

morse_a_letra = {
    ".-":"A", "-...":"B", "-.-.":"C", "-..":"D",
    ".":"E", "..-.":"F", "--.":"G", "....":"H",
    "..":"I", ".---":"J", "-.-":"K", ".-..":"L",
    "--":"M", "-.":"N", "---":"O", ".--.":"P",
    "--.-":"Q", ".-.":"R", "...":"S", "-":"T",
    "..-":"U", "...-":"V", ".--":"W", "-..-":"X",
    "-.--":"Y", "--..":"Z",
    ".----":"1", "..---":"2", "...--":"3", "....-":"4",
    ".....":"5", "-....":"6", "--...":"7", "---..":"8",
    "----.":"9", "-----":"0",
    ".-.-.":"+", "-....-":"-"
}

# ---- Frases ------------------------------------------------------

frases = [
    ["P","A","L","O","M","I","T","A","S"],
    ["M","I","L","T","O","N"],
    ["T","E","C"], ["S","I"], ["H","O","L","A"],
    ["H","O","L","A","M","U","N","D","O"],
    ["N","O"], ["3","+","2"],
    ["P","R","I","M","E","R","S","E","M","E","S","T","R","E"],
    ["C","O","D","I","G","O","M","O","R","S","E"]
]

# ---- Variables globales ------------------------------------------

frase_actual       = []   # lista de letras
frase_str          = ""   # string para mostrar
tiempo_presion     = None
morse_letra_actual = []
letras_ingresadas  = []
timer_letra        = None
timer_espacio      = None
jugando            = False

# Versus
ronda_actual         = 1
puntajes_pc          = []   # puntajes del jugador PC por ronda
puntajes_maqueta     = []   # puntajes del jugador maqueta por ronda
resultado_maqueta    = None # resultado recibido de la Raspberry
esperando_maqueta    = False

# ---- Leer serial en hilo ----------------------------------------

def leer_serial():
    """Hilo que escucha el puerto serial y guarda resultados de la maqueta."""
    global resultado_maqueta
    buffer = ""
    capturando = False

    while True:
        try:
            linea = ser.readline().decode("utf-8", errors="ignore").strip()
            if not linea:
                continue

            if linea == "---- RESULTADO ----":
                capturando = True
                continue

            if capturando:
                datos = json.loads(linea)
                resultado_maqueta = datos
                capturando = False
                print("Resultado maqueta recibido:", datos)
                # Avisar a la interfaz que llegó el resultado
                ventana.after(0, verificar_ambos_terminaron)

        except Exception as e:
            pass

threading.Thread(target=leer_serial, daemon=True).start()

# ---- Enviar frase por serial ------------------------------------

def enviar_frase(frase_lista):
    """Manda la frase a la Raspberry en formato FRASE:["H","O","L","A"]"""
    msg = "FRASE:" + json.dumps(frase_lista) + "\n"
    ser.write(msg.encode())
    print("Frase enviada:", "".join(frase_lista))

def enviar_siguiente():
    """Avisa a la Raspberry que puede empezar la siguiente ronda."""
    ser.write(b"SIGUIENTE\n")

# ---- Logica Morse -----------------------------------------------

def al_presionar(evento):
    global tiempo_presion
    if not jugando:
        return
    if tiempo_presion is None:
        tiempo_presion = time.time()

def al_soltar(evento):
    global tiempo_presion, timer_letra, timer_espacio
    if not jugando or tiempo_presion is None:
        return

    duracion = time.time() - tiempo_presion
    tiempo_presion = None

    if duracion < raya:
        morse_letra_actual.append(".")
    else:
        morse_letra_actual.append("-")

    actualizar()

    if timer_letra:
        ventana.after_cancel(timer_letra)
    if timer_espacio:
        ventana.after_cancel(timer_espacio)

    timer_letra  = ventana.after(int(pausa_letra * 1000), confirmar_letra)
    timer_espacio = ventana.after(int(pausa_palabra * 1000), agregar_espacio)

def confirmar_letra():
    if not morse_letra_actual:
        return
    texto_actual = "".join(letras_ingresadas).replace(" ", "")
    objetivo = frase_str.replace(" ", "")
    if len(texto_actual) >= len(objetivo):
        jugador_pc_termino()
        return
    codigo = "".join(morse_letra_actual)
    letra = morse_a_letra.get(codigo, "?")
    letras_ingresadas.append(letra)
    morse_letra_actual.clear()
    actualizar()
    revisar_fin_pc()

def agregar_espacio():
    if letras_ingresadas and letras_ingresadas[-1] != " ":
        letras_ingresadas.append(" ")
        actualizar()

def revisar_fin_pc():
    texto = "".join(letras_ingresadas).replace(" ", "")
    if len(texto) >= len(frase_str.replace(" ", "")):
        jugador_pc_termino()

# ---- Terminar turno PC ------------------------------------------

def jugador_pc_termino():
    global jugando
    if not jugando:
        return
    jugando = False

    txt = "".join(letras_ingresadas).replace(" ", "")
    objetivo = frase_str.replace(" ", "")
    correctas = sum(1 for a, b in zip(txt, objetivo) if a == b)
    puntaje = int((correctas / len(objetivo)) * 100)

    puntajes_pc.append(puntaje)

    label_estado.config(text=f"Terminaste: {txt} | {puntaje}% — esperando maqueta...")
    print(f"PC terminó ronda {ronda_actual}: {puntaje}%")

    verificar_ambos_terminaron()

def verificar_ambos_terminaron():
    """Se llama cuando cualquiera termina. Si ambos terminaron, muestra resultado."""
    pc_termino      = len(puntajes_pc) >= ronda_actual
    maqueta_termino = resultado_maqueta is not None

    if pc_termino and maqueta_termino:
        mostrar_resultado_ronda()

# ---- Mostrar resultado de ronda ---------------------------------

def mostrar_resultado_ronda():
    global ronda_actual, resultado_maqueta

    p_pc      = puntajes_pc[-1]
    p_maqueta = resultado_maqueta["porcentaje"]
    puntajes_maqueta.append(p_maqueta)
    resultado_maqueta = None  # resetea para la siguiente ronda

    # Ganador de la ronda
    if p_pc > p_maqueta:
        msg = f"Ronda {ronda_actual}: ¡Gana el jugador PC! ({p_pc}% vs {p_maqueta}%)"
    elif p_maqueta > p_pc:
        msg = f"Ronda {ronda_actual}: ¡Gana la maqueta! ({p_maqueta}% vs {p_pc}%)"
    else:
        msg = f"Ronda {ronda_actual}: ¡Empate! ({p_pc}%)"

    label_estado.config(text=msg)

    if ronda_actual < 2:
        # Hay más rondas — preparar la siguiente
        ronda_actual += 1
        boton.config(state="normal", text=f"Iniciar ronda {ronda_actual} (intercambia dispositivos)")
    else:
        # Fin del juego
        mostrar_ganador_final()

# ---- Ganador final ----------------------------------------------

def mostrar_ganador_final():
    total_pc      = sum(puntajes_pc)
    total_maqueta = sum(puntajes_maqueta)

    pantalla = tk.Toplevel(ventana)
    pantalla.title("Resultado Final")
    pantalla.geometry("700x520")
    pantalla.config(bg="#1a1a2e")
    pantalla.grab_set()

    tk.Label(pantalla, text=" RESULTADO FINAL ",
             font=("Arial", 22, "bold"), bg="#1a1a2e", fg="#e94560").pack(pady=20)

    frame = tk.Frame(pantalla, bg="#16213e", bd=2, relief="groove")
    frame.pack(padx=30, pady=10, fill="x")

    # Encabezados
    for col, h in enumerate(["", "PC (teclado)", "Maqueta (botón)"]):
        tk.Label(frame, text=h, font=("Arial", 11, "bold"),
                 bg="#0f3460", fg="white", width=22, pady=8,
                 relief="ridge").grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

    # Puntajes por ronda
    for i, (pp, pm) in enumerate(zip(puntajes_pc, puntajes_maqueta)):
        color_pc  = "#00b894" if pp >= pm else "#e17055"
        color_maq = "#00b894" if pm >= pp else "#e17055"
        tk.Label(frame, text=f"Ronda {i+1}", font=("Arial", 10, "bold"),
                 bg="#1a1a2e", fg="#a8dadc", pady=6).grid(row=i+1, column=0, sticky="nsew", padx=1, pady=1)
        tk.Label(frame, text=f"{pp}%", font=("Arial", 13, "bold"),
                 bg="#1a1a2e", fg=color_pc, pady=6).grid(row=i+1, column=1, sticky="nsew", padx=1, pady=1)
        tk.Label(frame, text=f"{pm}%", font=("Arial", 13, "bold"),
                 bg="#1a1a2e", fg=color_maq, pady=6).grid(row=i+1, column=2, sticky="nsew", padx=1, pady=1)

    # Total
    color_tot_pc  = "#00b894" if total_pc >= total_maqueta else "#e17055"
    color_tot_maq = "#00b894" if total_maqueta >= total_pc else "#e17055"
    tk.Label(frame, text="TOTAL", font=("Arial", 11, "bold"),
             bg="#1a1a2e", fg="white", pady=6).grid(row=3, column=0, sticky="nsew", padx=1, pady=1)
    tk.Label(frame, text=f"{total_pc}%", font=("Arial", 15, "bold"),
             bg="#1a1a2e", fg=color_tot_pc, pady=6).grid(row=3, column=1, sticky="nsew", padx=1, pady=1)
    tk.Label(frame, text=f"{total_maqueta}%", font=("Arial", 15, "bold"),
             bg="#1a1a2e", fg=color_tot_maq, pady=6).grid(row=3, column=2, sticky="nsew", padx=1, pady=1)

    # Ganador
    if total_pc > total_maqueta:
        msg = "¡Gana el jugador PC!"
        color = "#00b894"
    elif total_maqueta > total_pc:
        msg = "¡Gana la maqueta!"
        color = "#00b894"
    else:
        msg = "¡Empate total!"
        color = "#fdcb6e"

    tk.Label(pantalla, text=msg, font=("Arial", 18, "bold"),
             bg="#1a1a2e", fg=color).pack(pady=20)

    tk.Button(pantalla, text="Cerrar", command=pantalla.destroy,
              font=("Arial", 11), bg="#e94560", fg="white",
              padx=20, pady=6, relief="flat", cursor="hand2").pack()

    boton.config(state="disabled", text="Iniciar")

# ---- Display ----------------------------------------------------

def actualizar():
    txt_morse = " ".join(morse_letra_actual) if morse_letra_actual else "esperando..."
    label_morse.config(text=txt_morse)
    txt_letras = " ".join(letras_ingresadas)
    label_ingresado.config(text="Ingresado: " + txt_letras)
    texto = "".join(letras_ingresadas).replace(" ", "")
    label_progreso.config(text=f"{len(texto)}/{len(frase_str.replace(' ', ''))} letras")

# ---- Iniciar ronda ----------------------------------------------

def iniciar():
    global frase_actual, frase_str, letras_ingresadas
    global morse_letra_actual, jugando, resultado_maqueta

    if timer_letra:
        ventana.after_cancel(timer_letra)
    if timer_espacio:
        ventana.after_cancel(timer_espacio)

    # Elegir frase nueva para esta ronda
    frase_actual = random.choice(frases)
    frase_str    = "".join(frase_actual)

    letras_ingresadas  = []
    morse_letra_actual = []
    resultado_maqueta  = None
    jugando            = True

    # Enviar frase a la Raspberry
    enviar_frase(frase_actual)

    label_frase.config(text=f"Ronda {ronda_actual} — Frase: {frase_str}")
    label_estado.config(text="¡Jugando! Escribe en morse con la barra espaciadora")
    label_ingresado.config(text="Ingresado: ")
    label_morse.config(text="...")
    label_progreso.config(text=f"0/{len(frase_str)} letras")
    boton.config(state="disabled")

# ---- Interfaz ---------------------------------------------------

ventana = tk.Tk()
ventana.title("StrangerTEC — Modo Versus")
ventana.geometry("1000x800")
ventana.config(bg="white")

tk.Label(ventana, text="Stranger TEC — Versus",
         font=('Arial', 22, 'bold'), bg='white', fg='black').pack(pady=15)

label_frase    = tk.Label(ventana, text="Presiona iniciar para comenzar", font=("Arial", 13))
label_frase.pack(pady=10)

label_morse    = tk.Label(ventana, text="...", font=("Arial", 20))
label_morse.pack(pady=10)

label_ingresado = tk.Label(ventana, text="Ingresado: ", font=("Arial", 12))
label_ingresado.pack()

label_progreso  = tk.Label(ventana, text="", font=("Arial", 11))
label_progreso.pack()

label_estado    = tk.Label(ventana, text="", font=("Arial", 11), wraplength=800)
label_estado.pack(pady=10)

boton = tk.Button(ventana, text="Iniciar ronda 1", command=iniciar,
                  font=("Arial", 13), padx=15, pady=8)
boton.pack(pady=10)

ventana.bind("<KeyPress-space>",   al_presionar)
ventana.bind("<KeyRelease-space>", al_soltar)

ruta_img_morse = "Imagenes\\morse.png"
img_morse = Image.open(ruta_img_morse)
img_morse = img_morse.resize((480, 400))
img_morse_tk = ImageTk.PhotoImage(img_morse)
tk.Label(ventana, image=img_morse_tk).place(x=250, y=350)

ventana.mainloop()