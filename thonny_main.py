from machine import Pin, PWM
import time
import random
import json

# ---- Pines ------------------------------------------------------

AB = Pin(27, Pin.OUT)
CLK = Pin(26, Pin.OUT)

Boton = Pin(16, Pin.IN, Pin.PULL_UP)
Buzzer = PWM(Pin(5))

FilaLed1 = Pin(13, Pin.OUT)
FilaLed2 = Pin(14, Pin.OUT)
FilaLed3 = Pin(15, Pin.OUT)

SW1 = Pin(17, Pin.IN, Pin.PULL_UP)
SW2 = Pin(18, Pin.IN, Pin.PULL_UP)

# ---- Constantes morse -------------------------------------------

DEBOUNCE    = 40
TIEMPO_PUNTO = 300
PAUSA_LETRA  = 800

# ---- Secuencias -------------------------------------------------

SecuenciaAN0 =    [1,0,0,0,0,0,0,0,0,0,0,0,0]
SecuenciaBO1 =    [0,1,0,0,0,0,0,0,0,0,0,0,0]
SecuenciaCP2 =    [0,0,1,0,0,0,0,0,0,0,0,0,0]
SecuenciaDQ3 =    [0,0,0,1,0,0,0,0,0,0,0,0,0]
SecuenciaER4 =    [0,0,0,0,1,0,0,0,0,0,0,0,0]
SecuenciaFS5 =    [0,0,0,0,0,1,0,0,0,0,0,0,0]
SecuenciaGT6 =    [0,0,0,0,0,0,1,0,0,0,0,0,0]
SecuenciaHU7 =    [0,0,0,0,0,0,0,1,0,0,0,0,0]
SecuenciaIV8 =    [0,0,0,0,0,0,0,0,1,0,0,0,0]
SecuenciaJW9 =    [0,0,0,0,0,0,0,0,0,1,0,0,0]
SecuenciaKXmas =  [0,0,0,0,0,0,0,0,0,0,1,0,0]
SecuenciaLYmenos =[0,0,0,0,0,0,0,0,0,0,0,1,0]
SecuenciaMZ =     [0,0,0,0,0,0,0,0,0,0,0,0,1]

Mapa_Letras = {
    "A": (SecuenciaAN0, FilaLed1),"B": (SecuenciaBO1, FilaLed1),
    "C": (SecuenciaCP2, FilaLed1),"D": (SecuenciaDQ3, FilaLed1),
    "E": (SecuenciaER4, FilaLed1),"F": (SecuenciaFS5, FilaLed1),
    "G": (SecuenciaGT6, FilaLed1),"H": (SecuenciaHU7, FilaLed1),
    "I": (SecuenciaIV8, FilaLed1),"J": (SecuenciaJW9, FilaLed1),
    "K": (SecuenciaKXmas, FilaLed1),"L": (SecuenciaLYmenos, FilaLed1),
    "M": (SecuenciaMZ, FilaLed1),

    "N": (SecuenciaAN0, FilaLed2),"O": (SecuenciaBO1, FilaLed2),
    "P": (SecuenciaCP2, FilaLed2),"Q": (SecuenciaDQ3, FilaLed2),
    "R": (SecuenciaER4, FilaLed2),"S": (SecuenciaFS5, FilaLed2),
    "T": (SecuenciaGT6, FilaLed2),"U": (SecuenciaHU7, FilaLed2),
    "V": (SecuenciaIV8, FilaLed2),"W": (SecuenciaJW9, FilaLed2),
    "X": (SecuenciaKXmas, FilaLed2),"Y": (SecuenciaLYmenos, FilaLed2),
    "Z": (SecuenciaMZ, FilaLed2),

    "0": (SecuenciaAN0, FilaLed3),"1": (SecuenciaBO1, FilaLed3),
    "2": (SecuenciaCP2, FilaLed3),"3": (SecuenciaDQ3, FilaLed3),
    "4": (SecuenciaER4, FilaLed3),"5": (SecuenciaFS5, FilaLed3),
    "6": (SecuenciaGT6, FilaLed3),"7": (SecuenciaHU7, FilaLed3),
    "8": (SecuenciaIV8, FilaLed3),"9": (SecuenciaJW9, FilaLed3),
    "+": (SecuenciaKXmas, FilaLed3),"-": (SecuenciaLYmenos, FilaLed3),
}

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

frases = [
    ["P","A","L","O","M","I","T","A","S"],
    ["M","I","L","T","O","N"],
    ["T","E","C"],
    ["S","I"],
    ["H","O","L","A"],
    ["H","O","L","A","M","U","N","D","O"],
    ["N","O"],
    ["3","+","2"],
    ["P","R","I","M","E","R","S","E","M","E","S","T","R","E"],
    ["C","O","D","I","G","O","M","O","R","S","E"]
]


"""Se asocian las entradas a los pines de la RASP"""

# Entradas al circuito incremento
A = Pin(0, Pin.OUT)   # MSB
B = Pin(1, Pin.OUT)
C = Pin(20, Pin.OUT)
D = Pin(21, Pin.OUT)  # LSB

"""De la mismma manera se ingresa el nuevo modo para el SWITCH"""

SW3=Pin(19, Pin.IN, Pin.PULL_UP)

"""El boton, para que se ingresen los dos pares de letras."""

BotonACSII=Pin(16, Pin.IN, Pin.PULL_UP)

"""Diccionario ACSII A BINARIO. Se toma el nibble menos significativo y al final se debe truncar los mas significativos"""

ACSII_a_letra = {
    "01000001":"A", "01000010":"B", "01000011":"C", "01000100":"D",
    "01000101":"E", "01000110":"F", "01000111":"G", "01001000":"H",
    "01001001":"I", "01001010":"J", "01001011":"K", "01001100":"L",
    "01001101":"M", "01001110":"N", "01001111":"O", "01010000":"P",
    "01010001":"Q", "01010010":"R", "01010011":"S", "01010100":"T",
    "01010101":"U", "01010110":"V", "01010111":"W", "01011000":"X",
    "01011001":"Y", "01011010":"Z"
}


"""Aca se reutiliza el codigo para poder tomar la funcion que obtiene la letra que el usuario ingresa para poder proceder con el ajusto"""

def codigo_ASCII():
    # Obtener la letra ingresada en Morse
    letra = obtener_letra_morse()
    if letra is None:
        return None
    
    # Convertir a ASCII
    ascii_val = ord(letra)
    
    # Tomar los 4 bits menos significativos
    lsb4 = ascii_val & 0b1111
    
    # Separar en bits A,B,C,D
    bits = [(lsb4 >> 3) & 1, (lsb4 >> 2) & 1, (lsb4 >> 1) & 1, lsb4 & 1]
    
    print(f"Letra: {letra}, ASCII: {ascii_val}, Bits ABCD: {bits}")
    
    # Asignar a los pines físicos
    A.value(bits[0])
    B.value(bits[1])
    C.value(bits[2])
    D.value(bits[3])
    
    return bits

# Ejemplo de uso
while True:
    if SW3.value() == 0:  # Switch activado
        bits_in = codigo_ASCII()
        if bits_in:
            print("Bits enviados al circuito:", bits_in)
    else:
        time.sleep(0.5)
# Reutilizamos el botón y diccionario de tus fuentes [3, 4]

# ---- Funciones de Soporte ----

def leer_boton():
    """Devuelve True si el botón está presionado con debounce [4]."""
    v1 = Boton.value()
    time.sleep_ms(DEBOUNCE)
    v2 = Boton.value()
    if v1 == v2:
        return v1 == 0  # PULL_UP: 0 es presionado
    return False

def leer_modo():
    """Identifica el modo de juego según los switches [5]."""
    if SW1.value() == 0: return "LOCAL"
    if SW2.value() == 0: return "VERSUS"
    return "NINGUNO"

def actualizar_hardware_ascii(letra):
    """Extrae 4 bits LSB del ASCII y los manda a los pines [6]."""
    val_ascii = ord(letra)
    # Extraer los 4 bits menos significativos (LSB)
    bits = val_ascii & 0x0F 
    
    # Escribir en los pines físicos para el circuito de compuertas
    pin_A.value((bits >> 3) & 1) # Bit 3 (MSB)
    pin_B.value((bits >> 2) & 1) # Bit 2
    pin_C.value((bits >> 1) & 1) # Bit 1
    pin_D.value(bits & 1)        # Bit 0 (LSB) [7]
    
    print(f"Letra: {letra} | ASCII: {val_ascii} | LSB Enviado: {bin(bits)}")

# ---- FUNCIÓN SOLICITADA: Obtener Letra Morse ----

def obtener_letra_morse():
    """
    Lee pulsos del botón y traduce a letra cuando detecta una pausa larga.
    """
    codigo = ""
    while True:
        inicio_silencio = time.ticks_ms()
        
        # 1. Esperar a que el usuario presione el botón o se acabe el tiempo de la letra
        while not leer_boton():
            # Si el silencio supera la PAUSA_LETRA, la letra terminó [1]
            if time.ticks_diff(time.ticks_ms(), inicio_silencio) > PAUSA_LETRA:
                if codigo == "": 
                    return None # No se ingresó nada
                return morse_a_letra.get(codigo, "?")
        
        # 2. El botón fue presionado, medir duración del pulso
        inicio_pulso = time.ticks_ms()
        while leer_boton():
            pass # Esperar a que suelte
        
        duracion = time.ticks_diff(time.ticks_ms(), inicio_pulso)
        
        # 3. Determinar si es punto o raya basado en TIEMPO_PUNTO [1]
        if duracion > TIEMPO_PUNTO:
            codigo += "-"
        else:
            codigo += "."
        
        # Feedback rápido para el usuario
        print(f"Código actual: {codigo}")
# ---- LOOP PRINCIPAL DE INTEGRACIÓN ----

def ejecutar_maqueta():
    print("Sistema StrangerTEC Listo.")
    while True:
        modo = leer_modo()
        if modo == "NINGUNO":
            # Apagar pines si no hay modo
            pin_A.off(); pin_B.off(); pin_C.off(); pin_D.off()
            continue

        # El juego está activo, esperamos letras
        letra_detectada = obtener_letra_morse()
        
        if letra_detectada:
            # Requisito 1: Verificar el Switch de Activación (SW3) [2]
            if SW3.value() == 0:
                # Requisito 2 y 3: Procesar ASCII y enviar al circuito físico [6, 7]
                actualizar_hardware_ascii(letra_detectada)
            else:
                # Si el switch está OFF, limpiar pines
                pin_A.off(); pin_B.off(); pin_C.off(); pin_D.off()
            
            # Aquí enviarías la letra a la PC (VSCODE_MAIN_PC) por Serial
            print(f"Resultado Final: {letra_detectada}")
            
            # Iniciar programa
ejecutar_maqueta()
# ---- Funciones LEDs ---------------------------------------------

def EjecutarSecuencia(sec):
    for i in range(13):
        bit = sec[12 - i]
        AB.value(bit)
        CLK.value(1)
        CLK.value(0)

def MostrarLetra(letra, dur=1):
    if letra not in Mapa_Letras:
        return
    sec, fila = Mapa_Letras[letra]
    EjecutarSecuencia(sec)
    fila.on()
    time.sleep(dur)
    fila.off()
    EjecutarSecuencia([0]*13)

def MostrarFrase(frase):
    for letra in frase:
        MostrarLetra(letra, 1)
        time.sleep(0.5)

# ---- Leer botón con debounce ------------------------------------

def leer_boton():
    """Devuelve True si el botón está presionado (con debounce)."""
    v1 = Boton.value()
    time.sleep_ms(DEBOUNCE)
    v2 = Boton.value()
    if v1 == v2:
        return v1 == 0  # PULL_UP: 0 = presionado
    return False

def esperar_boton_suelto():
    """Espera a que el botón esté completamente suelto antes de continuar."""
    while Boton.value() == 0:
        time.sleep_ms(20)
    time.sleep_ms(100)  # pausa extra para estabilidad

# ---- Turno de un jugador ----------------------------------------

def turno_jugador(nombre, frase):
    print(f"\n--- Turno de {nombre} ---")
    print("Presiona el botón para empezar a escribir en morse...")

    # Espera a que el botón esté suelto antes de empezar
    # (evita leer pulsaciones del turno anterior)
    esperar_boton_suelto()

    morse_actual = ""
    letras_jugador = []
    presionando = False
    inicio = 0
    tiempo_ultima = time.ticks_ms()

    objetivo = "".join(frase)

    while True:
        # ---- Leer botón con debounce ----
        v1 = Boton.value()
        time.sleep_ms(DEBOUNCE)
        v2 = Boton.value()
        estado = v1 if v1 == v2 else None  # None si hay rebote

        if estado is None:
            continue

        # Botón presionado
        if estado == 0 and not presionando:
            presionando = True
            inicio = time.ticks_ms()
            Buzzer.freq(1000)
            Buzzer.duty_u16(30000)

        # Botón suelto
        if estado == 1 and presionando:
            presionando = False
            Buzzer.duty_u16(0)

            duracion = time.ticks_diff(time.ticks_ms(), inicio)

            if duracion < TIEMPO_PUNTO:
                print(".", end="")
                morse_actual += "."
            else:
                print("-", end="")
                morse_actual += "-"

            tiempo_ultima = time.ticks_ms()

        # ---- Fin de letra (pausa detectada) ----
        ahora = time.ticks_ms()
        pausa = time.ticks_diff(ahora, tiempo_ultima)

        if morse_actual != "" and not presionando and pausa > PAUSA_LETRA:
            letra = morse_a_letra.get(morse_actual, "?")
            letras_jugador.append(letra)
            print(f" → {letra}", end=" ")
            morse_actual = ""
            tiempo_ultima = ahora  # reinicia el temporizador

        # ---- Fin del turno ----
        texto = "".join(letras_jugador)
        if len(texto) >= len(objetivo):
            # Espera a que termine de escribir la última letra
            time.sleep_ms(PAUSA_LETRA + 100)

            correctas = sum(1 for a, b in zip(texto, objetivo) if a == b)
            porcentaje = int((correctas / len(objetivo)) * 100)

            print(f"\nEscribiste : {texto}")
            print(f"Correcto   : {objetivo}")
            print(f"Precisión  : {porcentaje}%")

            return porcentaje, texto




def turno_versus(frase):
        """Turno del jugador en la maqueta durante modo versus."""
        print(f"\n--- Turno Versus (Maqueta) ---")
        esperar_boton_suelto()

        morse_actual = ""
        letras_jugador = []
        presionando = False
        inicio = 0
        tiempo_ultima = time.ticks_ms()
        objetivo = "".join(frase)

        while True:
            v1 = Boton.value()
            time.sleep_ms(DEBOUNCE)
            v2 = Boton.value()
            estado = v1 if v1 == v2 else None

            if estado is None:
                continue

            if estado == 0 and not presionando:
                presionando = True
                inicio = time.ticks_ms()
                Buzzer.freq(1000)
                Buzzer.duty_u16(30000)

            if estado == 1 and presionando:
                presionando = False
                Buzzer.duty_u16(0)
                duracion = time.ticks_diff(time.ticks_ms(), inicio)
                if duracion < TIEMPO_PUNTO:
                    morse_actual += "."
                else:
                    morse_actual += "-"
                tiempo_ultima = time.ticks_ms()

            ahora = time.ticks_ms()
            pausa = time.ticks_diff(ahora, tiempo_ultima)

            if morse_actual != "" and not presionando and pausa > PAUSA_LETRA:
                letra = morse_a_letra.get(morse_actual, "?")
                letras_jugador.append(letra)
                print(f" → {letra}", end=" ")
                morse_actual = ""
                tiempo_ultima = ahora

            texto = "".join(letras_jugador)
            if len(texto) >= len(objetivo):
                time.sleep_ms(PAUSA_LETRA + 100)
                correctas = sum(1 for a, b in zip(texto, objetivo) if a == b)
                porcentaje = int((correctas / len(objetivo)) * 100)

            # Enviar resultado a VS Code por serial
                import json
                resultado = {
                    "frase_objetivo": objetivo,
                    "frase_jugador": texto,
                    "porcentaje": porcentaje
                }
                print("\n---- RESULTADO ----")
                print(json.dumps(resultado))

                return porcentaje, texto




# ---- Leer DIP switch --------------------------------------------

def leer_modo():
    """
    DIP con PULL_UP: 0 = switch ON, 1 = switch OFF
    SW1=ON, SW2=OFF → modo local   (SW1=0, SW2=1)
    SW1=OFF, SW2=ON → modo versus  (SW1=1, SW2=0)
    """
    s1 = SW1.value()
    s2 = SW2.value()
    s3 = SW3.value() # Debes leer el pin 19
    if s1 == 0 and s2 == 1:
        return "LOCAL"
    elif s1 == 1 and s2 == 0:
        return "VERSUS"
    elif s3 == 1: # Si el SW3 está en ON (valor 0)
        return "INCREMENTO_ACTIVO"
    else:
        return "NINGUNO"

# ---- LOOP PRINCIPAL ---------------------------------------------

ultimo_modo = ""

while True:
    modo = leer_modo()

    # Solo imprime el modo cuando cambia (evita spam en consola)
    if modo != ultimo_modo:
        print(f"\nModo detectado: {modo}")
        ultimo_modo = modo

    if modo == "LOCAL":
        print("\n========== MODO LOCAL ==========")
        print("Se jugarán 2 rondas. Gana quien acumule más puntos.\n")

        puntaje_total_j1 = 0
        puntaje_total_j2 = 0

        for ronda in range(1, 3):
            print(f"\n---------- RONDA {ronda} ----------")

            FraseActual = random.choice(frases)
            

            print("\nObserva la frase en los LEDs...")
            MostrarFrase(FraseActual)
            time.sleep(1)

            print("\nJugador 1, ¡tu turno!")
            p1, texto1 = turno_jugador("Jugador 1", FraseActual)
            time.sleep(2)

            print("\nObserva la frase otra vez...")
            MostrarFrase(FraseActual)
            time.sleep(1)

            print("\nJugador 2, ¡tu turno!")
            p2, texto2 = turno_jugador("Jugador 2", FraseActual)

            puntaje_total_j1 += p1
            puntaje_total_j2 += p2

            print(f"\n-- Resultado ronda {ronda} --")
            print(f"Jugador 1: {texto1}  →  {p1}%")
            print(f"Jugador 2: {texto2}  →  {p2}%")

            if p1 > p2:
                print(f"Ronda {ronda}: gana Jugador 1")
            elif p2 > p1:
                print(f"Ronda {ronda}: gana Jugador 2")
            else:
                print(f"Ronda {ronda}: empate")

            time.sleep(3)

        # Resultado final
        print("\n========== RESULTADO FINAL ==========")
        print(f"Jugador 1 total: {puntaje_total_j1}%")
        print(f"Jugador 2 total: {puntaje_total_j2}%")

        if puntaje_total_j1 > puntaje_total_j2:
            print("¡¡ GANA JUGADOR 1 !!")
        elif puntaje_total_j2 > puntaje_total_j1:
            print("¡¡ GANA JUGADOR 2 !!")
        else:
            print("¡¡ EMPATE TOTAL !!")

        # ---- Espera a que el switch cambie antes de permitir nueva partida ----
        print("\nCambia el DIP switch para jugar de nuevo.")
        while leer_modo() == "LOCAL":
            time.sleep(0.3)

        ultimo_modo = ""  # resetea para que detecte el cambio correctamente

    elif modo == "VERSUS":
        import json

        print("\n========== MODO VERSUS ==========")
        print("Esperando frase de VS Code...")

        # ---- Esperar frase de VS Code por serial ----
        frase_recibida = None
        while frase_recibida is None:
            linea = input()  # lee del serial
            linea = linea.strip()
            if linea.startswith("FRASE:"):
                datos = linea[6:]  # quita el prefijo
                frase_recibida = json.loads(datos)  # lista de letras

        FraseActual = frase_recibida
        print("Frase recibida:", "".join(FraseActual))

        for ronda in range(1, 3):
            print(f"\n---------- RONDA {ronda} ----------")
            print("Mostrando frase en LEDs...")
            MostrarFrase(FraseActual)
            time.sleep(1)

            print("¡Empieza!")
            porcentaje, texto = turno_versus(FraseActual)

            # Avisar a VS Code que terminó esta ronda
            resultado_ronda = {
                "ronda": ronda,
                "frase_objetivo": "".join(FraseActual),
                "frase_jugador": texto,
                "porcentaje": porcentaje
            }
            print("\n---- RESULTADO ----")
            print(json.dumps(resultado_ronda))

            # Esperar confirmación de VS Code para siguiente ronda
            print("Esperando siguiente ronda...")
            while True:
                linea = input().strip()
                if linea == "SIGUIENTE":
                    break
                elif linea.startswith("FRASE:"):
                    datos = linea[6:]
                    FraseActual = json.loads(datos)
                    break

        # Esperar a que el switch cambie
        print("\nModo versus terminado. Cambia el DIP switch.")
        while leer_modo() == "VERSUS":
            time.sleep(0.3)
        ultimo_modo = ""

    else:
        time.sleep(0.5)  # espera corta cuando no hay modo seleccionado