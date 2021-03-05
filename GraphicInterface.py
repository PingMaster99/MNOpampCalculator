# encoding: utf-8
"""
    GraphicInterface.py

    Displays the op amp calculator

    Dario Marroquin 18269 (dariomarroquin)
    Pablo Ruiz 18259 (PingMaster99)

    Version 1.0
    Updated March 4, 2020
"""
from tkinter import *
from CalculationsModule import *
import matplotlib.pyplot as plt
import numpy as np

# Constants
TITLE_SIZE = 15


def calculate():
    """
    Performs the op amp calculator calculations
    """
    plt.clf()
    inverter = int(opa.get()) == 1
    point = vin.get()
    try:
        point = float(point)
    except ValueError:
        vin.delete(0, END)
        point = None

    # Needed data
    populate_calculations()
    function, result, real_value = calculate_opamp_function(point, inverter)
    spline_result, spline_print = calculate_opamp_spline(point)
    error = calculate_error(point, result, inverter)
    spline_error = calculate_error(point, spline_result, inverter)

    # Error comparison
    print("Error mínimo cuadrado:", error, "%\nError trazadores cúbicos: ", spline_error, "%\n\nTrazadores:\n",
          spline_print, "\n\n")

    if type(result) is not str:
        str(round(result, 4))

    if type(error) is not str:
        error = str(round(error, 4)) + " %"

    if function[0] > 0:
        a0 = "+ " + str(round(function[0], 4))
    elif function[0] < 0:
        a0 = "- " + str(round(function[0], 4))[1:]
    else:
        a0 = ""
    result_funcion["text"] = f"{round(function[1], 4)} * Vin {a0}"

    result_ev["text"] = result
    result_err["text"] = error

    x_1 = np.linspace(0, 20)
    y_1 = x_1 * real_value
    y_2 = x_1 * function[1] + function[0]

    # Results graph
    plt.plot(x_1, y_1, label="Teórico")
    plt.plot(x_1, y_2, label="Experimental")
    plt.legend()
    plt.title("Función teórica y experimental")
    plt.xlabel("Vin")
    plt.ylabel("Vout")
    plt.show()


"""
    GUI window with grid layout
"""
window = Tk()
window.columnconfigure(0, minsize=100)
window.columnconfigure(1, minsize=100)
window.columnconfigure(2, minsize=100)
window.columnconfigure(3, minsize=100)
window.columnconfigure(4, minsize=100)
window.columnconfigure(5, minsize=100)
window.columnconfigure(6, minsize=100)
window.columnconfigure(7, minsize=50)

window.rowconfigure(0, minsize=30)
window.rowconfigure(1, minsize=30)
window.rowconfigure(2, minsize=30)
window.rowconfigure(3, minsize=30)
window.rowconfigure(4, minsize=30)
window.rowconfigure(5, minsize=30)
window.rowconfigure(6, minsize=30)
window.rowconfigure(7, minsize=30)

"""
    Titles 
"""
title = Label(window, text="Calculadora de Op amps", bg="#595358", fg="white")
title.config(font=("Arial", 20))
title.grid(column=0, row=0, columnspan=8, sticky="we")

"""
    Input 
"""
vin = Entry(window, font="Arial 20")
vin.grid(row=1, column=4)
vin_title = Label(window, text="Vin", bg="#3891A6", fg="BLACK")
vin_title.config(font=("Arial", TITLE_SIZE))
vin_title.grid(row=1, column=3)

"""
    RadioButton 
"""


opa = StringVar(window, True)

# Dictionary to create multiple buttons
radio = {"Opamp Amplificador Inversor": True,
         "Opamp Amplificador no inversor": False,
         }
# Loop is used to create multiple Radiobuttons
# rather than creating each button separately
for (text, value) in radio.items():
    Radiobutton(window, text=text, variable=opa, value=value).grid(columnspan=2, pady=(1, 0))

"""
    Buttons
"""
calculate_button = Button(window, text="Calcular", padx=20, pady=10, command=calculate, bg="#99c24d")
calculate_button.config(font=("Arial", 15))
calculate_button.grid(row=2, column=6)

"""
    Results
"""
result_funcion = Label(window)
result_funcion.grid(row=2, column=4)
rsf_title = Label(window, text="Función", bg="#3891A6", fg="BLACK")
rsf_title.config(font=("Arial", TITLE_SIZE))
rsf_title.grid(row=2, column=3)

result_ev = Label(window)
result_ev.grid(row=3, column=4)
rsev_title = Label(window, text="Vout", bg="#3891A6", fg="BLACK")
rsev_title.config(font=("Arial", TITLE_SIZE))
rsev_title.grid(row=3, column=3)

result_err = Label(window)
result_err.grid(row=4, column=4)
rserr_title = Label(window, text="Error (%)", bg="#3891A6", fg="BLACK")
rserr_title.config(font=("Arial", TITLE_SIZE))
rserr_title.grid(row=4, column=3)

"""
    Circuit picture
"""

photo = PhotoImage(file=r"./OPAMPS.png")
image = Button(window, image=photo, padx=0, pady=0)
image.config(height=200, width=500)
image.grid(row=6, column=1, columnspan=5, pady=(0, 20))

"""
    Window display
"""
window.geometry("980x500")
window.config(bg="#B2CEDE")
window.mainloop()
