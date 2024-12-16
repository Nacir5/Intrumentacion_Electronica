import time
import serial
import tkinter as tk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

def iniciar_proceso():
    """Función para iniciar la lectura de datos y animación."""
    altura = entrada_altura.get()
    
    try:
        # Validación de que la altura es un flotante
        altura_float = float(altura)
        if altura_float <= 0 or altura_float > 10:
            raise ValueError("Altura fuera de rango")
    except ValueError:
        messagebox.showerror("Entrada inválida", "Por favor ingrese un número flotante entre 0 y 10.")
        return
    
    # Enviar altura al ESP32
    ser.write(b'g\n')  # Comando para recibir datos
    ser.write(f"{altura_float}\n".encode('ascii'))  # Enviamos la altura como string codificada
    
    # Iniciar animación
    ani.event_source.start()

def enviar_panic():
    """Función para enviar el comando de emergencia 'stop' al ESP32."""
    ser.write(b'stop\n')
    messagebox.showwarning("Pánico activado", "Se envió el comando de emergencia 'stop' al ESP32.")

def animate(i, dataList, ser):
    """Función para animar la gráfica y actualizar el nivel del tanque."""
    ser.write(b'g\n')  # Comando para recibir datos
    try:
        # Leer y decodificar el dato recibido
        SP32Data_string = ser.readline().decode('ascii').strip()
        #print(f"{SP32Data_string}")  # Debug: Ver el dato recibido

        # Convertir a flotante
        SP32Data_float = float(SP32Data_string)
        dataList.append(SP32Data_float)
    except ValueError:
        #print(f": {SP32Data_string}")  # Debug: Imprimir error
        return  # Salir de la función si no se puede convertir

    dataList = dataList[-50:]  # Limitamos la lista a 50 elementos
    ax.clear()
    ax.plot(dataList)
    ax.set_ylim([0, 12])
    ax.set_title("Nivel de control")
    ax.set_ylabel("Altura del agua ")

    # Actualizar visualización del tanque
    tanque_canvas.delete("nivel")
    nivel_tanque = max(0, min(100, 100 - float(SP32Data_string) * 25))  # Escala de 0 a 100 (10 cm a 0)
    tanque_canvas.create_rectangle(50, nivel_tanque, 150, 100, fill="blue", tags="nivel")

# Configuración de la interfaz de Tkinter
root = tk.Tk()
root.title("Control de nivel con ESP32")

# Entrada de altura
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Ingrese altura (0 a 10 cm):").pack(side=tk.LEFT)
entrada_altura = tk.Entry(frame)
entrada_altura.pack(side=tk.LEFT)

btn_iniciar = tk.Button(frame, text="Iniciar", command=iniciar_proceso)
btn_iniciar.pack(side=tk.LEFT)

# Botón de pánico
btn_panic = tk.Button(root, text="Emergencia", command=enviar_panic, bg="red", fg="white")
btn_panic.pack(pady=10)

# Canvas para la visualización del tanque
tanque_canvas = tk.Canvas(root, width=200, height=120, bg="white")
tanque_canvas.pack(pady=10)
tanque_canvas.create_rectangle(50, 0, 150, 100, outline="black", width=2)

# Gráfica con matplotlib incrustada en Tkinter
fig = Figure(figsize=(5, 3), dpi=100)
ax = fig.add_subplot(111)

dataList = []

canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack()

# Configuración de comunicación serial
ser = serial.Serial("/dev/ttyACM0", 9600)
time.sleep(2)

# Animación
ani = animation.FuncAnimation(fig, animate, frames=100, fargs=(dataList, ser), interval=100)
ani.event_source.stop()  # Detenemos la animación hasta que se presione el botón

# Ejecutar la aplicación
root.mainloop()

# Cerrar comunicación serial al cerrar la aplicación
ser.close()
