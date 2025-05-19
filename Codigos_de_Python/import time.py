import serial
import time
import threading
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

# Configuración del puerto serial (ajustar 'COMx' según el sistema operativo)
arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=1)  # Ajusta el puerto según tu configuración

# Tiempo de espera para establecer conexión
time.sleep(2)

setpoint = 25  # Setpoint inicial
actual_temperature = 25  # Temperatura inicial
temperatures = []  # Lista para almacenar valores de temperatura

# Función para enviar el setpoint al Arduino y asegurarse de que se procese inmediatamente
def actualizar_setpoint():
    global setpoint
    try:
        setpoint = int(entrada_setpoint.get())
        if 35 <= setpoint <= 55:
            arduino.write(f"S{setpoint}\n".encode())
            print(f"Setpoint enviado: {setpoint}")
            # Limpiar el buffer de entrada para evitar retrasos
            while arduino.in_waiting > 0:
                arduino.readline()
        else:
            print("Setpoint fuera de rango (35-55°C)")
    except ValueError:
        print("Error: Ingrese un número válido")

# Crear la ventana de Tkinter
root = tk.Tk()
root.title("Control PID de Temperatura")
root.geometry("1000x700")

# Etiqueta y campo de entrada para el setpoint
tk.Label(root, text="Setpoint (35-55°C):").pack(pady=5)
entrada_setpoint = tk.Entry(root)
entrada_setpoint.insert(0, "25")  # Valor por defecto
entrada_setpoint.pack(pady=5)

boton_actualizar = tk.Button(root, text="Actualizar Setpoint", command=actualizar_setpoint)
boton_actualizar.pack(pady=10)

# Etiqueta para mostrar la temperatura actual
label_temp = tk.Label(root, text="Temperatura Actual: 0°C", font=("Arial", 14), fg="red")
label_temp.pack(pady=10)

# Crear figura de Matplotlib
fig, ax = plt.subplots(figsize=(7, 5))
ax.set_ylim(0, 70)
ax.set_title("Evolución de la Temperatura")
ax.set_ylabel("Temperatura (°C)")
ax.set_xlabel("Tiempo (s)")
line, = ax.plot([], [], 'r-', label="Temperatura")
ax.legend()

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

def actualizar_grafica(i):
    if len(temperatures) > 50:
        temperatures.pop(0)  # Limitar la cantidad de datos en la gráfica
    line.set_data(range(len(temperatures)), temperatures)
    ax.relim()
    ax.autoscale_view()
    canvas.draw()

ani = animation.FuncAnimation(fig, actualizar_grafica, interval=500)

# Función para actualizar la temperatura en la interfaz
def actualizar_temperatura():
    global actual_temperature
    try:
        if arduino.in_waiting > 0:
            actual_temperature = arduino.readline().decode('utf-8').strip()
            label_temp.config(text=f"Temperatura Actual: {actual_temperature}°C")
            temperatures.append(float(actual_temperature))
    except Exception as e:
        print(f"Error en la lectura serial: {e}")
    root.after(500, actualizar_temperatura)  # Repetir cada 500 ms

# Inicia la actualización de temperatura
actualizar_temperatura()

# Ejecutar la interfaz Tkinter
root.mainloop()

# Cierra el puerto serial al cerrar la aplicación
arduino.close()
print("Conexión cerrada.")
