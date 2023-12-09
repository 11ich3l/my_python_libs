from my_strings.my_string import *
from my_science import *
from collections import OrderedDict
from sympy import diff, simplify, factor
from matplotlib import pyplot

bin_string = '00011000111'
integer = formstr_to_int(bin_string)
print("bin string to integer")
print(str(bin_string) + " | " + str(integer))
print("")

hexa_string = 'ABCD'
integer = formstr_to_int(hexa_string)
print("hexa string to integer")
print(str(hexa_string) + " | " + str(integer))
print("")

integer = 102
format_str1 = int_to_formstr(integer, 'bin')
print("integer to binary string")
print(str(integer) + " | " + str(format_str1) + " | " + str(bin(integer)))
format_str2 = int_to_formstr(integer, 'hex')
print("integer to hexa string")
print(str(integer) + " | " + str(format_str2) + " | " + str(hex(integer)))
format_str3 = int_to_formstr(integer, 'hex',length=8)
print("integer to hexa string")
print(str(integer) + " | " + str(format_str3) + " | " + str(hex(integer)))

val_desc = OrderedDict([
      ('defaut_sel_demi_charg', 0)
    , ('defaut_sel_vt_pc', 1)
    , ('defaut_sel_vt_pf', 2)
    , ('defaut_tempo_vt_pc', 3)
    , ('defaut_tempo_vt_pf', 4)
    , ('defaut_tempo_invent', 5)
    , ('defaut_courant_inv', [30,50])
])

bin_string = '00011000111'
bin_string=bin_string[::-1]
dissect_val = strbin_dissector(val_desc, bin_string)
print(bin_string)
for key in dissect_val:
    print(str(key) + ': ' + str(dissect_val[key]))


R1 = resistor(value=2,tol="5%",sym_name="R1")
print(R1)
R2 = resistor(value=1,tol="1%",sym_name="R2")

R_serie = R1 + R2
R_prod = R1*R2
R_div = R1/R2
R_par = (R1*R2)/(R1+R2)

U1 = voltage(5,[4.9,5.1],sym_name="U1")
Uint = U1*R1
G = R1/(R1+R2)
U2 = U1*(R1/(R1+R2))
print(U2)

R = resistor(value=1800,tol="5%",sym_name="R")
Vcc = voltage(value=5,tol="5%",sym_name="Vcc")
Udiode = voltage(value=0.6,tol=[0.4,0.8],sym_name="Ud")
Uopto = voltage(value=1.3,tol=[1,1.5],sym_name="Uo")
I = (Vcc-Udiode-Uopto)/(R)
print(I)
I_max = Vcc/R
print(I_max)

I = current(value=2e-3,tol="1%",sym_name="I")
Vcc = voltage(value=5,tol="5%",sym_name="Vcc")
Udiode = voltage(value=0.6,tol=[0.4,0.8],sym_name="Ud")
Uopto = voltage(value=1.3,tol=[1.2,1.4],sym_name="Uo")
R10 = (Vcc-Udiode-Uopto)/(I)
# Gain = (R1*R3)/((R1+R2+(R3*R4/(R3+R4)))*(R3+R4))

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import uniform

# Génération de valeurs aléatoires selon une distribution uniforme
data_uniform = uniform.rvs(size=1000)

# Tracer l'histogramme des données générées
plt.hist(data_uniform, bins=20, density=True, alpha=0.7, color='blue', edgecolor='black')

# Afficher le titre et les labels des axes
plt.title('Distribution uniforme')
plt.xlabel('Valeurs')
plt.ylabel('Fréquence')

from sympy import symbols, Piecewise
from sympy.plotting import plot

# Define the variable
x = symbols('x')

# Define a continuous function (e.g., a quadratic function)
continuous_function = x**2

# Define three different pieces of the function using Piecewise
piece2 = Piecewise((1, (x >= -1) & (x < 1)), (0, (x <= -1) | (x >= 1)))

piece = piece2 * continuous_function

# Plot all three pieces together
p = plot(piece, (x, -2,2),
         title='Function with Three Pieces',
         xlabel='x', ylabel='y', show=False)

# Show the plot
p.show()
plt.show()

print("OK")