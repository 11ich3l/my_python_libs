from my_strings.my_string import number_to_scistr, scistr_to_number, which_pow
from sympy import symbols, diff, evalf, simplify
from math import sqrt
from collections import OrderedDict
from components_series import series

# Définition d'une grandeur scientifique par:
#   - sa valeur
#   - sa tolérance
#   - son expression en fonction d'autres paramètre
#   - son unité
sym_values = dict()
class scival():
    def __init__(self, value, tol="0%", unit:str="", *args, **kwargs):
        self.value = value
        self.unit = unit
        self.tol_calc(tol)
        self.tol_abs_range = [self.tol_abs_m, self.tol_abs_p]
        self.tol_abs = self.tol_abs_p - self.tol_abs_m
        self.rtol = ((max(self.tol_abs_range) - min(self.tol_abs_range)) / self.value) / 2
        self.tol_center = (max(self.tol_abs_range) - min(self.tol_abs_range)) / 2 + min(self.tol_abs_range)

        if "qtol" in kwargs:
            self.qtol = kwargs["qtol"]
        else:
            self.qtol = 0

        if "mmtol" in kwargs:
            self.mmtol = kwargs["mmtol"]
        else:
            self.mmtol = 0

        if "sym_name" in kwargs:
            self.sym_name = kwargs["sym_name"]
        else:
            self.sym_name = None

        if "sym_expr" in kwargs:
            self.sym_expr = kwargs["sym_expr"]
        else:
            self.sym_expr = None

        if "sym_diff_expr" in kwargs:
            self.sym_diff_expr = kwargs["sym_diff_expr"]
        else:
            self.sym_diff_expr = [[],[]]

        if "sym_diff_expr_tol" in kwargs:
            self.sym_diff_expr_tol = kwargs["sym_diff_expr_tol"]
        else:
            self.sym_diff_expr_tol = []

        if self.sym_name!=None:
            self.sym_val = symbols(self.sym_name)
            self.sym_expr = [self.sym_val,[self.sym_val]]
            sym_values[str(self.sym_val)]={"value":self.value,
                                           "unit":self.unit,
                                           "tol_abs":self.tol_abs}
        elif self.sym_expr == None:
            self.sym_val = symbols("p"+str(len(sym_values)+1))
            self.sym_expr = [self.sym_val, [self.sym_val]]
            sym_values[str(self.sym_val)] = {"value": self.value,
                                             "unit": self.unit,
                                             "tol_abs": self.tol_abs}
        elif self.sym_expr != None:
            self.sym_val = self.sym_expr[1]

    def __str__(self):
        val_scistr = number_to_scistr(self.value)
        print_val = f"{val_scistr['str']}"
        t_abs_m_scistr = number_to_scistr(self.tol_abs_m)
        val_min = f"{t_abs_m_scistr['str']}"
        t_abs_p_scistr = number_to_scistr(self.tol_abs_p)
        val_max = f"{t_abs_p_scistr['str']}"
        stand_dev_m = number_to_scistr(self.value*(1-self.qtol))
        stand_dev_m = f"{stand_dev_m['str']}"
        stand_dev_p = number_to_scistr(self.value*(1+self.qtol))
        stand_dev_p = f"{stand_dev_p['str']}"
        return f"{print_val}{self.unit}; " \
               f"relative tolerance: [{val_min};{val_max}]"\
               f"\u00B1{round(100*self.rtol, 1)}%; " \
               f"standard deviation: [{stand_dev_m};{stand_dev_p}]" \
               f"\u00B1{round(100 * self.qtol, 1)}%"

    def __add__(self, other):
        value = self.value + other.value
        sym_expr = [self.sym_expr[0]+other.sym_expr[0],
                    list(set(self.sym_expr[1]+other.sym_expr[1]))]
        tol, qtol, sym_diff_expr, sym_diff_expr_tol = self.sym_tol_calc(sym_expr, other, value)
        mmtol = ((max(self.tol_abs_range) + max(other.tol_abs_range))
               - (min(self.tol_abs_range) + min((other.tol_abs_range))))\
              /value/2
        unit = find_usi_unit(self, other, "+")
        if unit == "Ohm":
            return resistor(value,
                          tol=tol,
                          sym_expr=sym_expr,
                          qtol=qtol,
                          mmtol=mmtol,
                          sym_diff_expr=sym_diff_expr,
                          sym_diff_expr_tol=sym_diff_expr_tol,
                          unit = unit)
        if unit == "F":
            return capacitor(value,
                          tol=tol,
                          sym_expr=sym_expr,
                          qtol=qtol,
                          mmtol=mmtol,
                          sym_diff_expr=sym_diff_expr,
                          sym_diff_expr_tol=sym_diff_expr_tol,
                          unit = unit)
        if unit == "H":
            return inductor(value,
                          tol=tol,
                          sym_expr=sym_expr,
                          qtol=qtol,
                          mmtol=mmtol,
                          sym_diff_expr=sym_diff_expr,
                          sym_diff_expr_tol=sym_diff_expr_tol,
                          unit = unit)
        else:
            return scival(value,
                          tol=tol,
                          sym_expr=sym_expr,
                          qtol=qtol,
                          mmtol=mmtol,
                          sym_diff_expr=sym_diff_expr,
                          sym_diff_expr_tol=sym_diff_expr_tol,
                          unit = unit)

    def __sub__(self, other):
        value = self.value - other.value
        sym_expr = [self.sym_expr[0]-other.sym_expr[0],
                    list(set(self.sym_expr[1]+other.sym_expr[1]))]
        tol, qtol, sym_diff_expr, sym_diff_expr_tol = self.sym_tol_calc(sym_expr, other, value)
        mmtol = abs(((max(self.tol_abs_range) - min(other.tol_abs_range))
               - (min(self.tol_abs_range) - max((other.tol_abs_range))))\
              /value/2)
        unit = find_usi_unit(self, other, "-")
        if unit == "Ohm":
            return resistor(value,
                            tol=tol,
                            sym_expr=sym_expr,
                            qtol=qtol,
                            mmtol=mmtol,
                            sym_diff_expr=sym_diff_expr,
                            sym_diff_expr_tol=sym_diff_expr_tol,
                            unit=unit)
        if unit == "F":
            return capacitor(value,
                             tol=tol,
                             sym_expr=sym_expr,
                             qtol=qtol,
                             mmtol=mmtol,
                             sym_diff_expr=sym_diff_expr,
                             sym_diff_expr_tol=sym_diff_expr_tol,
                             unit=unit)
        if unit == "H":
            return inductor(value,
                            tol=tol,
                            sym_expr=sym_expr,
                            qtol=qtol,
                            mmtol=mmtol,
                            sym_diff_expr=sym_diff_expr,
                            sym_diff_expr_tol=sym_diff_expr_tol,
                            unit=unit)
        else:
            return scival(value,
                          tol=tol,
                          sym_expr=sym_expr,
                          qtol=qtol,
                          mmtol=mmtol,
                          sym_diff_expr=sym_diff_expr,
                          sym_diff_expr_tol=sym_diff_expr_tol,
                          unit=unit)

    def __mul__(self, other):
        value = self.value * other.value
        sym_expr = [self.sym_expr[0] * other.sym_expr[0],
                    list(set(self.sym_expr[1]+other.sym_expr[1]))]
        tol, qtol, sym_diff_expr, sym_diff_expr_tol = self.sym_tol_calc(sym_expr, other, value)
        mmtol = ((self.tol_abs_p * other.tol_abs_p)\
                    -(self.tol_abs_m * other.tol_abs_m))\
                /value/2
        unit = find_usi_unit(self, other, "*")
        if unit == "Ohm":
            return resistor(value,
                            tol=tol,
                            sym_expr=sym_expr,
                            qtol=qtol,
                            mmtol=mmtol,
                            sym_diff_expr=sym_diff_expr,
                            sym_diff_expr_tol=sym_diff_expr_tol,
                            unit=unit)
        if unit == "F":
            return capacitor(value,
                             tol=tol,
                             sym_expr=sym_expr,
                             qtol=qtol,
                             mmtol=mmtol,
                             sym_diff_expr=sym_diff_expr,
                             sym_diff_expr_tol=sym_diff_expr_tol,
                             unit=unit)
        if unit == "H":
            return inductor(value,
                            tol=tol,
                            sym_expr=sym_expr,
                            qtol=qtol,
                            mmtol=mmtol,
                            sym_diff_expr=sym_diff_expr,
                            sym_diff_expr_tol=sym_diff_expr_tol,
                            unit=unit)
        else:
            return scival(value,
                          tol=tol,
                          sym_expr=sym_expr,
                          qtol=qtol,
                          mmtol=mmtol,
                          sym_diff_expr=sym_diff_expr,
                          sym_diff_expr_tol=sym_diff_expr_tol,
                          unit=unit)

    def __truediv__(self, other):
        value = self.value / other.value
        sym_expr = [self.sym_expr[0] / other.sym_expr[0],
                    list(set(self.sym_expr[1]+other.sym_expr[1]))]
        mmtol = ((self.tol_abs_p / other.tol_abs_m) \
                 - (self.tol_abs_m / other.tol_abs_p)) \
                / value / 2
        tol, qtol, sym_diff_expr, sym_diff_expr_tol = self.sym_tol_calc(sym_expr, other, value)
        unit = find_usi_unit(self, other, "/")
        if unit == "Ohm":
            return resistor(value,
                            tol=tol,
                            sym_expr=sym_expr,
                            qtol=qtol,
                            mmtol=mmtol,
                            sym_diff_expr=sym_diff_expr,
                            sym_diff_expr_tol=sym_diff_expr_tol,
                            unit=unit)
        if unit == "F":
            return capacitor(value,
                             tol=tol,
                             sym_expr=sym_expr,
                             qtol=qtol,
                             mmtol=mmtol,
                             sym_diff_expr=sym_diff_expr,
                             sym_diff_expr_tol=sym_diff_expr_tol,
                             unit=unit)
        if unit == "H":
            return inductor(value,
                            tol=tol,
                            sym_expr=sym_expr,
                            qtol=qtol,
                            mmtol=mmtol,
                            sym_diff_expr=sym_diff_expr,
                            sym_diff_expr_tol=sym_diff_expr_tol,
                            unit=unit)
        else:
            return scival(value,
                          tol=tol,
                          sym_expr=sym_expr,
                          qtol=qtol,
                          mmtol=mmtol,
                          sym_diff_expr=sym_diff_expr,
                          sym_diff_expr_tol=sym_diff_expr_tol,
                          unit=unit)

    def sym_tol_calc(self, sym_expr, other, value):
        sym_diff_expr = [[simplify(diff(sym_expr[0],x)),x] for x in sym_expr[1]]
        tol_abs_range = [abs(x[0]*sym_values[str(x[1])]["tol_abs"]) for x in sym_diff_expr]
        qtol_abs_range = [abs(x[0] * sym_values[str(x[1])]["tol_abs"])**2 for x in sym_diff_expr]
        param = {x:sym_values[str(x)]["value"] for x in sym_expr[1]}
        sym_diff_expr_tol  = [diff_x[0].evalf(subs=param) for diff_x in sym_diff_expr]
        tol_abs_range = float(sum(tol_abs_range).evalf(subs=param))
        qtol_abs_range = sqrt(float(sum(qtol_abs_range).evalf(subs=param)))
        tol = (tol_abs_range/value/2)
        qtol = (qtol_abs_range / value / 2)
        # tol = (((max(self.tol_abs_range) - min(self.tol_abs_range)) / self.value)
        #        + (max(other.tol_abs_range) - min(other.tol_abs_range)) / other.value) / 2
        return tol, qtol, sym_diff_expr, sym_diff_expr_tol

    def tol_calc(self,tol):
        tol_type = type(tol)
        if tol_type == list and len(tol) == 2:
            if (type(tol[0]) == float or type(tol[0]) == int) and (type(tol[1]) == int or type(tol[1]) == float):
                self.tol_abs_p  = max(tol)
                self.tol_abs_m  = min(tol)
            if (type(tol[0]) == str and type(tol[1]) == str):
                    if "%" in tol[0] and "%" in tol[1]:
                        if "-" in tol[0]:
                            min_tol = float(tol[0][1:-1])/100
                            self.tol_abs_m = (self.value *(1 - min_tol))
                        elif "+" in tol[0]:
                            max_tol = float(tol[0][1:-1])/100
                            self.tol_abs_p = (self.value *(1 + max_tol))
                        if "-" in tol[1]:
                            min_tol = float(tol[1][1:-1])/100
                            self.tol_abs_m = (self.value * (1 - min_tol))
                        elif "+" in tol[1]:
                            max_tol = float(tol[1][1:-1])/100
                            self.tol_abs_p = (self.value * (1 + max_tol))

        if tol_type == float:
            self.tol_abs_p = self.value*(1+tol)
            self.tol_abs_m = self.value*(1-tol)

        if tol_type == str:
            if "%" in tol:
                tol = float(tol[:-1])/100
                self.tol_calc(tol)

class voltage(scival):
    def __init__(self, value, tol="0%", unit:str="V",*args,**kwargs):
        scival.__init__(self, value, tol=tol, unit=unit,*args,**kwargs)

    def __add__(self, other):
        v_add = scival.__add__(self, other)
        return v_add

    def __sub__(self, other):
        v_sub = scival.__sub__(self, other)
        return v_sub
    #
    def __mul__(self, other):
        v_mul = scival.__mul__(self, other)
        return v_mul

    def __truediv__(self, other):
        v_div = scival.__truediv__(self, other)
        return v_div

class current(scival):
    def __init__(self, value, tol="0%", unit:str="A",*args,**kwargs):
        scival.__init__(self, value, tol=tol, unit=unit,*args,**kwargs)

    def __add__(self, other):
        i_add = scival.__add__(self, other)
        return i_add

    def __sub__(self, other):
        i_sub = scival.__sub__(self, other)
        return i_sub
    #
    def __mul__(self, other):
        i_mul = scival.__mul__(self, other)
        return i_mul

    def __truediv__(self, other):
        i_div = scival.__truediv__(self, other)
        return i_div

class resistor(scival):
    def __init__(self, value, tol="0%", unit:str="Ohm",*args,**kwargs):
        scival.__init__(self, value, tol=tol, unit=unit,*args,**kwargs)
        self.serie_value = self.find_nearest_resistor(self.value)

    def __add__(self, other):
        r_add = scival.__add__(self, other)
        return r_add

    def __sub__(self, other):
        r_sub = scival.__sub__(self, other)
        return r_sub
    #
    def __mul__(self, other):
        r_mul = scival.__mul__(self, other)
        return r_mul

    def __truediv__(self, other):
        r_div = scival.__truediv__(self, other)
        return r_div

    def find_nearest_resistor(self,value):
        closest_value = find_nearest_in_series(value)
        return closest_value

class capacitor(scival):
    def __init__(self, value, tol="0%", unit:str="Ohm",*args,**kwargs):
        scival.__init__(self, value, tol=tol, unit=unit,*args,**kwargs)
        self.serie_value = self.find_nearest_capacitor(self.value)

    def __add__(self, other):
        c_add = scival.__add__(self, other)
        return c_add

    def __sub__(self, other):
        c_sub = scival.__sub__(self, other)
        return c_sub
    #
    def __mul__(self, other):
        c_mul = scival.__mul__(self, other)
        return c_mul

    def __truediv__(self, other):
        c_div = scival.__truediv__(self, other)
        return c_div

    def find_nearest_capacitor(self,value):
        closest_value = find_nearest_in_series(value)
        return closest_value

class inductor(scival):
    def __init__(self, value, tol="0%", unit:str="Ohm",*args,**kwargs):
        scival.__init__(self, value, tol=tol, unit=unit,*args,**kwargs)
        self.serie_value = self.find_nearest_inductor(self.value)

    def __add__(self, other):
        l_add = scival.__add__(self, other)
        return l_add

    def __sub__(self, other):
        l_sub = scival.__sub__(self, other)
        return l_sub
    #
    def __mul__(self, other):
        l_mul = scival.__mul__(self, other)
        return l_mul

    def __truediv__(self, other):
        l_div = scival.__truediv__(self, other)
        return l_div

    def find_nearest_inductor(self,value):
        closest_value = find_nearest_in_series(value)
        return closest_value

def find_nearest_in_series(value):
    closest_value = OrderedDict()
    # récupération de la valeur au format "value""préfix usi"
    #   avec (0<value<1000)
    value = number_to_scistr(value)
    value = value['value']
    # passage à 0<value<10
    value = value / 10 ** (which_pow(value, 10) - 1)
    for serie_name, serie in series.items():
        closest_value[serie_name] = [min(serie, key=lambda x: abs(x - value))]
        closest_value[serie_name].append(abs(closest_value[serie_name][0] - value))
    return closest_value

def find_usi_unit(sci_object1,sci_object2,operation:str):
    # Dictionnaire associant les opérations à leurs unités SI correspondantes
    operation_units = {
        '+': {
            ('Ohm', 'Ohm'): 'Ohm',
            ('V', 'V'): 'V',
            ('A', 'A'): 'A',
            ('W', 'W'): 'W',
            # Ajoutez d'autres correspondances pour les opérations ici
        },
        '-': {
            ('Ohm', 'Ohm'): 'Ohm',
            ('V', 'V'): 'V',
            ('A', 'A'): 'A',
            ('W', 'W'): 'W',
            # Ajoutez d'autres correspondances pour les opérations ici
        },
        '*': {
            ('Ohm', ''): f"Ohm",
            ('V', ''): f"V",
            ('A', ''): f"A",
            ('F', ''): f"F",
            ('H', ''): f"H",
            ('Ohm', 'Ohm'): f"Ohm\u00B2",
            ('A', 'A'): f"A\u00B2",
            ('V', 'V'): f"V\u00B2",
            ('F', 'F'): f"F\u00B2",
            ('H', 'H'): f"H\u00B2",
            ('Ohm', 'A'): 'V',
            ('V', 'A'): 'W',
            ('W', 'Ohm'): f"V\u00B2",
            ('R', 'F'): f"s",
            ('H', 'F'): f"s\u00B2",
            # Ajoutez d'autres correspondances pour les opérations ici
        },
        '/': {
            ('Ohm', ''): f"Ohm",
            ('V', ''): f"V",
            ('A', ''): f"A",
            ('F', ''): f"F",
            ('H', ''): f"H",
            (f"Ohm\u00B2", 'Ohm'): f"Ohm",
            (f"A\u00B2", 'A'): f"A",
            (f"V\u00B2", 'V'): f"V",
            (f"F\u00B2", 'F'): f"F",
            (f"H\u00B2", 'H'): f"H",
            ('V', 'Ohm'): 'A',
            ('V', 'A'): 'Ohm',
            ('W', 'Ohm'): f"A\u00B2",
            ('W', 'V'): f"A",
            ('W', 'A'): f"V",
            ('H', 'R'): f"V",
            # Ajoutez d'autres correspondances pour les opérations ici
        },
        # Ajoutez d'autres opérations et leurs correspondances ici
    }

    # Vérifier si l'opération existe dans le dictionnaire
    if operation in operation_units:
        unit = operation_units[operation].get((sci_object1.unit, sci_object2.unit))
        if unit:
            return unit
        else:
            # Vérifier l'autre combinaison d'unités
            unit = operation_units[operation].get((sci_object1.unit, sci_object2.unit))
            if unit:
                return unit
            else:
                return ""
    else:
        return ""