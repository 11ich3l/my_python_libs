from collections import OrderedDict
import re

# fonction prenant en argument une chaine de caractère
#   au format binaire ou héxadecimal
# Et renvoie la valeur entière correspondate
def formstr_to_int(value:str):
    try:
        bin_val = re.findall('([01]+)', value)
    except:
        int_val = None
    else:
        if len(bin_val) == 1:
            int_val = int(bin_val[0],2)
            return int_val
        else:
            int_val = None
    try:
        hexa_val = re.findall('([0-9A-Fa-f]+)', value)
    except:
        int_val = None
    else:
        if len(hexa_val) == 1:
            int_val = int(hexa_val[0],16)
            return int_val
        else:
            int_val = None
    return int_val

# fonction prenant comme argument une valeur entière, un format
#   et en paramètre optionnel une taille
# Le retour est une chaine de caractère formattée au format
#   en paramètre
# Si le paramètre optionnel de lognueur de chaine est renseigné,
#   il est comparé à la valeur minimale recquise pour représenter
#   l'entier en paramètre et appliqué uniquement s'il est supérieur
def int_to_formstr(integer_value:int, format:str, length=None):
    if type(integer_value) == int:
            if format == 'bin':
                str_size = which_pow(integer_value,2)
                format = 'b'
            elif format == 'hex':
                str_size = which_pow(integer_value, 16)
                format = 'X'
            if length !=None and length >= str_size:
                str_size = length
            formatting = '{:0' + str(str_size) + str(format) + '}'
            format_string = ''.join(formatting.format(integer_value))
            return format_string
    else:
        return None

# fonction prenant en argumant une valeur entière
#   et vérifiant la puissance du paramètre base
#   nécessaire pour contenir la valeur entière
def which_pow(value:int,base):
    pow = 0
    while base**pow < value:
        pow += 1
    return pow



# fonction de récupération d'une donnée à une position dans une chaine de caractère
#   permettant de renvoyer la valeur de cette donnée au format qui convient binaire hexa entier
def get_inside_val(str_bin_value, pos1, pos2, format=None):
    # str_bin_value = str_bin_value[2:len(str_bin_value) - 1]
    raw_val = str_bin_value[pos1:pos2 + 1]
    if format=='bin':
        val = raw_val
    elif format == 'hex':
        val = hex(int(raw_val, 2))
    elif format == 'int':
        val = str(int(raw_val, 2))
    elif format == None:
        val = int(raw_val,2)
    return val

# fonction de dissection d'une chaine de caractère hexadécimale
#   en un dictionnaire en champs de bit nommés
# Les arguments de la fonction sont :
#   -   une chaine de caractère au format binaire
#   -   un dictionnaire contenant du nom du bit ou champs de bit comme clé et
#       la position ou les positions ( de début et de fin ) dans le champs de bit
# Le retour est un dictionnaire dont les clés sont identiques à celles
#   du dictonnaire passé en paramètre et dont les valeurs sont les valeurs
#   entière correspondantes à la conversion entière de bits de la chaine de caractère en paramètre
#   compris entre les positions ou à la position fournie(s) en tant que valeur
#   du dictionnaire en paramètre
def strbin_dissector(bit_sequence:str,dict):
    values = OrderedDict()
    for item in dict:
        pos = dict[item]
        try:
            if type(pos) == int:
                val = bit_sequence[pos]
            elif type(pos) == list:
                val = get_inside_val(bit_sequence, pos[0], pos[1], format='int')
            values[item] = val
        except Exception as ex:
            print(f"Exception: {ex}")
            val = None
    return values

# fonction de conversion des
#  chaines de caractères contenant un caractère de multiple litéral (k pour kilo, M pour méga)
#  en nombre flottant
def scistr_to_number(str_number):
    if type(str_number) != int or type(str_number) != float:
        num = re.findall('\d+', str_number)
        # print(len(num))
        if len(num) > 0:
            num = num[0]
        else:
            num = 1
        # str = re.findall('\w+', number)
        mult = re.findall('[GkKMmun]+', str_number)
        if len(mult) == 1:
            mult = mult[0]
            if mult == 'G':
                mult = 1e9
            elif mult == 'M':
                mult = 1e6
            if mult in ['k', 'K']:
                mult = 1e3
            elif mult == 'm':
                mult = 1/1e3
            elif mult == 'u':
                mult = 1/1e6
            elif mult == 'n':
                mult = 1/1e9
            num_str = float(num) * float(mult)
        elif len(mult) > 1:
            pass
        else:
            mult = 1
            num_str = float(num) * float(mult)

    return num_str

def number_to_scistr(number, prec:int=3):
    if number >= 1:
        if number // 1e9 != 0:
            str_number = {"value":round(number / 1e9, prec),"usi_pref":"G"}
        elif number // 1e6 != 0:
            str_number = {"value":round(number / 1e6, prec),"usi_pref":"M"}
        elif number // 1e3 != 0:
            str_number = {"value":round(number / 1e3, prec),"usi_pref":"k"}
        else:
            str_number = {"value":round(number, prec),"usi_pref":""}
    elif number < 1:
        if number * 1e3 > 1:
            str_number = {"value":round(number * 1e3, prec),"usi_pref":"m"}
        elif number * 1e6 > 1:
            str_number = {"value":round(number * 1e3, prec),"usi_pref":"u"}
        elif number * 1e9 > 1:
            str_number = {"value":round(number * 1e3, prec),"usi_pref":"n"}
        elif number * 1e12 > 1:
            str_number = {"value":round(number * 1e3, prec),"usi_pref":"p"}
        elif number * 1e16 > 1:
            str_number = {"value":round(number * 1e3, prec),"usi_pref":"f"}
    str_number["str"] = f"{str_number['value']}{str_number['usi_pref']}"
    return str_number