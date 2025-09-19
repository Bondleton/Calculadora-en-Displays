import tkinter as tk
import serial
import threading

# --- Configuración del puerto serie ---
try:
    esp32 = serial.Serial("COM4", 115200, timeout=1)
except:
    esp32 = None
    print("⚠️ ESP32 no conectado")

# --- Variables globales ---
expresion = ""
historial = []

# --- Paleta de colores ---
COLORES = {
    "fondo": "#2D3047",
    "display": "#634D70",
    "display_texto": "#FFFFFF",
    "boton_num": "#996998",
    "boton_op": "#FF9B42",
    "boton_esp": "#C04ABC",
    "boton_igual": "#FF6B6B",
    "texto_oscuro": "#1E1E24",
    "texto_claro": "#FFFFFF",
    "historial": "#ede3ed",
    "marco": "#7e5b84"
}

# --- Funciones de calculadora ---
def presionar(tecla):
    global expresion
    expresion += str(tecla)
    entrada_var.set(expresion)

def borrar_un_digito():
    global expresion
    expresion = expresion[:-1]
    entrada_var.set(expresion)

def limpiar():
    global expresion
    expresion = ""
    entrada_var.set("")

def calcular():
    global expresion
    try:
        expresion_eval = expresion.lstrip("0")
        if expresion_eval == "":
            expresion_eval = "0"

        resultado = eval(expresion_eval)
        resultado_int = int(round(resultado))

        # --- Manejo de límites ---
        if resultado_int < 0:
            resultado_int = 0
        elif resultado_int > 99:
            entrada_var.set("Error")
            historial.append((expresion_eval, "Error"))
            actualizar_historial()
            expresion = ""
            if esp32:
                esp32.write(b"DISPLAY:ERROR\n")
            return

        historial.append((expresion, resultado_int))
        actualizar_historial()

        expresion = str(resultado_int)
        entrada_var.set(expresion)

        if esp32:
            esp32.write(f"DISPLAY:{resultado_int}\n".encode())

    except Exception as e:
        print(f"Error en calculo: {e}")
        entrada_var.set("Error")
        expresion = ""
        if esp32:
            esp32.write(b"DISPLAY:ERROR\n")

def actualizar_historial():
    historial_text.config(state=tk.NORMAL)
    historial_text.delete("1.0", tk.END)
    for h in historial[-10:]:
        historial_text.insert(tk.END, f"{h[0]} = {h[1]}\n")
    historial_text.config(state=tk.DISABLED)

# --- Control ESP32 ---
# def enviar_comando(cmd):
#     if esp32:
#         esp32.write((cmd + "\n").encode())

# --- Control ESP32 ---
def enviar_comando(cmd):
    global expresion, historial
    if esp32:
        esp32.write((cmd + "\n").encode())
    # Si el comando es RESET, borrar la expresión y limpiar la GUI
    if cmd == "RESET":
        expresion = ""
        entrada_var.set("")  # limpia el display en pantalla
        historial.clear()    # vacía el historial
        actualizar_historial()

# --- Escuchar puerto serie ---
def escuchar_serial():
    global expresion
    while True:
        if esp32 and esp32.in_waiting > 0:
            try:
                linea = esp32.readline().decode(errors="ignore").strip()
                if not linea:
                    continue
                if linea.startswith("VALOR:"):
                    valor = linea.split(":")[1].strip()
                    historial.append(("contador", valor))
                    actualizar_historial()
                    expresion = valor
                    entrada_var.set(valor)
            except Exception as e:
                print(f"Error leyendo serial: {e}")

if esp32:
    hilo_serial = threading.Thread(target=escuchar_serial, daemon=True)
    hilo_serial.start()

# --- Interfaz gráfica ---
root = tk.Tk()
root.title("Calculadora con ESP32")
root.configure(bg=COLORES["fondo"])
root.geometry("800x600")

# Estilo de fuente
fuente_botones = ("Arial", 14, "bold")
fuente_display = ("Arial", 24, "bold")

# Frame principal
main_frame = tk.Frame(root, bg=COLORES["fondo"])
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Display
entrada_var = tk.StringVar()
display_frame = tk.Frame(main_frame, bg=COLORES["marco"], relief=tk.RAISED, bd=2)
display_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=10, sticky="we")

entrada = tk.Entry(display_frame, textvariable=entrada_var, font=fuente_display, 
                   justify="right", bg=COLORES["display"], fg=COLORES["display_texto"],
                   relief=tk.FLAT, bd=5)
entrada.pack(fill=tk.BOTH, padx=2, pady=2)

# Frame de botones
botones_frame = tk.Frame(main_frame, bg=COLORES["fondo"])
botones_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

botones = [
    ("7",1,0),("8",1,1),("9",1,2),("/",1,3),
    ("4",2,0),("5",2,1),("6",2,2),("*",2,3),
    ("1",3,0),("2",3,1),("3",3,2),("-",3,3),
    ("0",4,0),(".",4,1),("=",4,2),("+",4,3),
]

for (texto, fila, col) in botones:
    if texto == "=":
        color = COLORES["boton_igual"]
    elif texto in ["/", "*", "-", "+"]:
        color = COLORES["boton_op"]
    else:
        color = COLORES["boton_num"]
        
    b = tk.Button(botones_frame, text=texto, 
                  command=lambda t=texto: presionar(t) if t != "=" else calcular(),
                  bg=color, fg=COLORES["texto_claro"], font=fuente_botones, 
                  relief=tk.RAISED, bd=2, activebackground=color)
    b.grid(row=fila, column=col, ipadx=10, ipady=10, padx=3, pady=3, sticky="nsew")

# Botones especiales
tk.Button(botones_frame, text="C", command=limpiar, bg=COLORES["boton_esp"], 
          fg=COLORES["texto_claro"], font=fuente_botones, relief=tk.RAISED, bd=2).grid(
          row=5, column=0, columnspan=2, sticky="nsew", padx=3, pady=3)
tk.Button(botones_frame, text="⌫", command=borrar_un_digito, bg=COLORES["boton_esp"], 
          fg=COLORES["texto_claro"], font=fuente_botones, relief=tk.RAISED, bd=2).grid(
          row=5, column=2, sticky="nsew", padx=3, pady=3)
tk.Button(botones_frame, text="Hist", command=actualizar_historial, bg=COLORES["boton_esp"], 
          fg=COLORES["texto_claro"], font=fuente_botones, relief=tk.RAISED, bd=2).grid(
          row=5, column=3, sticky="nsew", padx=3, pady=3)

# Historial
historial_frame = tk.LabelFrame(main_frame, text="Historial", bg=COLORES["fondo"], 
                                fg=COLORES["texto_claro"], font=("Arial", 12, "bold"))
historial_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

historial_text = tk.Text(historial_frame, height=10, width=30, bg=COLORES["historial"],
                         relief=tk.FLAT, bd=2, font=("Consolas", 15))
historial_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
historial_text.config(state=tk.DISABLED)

# Botones de control ESP32
frame_control = tk.LabelFrame(main_frame, text="Control ESP32", bg=COLORES["fondo"], 
                              fg=COLORES["texto_claro"], font=("Arial", 12, "bold"))
frame_control.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="we")

botones_control = [
    ("Iniciar ↑", "STARTUP", 0),
    ("Iniciar ↓", "STARTDOWN", 1),
    ("Paro", "STOP", 2),
    ("Reset", "RESET", 3)
]

for texto, cmd, col in botones_control:
    tk.Button(frame_control, text=texto, command=lambda c=cmd: enviar_comando(c), 
              bg=COLORES["boton_esp"], fg=COLORES["texto_claro"], 
              font=("Arial", 10, "bold"), relief=tk.RAISED, bd=2).grid(
              row=0, column=col, padx=5, pady=5, ipadx=5, ipady=3)

# Ajuste de filas y columnas
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

for i in range(6):
    botones_frame.grid_rowconfigure(i, weight=1)
for i in range(4):
    botones_frame.grid_columnconfigure(i, weight=1)

root.mainloop()
