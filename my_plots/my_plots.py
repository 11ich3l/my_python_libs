#TODO : reprendre les fonctions intéressantes et créé des fonction de base

# Librairie standards
import  csv
import  datetime
import  matplotlib.pyplot as plt
from    matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import  numpy as np
import  PySimpleGUI as sg
import  re
import  serial
import  time
import  threading
import  tkinter as Tk


# Librairies développées
import pySA

# Bibliothèque copiée depuis internet
import round_shapes as rs

# Paramètres initiaux
(X_WIND_MIN, Y_WIND_MIN) = (900, 900)
SZ_LABEL = 17
SZ_IN_TEXT = 10
DESC_FONT = 'normal 12 italic'
STAND_FONT = 'calibri 14 bold'
GRAPH_SIZE_X = 1000
GRAPH_SIZE_Y = 300
BKGN_FRAME_COL = '#243324'

UNITE = b'DBUV'
UNITE_FREQ = "Hz"
UNITE_TEMPS = " s"

F_START_INI = '10 kHz'
F_STOP_INI = '110 kHz'

F_CENTRALE_INI = '60 kHz'
F_SPAN_INI = '100 kHz'

RBW_INI = '10 Hz'
VBW_INI = '10 MHz'
SWT_INI = '10 s'

DEFAULT_FILE_TEXT = 'Specify a file to save acquired data in or import data from'

timeoutSerial = 0.05

sg.theme('Dark')
###########################################
# Classes
###########################################

# Barre d'outils du graphique de l'IHM
class Toolbar(NavigationToolbar2Tk):
    # only display the buttons we need
    # toolitems = [t for t in NavigationToolbar2Tk.toolitems if t[0] in ('Home', 'Pan', 'Zoom')] # t[0] in ('Home', 'Pan', 'Zoom','Save')]
    # display all buttons
    toolitems = [t for t in NavigationToolbar2Tk.toolitems]  # t[0] in ('Home', 'Pan', 'Zoom','Save')]

    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)

###########################################
# Fonctions
###########################################

# fonction de scan des ports de communication
#  trouve les ports ouverts et demande
#  l'identité de l'instrument
def thread_scan_port_com(ports, window):
    global port_scanning
    global instruments_liste
    global updt_instruments

    print('thread thread_scan_port_com running')
    while port_scanning == True:
        portsDispo = []
        echanges = []
        opened_ports = []
        opened_inst = []
        instrument = []
        portsIndispo = []
        j = 0
        # print('thread thread_scan_port_com running')
        if instruments_liste != []:
            for item in instruments_liste:
                if item[1].isOpen():
                    try:
                        com = pySA.echangeLS(port=item[1], data=b'*IDN?\n', log=True, display=True, echange=echanges, waitRep=True)
                        if com != []:
                            if len(com['reponse']) > 5:
                                opened_ports.append(item[1].name)
                                opened_inst.append(item)
                        else:
                            instruments_liste.remove(item)
                            updt_instruments = True
                    except Exception:
                        print('is open test ' +str (Exception))
                        instruments_liste.remove(item)
                        updt_instruments = True
                else:
                    pass

        for i in range(1, 256):
            try:
                ser = serial.Serial(port="COM" + str(i), timeout=timeoutSerial)
            except Exception:
                # print("Impossible d'ouvrir le port " + str(i))
                pass
            else:
                if ser.isOpen():
                    # print("Le port " + str(i) + " a bien été ouvert")
                    portsDispo.append(ser)
                    pass
                else:
                    print("Echec à l'ouverture du port " + str(i))
                    pass

        # for port in portsDispo:
        #     print(str(port))
        if portsDispo == [] and opened_ports == []:
            instruments_liste = []
            updt_instruments = True
        else:
            for port in portsDispo:
                try:
                    pySA.echangeLS(port=port, data=b'@REM\n', log=True, display=True, echange=echanges, waitRep=False)
                    time.sleep(0.1)
                    com = pySA.echangeLS(port=port, data=b'*IDN?\n', log=True, display=True, echange=echanges, waitRep=False)
                    if com != []:
                        if len(com['reponse']) > 5:
                            inst = re.findall('b\'(.*)\\\\r', str(com['reponse']))[0]
                            instrument = [inst, com['portSerie']]
                            if instrument not in instruments_liste:
                                instruments_liste.append([inst,com['portSerie']])
                                updt_instruments = True
                except Exception:
                    portsIndispo.append(port)
                    print(Exception)
                    print('ports dispo exception ' + str(Exception))

        if len(portsIndispo) > 0:
            for port in portsIndispo:
                for item in instruments_liste:
                    if port == item:
                        instruments_liste.remove(item)
                        updt_instruments = True
                port.close()

# fonction de mise à jour dans l'IHM
# de la liste des instruments disponibles
def updt_instruments_liste(existing_inst, window):
    # print("entering scan_port_com")
    inst_combo = []
    if existing_inst != []:
        if len(existing_inst[0]) > 0:
            for item in existing_inst:
                inst_combo.append(item[0])
            current_inst = window['InstList'].get()
            if current_inst in inst_combo:
                window['InstList'].update(values=inst_combo,value=current_inst)
            else:
                window['InstList'].update(values=inst_combo)
            # port_inst = existing_inst[0][1]
            # port_name = port_inst.name
            # window['ComPort'].update(port_name)
            # window['InstList'].update(value=inst[0][0])
    else:
        instrument = 'None'
        port_inst = ''
        port_name = ''
        window['ComPort'].update(port_name)
        window['InstList'].update(value=instrument)
        window['InstList'].update(values=instrument, value=instrument)

# fonction d'initialisation des paramètres
#  de l'analyseur de spectre
def spectrum_analyzer_set(port, rbw, vbw, swt, f_start, f_stop):
    if port != '':
        pySA.rs_fsp_init(port, rbw, vbw, swt, f_start, f_stop)
    else:
        pass

# fonction de récupération des paramètres
#  de l'analyseur de spectre
def spectrum_analyzer_get_conf(port):
    if port != '':
        conf = pySA.sa_get_conf(port)
    else:
        conf = ''
        pass
    return conf

# fonction de démarrage du balayage
#  fréquentiel sur l'analyseur de spectre
# avec les paramètres de l'IHM
def sweep_scan(port, swt):
    if port != '':
        pySA.sweep_scan(port, swt)
    else:
        pass

# fonction appelant le module pySA
#  afin de réaliser le balayage fréquentiel
#  passé en paramètre
def scan_freq(portFSP, rbw, f_start, f_stop, file):
    global freq_scanning
    global port_scanning
    global reprise_port_scanning
    global trace
    global trace_csv

    freq = f_start
    echanges=[]


    while freq <= (f_stop) and freq_scanning == True:
        freq_b = bytes(str(freq), 'utf-8')
        pySA.echangeLS(port=portFSP, data=b'CALC:MARK:X ' + freq_b + b' Hz\n', log=False, display=False,
                  echange=echanges, waitRep=0)
        x = pySA.echangeLS(port=portFSP, data=b'CALC:MARK:X?;Y?\n', log=False, display=False, echange=echanges,
                      waitRep=True)

        f = re.findall("b'(.*);", x['reponse'])[0]
        amp = str(re.findall("b'\d+;(.*)\\\\r", x['reponse'])[0])

        trace[0].append(float(f))
        trace[1].append(float(amp))

        trace_csv[0].append(str(f))
        amp = amp.replace('.', ',')
        trace_csv[1].append(str(amp))
        freq = freq + rbw / 2

# fonction appelée par l'IHM pour démarrer
#  le balayage fréquentiel et récupérer les amplitudes
def start_scan(port, rbw, f_start, f_stop, file):
    global freq_scanning
    global port_scanning
    global reprise_port_scanning
    global trace
    global trace_csv
    global trace_to_plot

    trace = [[],[]]
    trace_csv = [[],[]]

    print('start scanning frequency')
    # time.sleep(5)

    if port != '':
        scan_results = scan_freq(port, rbw, f_start, f_stop, file)
        trace_to_plot = True
        if file == DEFAULT_FILE_TEXT:
            save_to_default_file(trace_csv)
        else:
            save_to_file(trace_csv, file)
    else:
        pass

    reprise_port_scanning = True
    port_scanning = True

    return scan_results

# fonction de démarrage un balayage
#  fréquentiel sur l'analyseur de spectre
# avec les paramètres de la norme de l'IHM
def preparam_start_scan(port, norm_range, file):
    global freq_scanning
    global port_scanning
    global reprise_port_scanning
    global trace_to_plot
    global trace
    global trace_csv

    trace = [[],[]]
    trace_csv = [[],[]]

    for sub_range in norm_range:
        print('start scanning subrange frequency')
        # time.sleep(5)
        if port != '':
            spectrum_analyzer_set(port, sub_range['RBW'], sub_range['VBW'], sub_range['SWT'], sub_range['f_start'], sub_range['f_stop'])
            sweep_scan(port,sub_range['SWT'])
            scan_results = scan_freq(port, sub_range['RBW'], sub_range['f_start'], sub_range['f_stop'], file)
            trace_to_plot = True
        else:
            pass
    if file == DEFAULT_FILE_TEXT:
        save_to_default_file(trace_csv)
    else:
        save_to_file(trace_csv, file)

    reprise_port_scanning = True
    port_scanning = True

    return scan_results

# fonction d'arrêt du scan fréquentiel
def stop_scan():
    stop_scan = True
    return stop_scan

# fonction de sauvegarde des résultats
#  dans le fichier par défaut
def save_to_default_file(results):
    DOC_DEFAULT_PATH = './'
    DOC_DEFAULT_NAME = datetime.datetime.today().strftime("%d-%m-%Y") + "_" + datetime.datetime.now().strftime(
        "%H-%M-%S") + ".csv"
    doc = DOC_DEFAULT_NAME
    try:
        with open(doc, 'w+') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(results)
    except IOError as e:
        # print("Couldn't open or write to file (%s)." % e) # python 2
        print(f"Couldn't open or write to file ({e})")  # py3 f-strings

# fonction de sauvegarde des résultats
#  dans le fichier spécifié dans l'IHM
def save_to_file(results, doc):
    try:
        with open(doc, 'w+') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(results)
    except IOError as e:
        # print("Couldn't open or write to file (%s)." % e) # python 2
        print(f"Couldn't open or write to file ({e})")  # py3 f-strings

# fonction de choix d'affichage côté
#  côté analyseur de spectre
def display(disp, port):
    echanges = []
    if port != '':
        if disp == True:
            disp = False
            pySA.echangeLS(port=port, data=b'SYST:DISP:UPD OFF\n', log=True, display=True, echange=echanges, waitRep=0)
        elif disp == False:
            disp = True
            pySA.echangeLS(port=port, data=b'SYST:DISP:UPD ON\n', log=True, display=True, echange=echanges, waitRep=0)
    else:
        pass
    return disp

def sweep_mode(swp_mode, port):
    echanges = []
    if port != '':
        if swp_mode == True:
            swp_mode = False
            pySA.echangeLS(port=port, data=b'INIT:CONT OFF\n', log=True, display=True, echange=echanges, waitRep=0)
        elif swp_mode == False:
            swp_mode = True
            pySA.echangeLS(port=port, data=b'INIT:CONT ON\n', log=True, display=True, echange=echanges, waitRep=0)
    else:
        pass
    return swp_mode

def local_remote(loc_rem, port):
    global port_scanning
    global reprise_port_scanning

    echanges = []
    if port != '':
        if loc_rem == True:
            loc_rem = False
            pySA.echangeLS(port=port, data=b'@REM\n', log=True, display=True, echange=echanges, waitRep=0)
            reprise_port_scanning = True
        elif loc_rem == False:
            loc_rem = True
            port_scanning = False
            pySA.echangeLS(port=port, data=b'@LOC\n', log=True, display=True, echange=echanges, waitRep=0)
    else:
        pass
    return loc_rem


def scan_inst(scn_inst, port):
    global port_scanning
    global reprise_port_scanning

    echanges = []
    if port != '':
        if scn_inst == True:
            scn_inst = False
            port_scanning = False

        elif scn_inst == False:
            scn_inst = True
            reprise_port_scanning = True
    else:
        pass
    return scn_inst

def current_probes_factor(probe):
    if probe == '94111-1L':
        Zt = [[20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 200000, 300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000, 2000000, 3000000, 4000000, 5000000, 6000000, 7000000, 8000000, 9000000, 10000000, 20000000, 30000000, 40000000, 50000000, 60000000, 70000000, 80000000, 90000000, 100000000, 200000000, 300000000, 400000000, 500000000, 600000000, 700000000, 800000000, 900000000, 1000000000],
              [-81.9, -83.7, -81.5, -80.6, -78.6, -78.8, -76.7, -76.3, -75.6, -70, -66.3, -63.9, -62.1, -60.4, -59.2, -58.1, -57.1, -56.2, -50.3, -46.7, -44.3, -42.4, -40.7, -39.5, -38.3, -37.3, -36.3, -30.5, -27.0, -24.6, -22.7, -21.1, -19.9, -18.8, -17.8, -17.0, -11.6, -8.7, -6.9, -5.6, -4.5, -3.7, -3.0, -2.4, -1.9, 1.2, 2.9, 3.9, 4.7, 5.4, 5.9, 6.3, 6.7, 7.0, 8.8, 9.7, 10.3, 10.8, 11.2, 11.6, 11.9, 12.2, 12.4, 13.1, 14.2, 14.6, 14.9, 15.5, 15.3, 15.1, 14.7, 13.0]]
    return Zt


# demande de scan automatique selon
#  un NCE01 normatif
def set_nce01():
    limite = []

# demande de scan automatique selon
#  un NCE02 normatif
def set_nce02():
    limite = [  [50,    10000, 500000, 50000000],
                [140,   95,    60,     60]  ]
    NCE02_subRange1 = {'f_start': 30, 'f_stop': 1e3, 'RBW': 10, 'DWT': 0.15, 'resolution': 1, 'VBW': VBW_INI}
    NCE02_subRange2 = {'f_start': 1e3, 'f_stop': 10e3, 'RBW': 100, 'DWT': 0.015, 'resolution': 1e3, 'VBW': VBW_INI}
    NCE02_subRange3 = {'f_start': 10e3, 'f_stop': 150e3, 'RBW': 1e3, 'DWT': 0.015, 'resolution': 1e3, 'VBW': VBW_INI}
    NCE02_subRange4 = {'f_start': 150e3, 'f_stop': 30e6, 'RBW': 10e3, 'DWT': 0.015, 'resolution': 1e6, 'VBW': VBW_INI}

    # NCE02_range = [NCE02_subRange1, NCE02_subRange2, NCE02_subRange3, NCE02_subRange4]

    NCE02_range = [NCE02_subRange1, NCE02_subRange2]

    NbPoints = 0
    for item in NCE02_range:
        NbPoints += (2 * (item['f_stop'] - item['f_start']) / item['RBW'])
        item['SWT'] = (2 * (item['f_stop'] - item['f_start']) / item['RBW']) * item['DWT']

    return limite, NCE02_range, NbPoints

# demande de scan automatique selon
#  un NCE05 normatif
def set_nce05():
    limite = []

# fonction d'import de résultats
#  et affichage sur le graphique de l'IHM
def import_data(doc):
    values=[]
    try:
        with open(doc, newline='') as f:
            data = csv.reader(f, delimiter=',')
            for row in data:
                if row != []:
                    values.append(row)
            x_axis = [float(i) for i in values[0]]
            y_axis = [float(i) for i in values[1]]
            return x_axis, y_axis
    except IOError as e:
        # print("Couldn't open or write to file (%s)." % e) # python 2
        print(f"Couldn't open or write to file ({e})")  # py3 f-strings

# fonction de conversion des
#  chaines de caractères de l'IHM
#  en nombre
def str_to_number(number):
    if type(number) != int or type(number) != float:
        num = re.findall('\d+', number)
        # print(len(num))
        if len(num) > 0:
            num = num[0]
        else:
            num = 1
        # str = re.findall('\w+', number)
        mult = re.findall('[kKmMun]+', number)
        if len(mult) == 1:
            mult = mult[0]
            if mult in ['k', 'K']:
                mult = 1e3
            elif mult == 'm':
                mult = 1/1e3
            elif mult == 'u':
                mult = 1/1e6
            elif mult == 'n':
                mult = 1/1e9
            elif mult == 'M':
                mult = 1e6
            num_str = float(num) * float(mult)
        elif len(mult) > 1:
            pass
        else:
            mult = 1
            num_str = float(num) * float(mult)

    return num_str

# fonction de conversion des
#  nombre de caractères de l'IHM
#  en chaine de caractère
def number_to_str(number):
    num_e6 = number / 1e6
    num_e3 = number / 1e3
    num_em3 = number * 1e3
    num_em6 = number * 1e6
    num_em9 = number * 1e9
    if 0 <= number < 1000:
        str_num = str(number)
    elif num_e6 >= 1:
        str_num = str(num_e6) + " M"
    elif num_e3 >= 1:
        str_num = str(num_e3) + " k"
    elif num_em3 >= 1:
        str_num = str(num_e3) + " m"
    elif num_em6 >= 1:
        str_num = str(num_e3) + " u"
    elif num_em9 >= 1:
        str_num = str(num_e3) + " n"
    else:
        str_num = str(number)

    return str_num

# fontion de génération du graphique dans l'IHM
def draw_figure_w_toolbar(canvas, fig, canvas_toolbar,scatt):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=1)
    if scatt:
        time.sleep(0.05)
    return fig

# fonction d'initialisation des paramètres
#  du graphique
def set_plot():
    plt.figure(1, edgecolor='red')
    plt.xscale('log')
    plt.xlabel('frequence (Hz)')
    plt.ylabel('amp (' + str(UNITE) + ')')
    plt.grid(visible=True, which='both', axis='both', color='grey', linestyle='--', linewidth=0.5)
    plt.subplots_adjust(left=0.08, bottom=0.12, right=0.985, top=0.985, wspace=None, hspace=None)
    fig = plt.gcf()
    DPI = fig.get_dpi()
# you have to play with this size to reduce the movement error when the mouse hovers over the figure, it's close to canvas size
    fig.set_size_inches(404 * 2 / float(DPI), 404 / float(DPI))
    # -------------------------------
    return fig

# fonction de tracé du graphique point à point
def tracer_ppp(fig, window):
    x_axis = []
    y_axis = []
    for i in range(100):
        x = i
        x_axis.append(i)
        y = np.random.random()
        y_axis.append(y)
        print(str(y))
        plt.scatter(x, y)
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas,True)
    return(x_axis, y_axis)

# fonction de tracé du graphique continu
def tracer_continue(x_axis, y_axis, fig, window):
    plt.plot(x_axis, y_axis)
    draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas,False)

# fonction de RAZ du graphique
def clear_plot():
    plt.clf()


# fonction de démarrage de l'IHM
def my_window():
    global port_scanning, rbw
    global freq_scanning
    global reprise_port_scanning
    global instruments_liste
    global updt_instruments
    global trace
    global trace_csv
    global trace_to_plot

    layout = \
    [
    [
    [rs.RoundedButton("SCAN INSTRUMENTS", mouseover_colors=('white',rs.theme_background_color()), size_image=(200,25), border_width=0, button_color=('white',sg.theme_background_color()), font = STAND_FONT),sg.Text('Instruments:',font=STAND_FONT), sg.Combo(values=[], font=STAND_FONT, key='InstList', expand_x=True, bind_return_key=True, enable_events=True), sg.Text('Port:', font=STAND_FONT), sg.Text(key='ComPort', font=STAND_FONT, size=5)]],
    [
        sg.Frame(layout=
            [[sg.Column(layout=
                [[rs.RoundedButton('DISPLAY ON/OFF', mouseover_colors=('white', rs.theme_background_color()),
                                   size_image=(150, 25), border_width=0, button_color=('white', sg.theme_background_color()),
                                   font=STAND_FONT)], [
                     rs.RoundedButton('SWEEP MODE', mouseover_colors=('white', rs.theme_background_color()),
                                      size_image=(150, 25), border_width=0, button_color=('white', sg.theme_background_color()),
                                      font=STAND_FONT)], [
                     rs.RoundedButton('LOCAL/REMOTE', mouseover_colors=('white', rs.theme_background_color()),
                                      size_image=(150, 25), border_width=0, button_color=('white', sg.theme_background_color()),
                                      font=STAND_FONT)]],key='COL_COMMANDS', justification='center', expand_x=True, expand_y=True, background_color=BKGN_FRAME_COL)]],title='Commands', expand_x=True, expand_y=True,font=DESC_FONT, element_justification='center', relief=sg.RELIEF_FLAT,pad=(0,0)),
        sg.Frame(layout=
            [[sg.Column(layout=
                [[sg.Column(layout=
                    [[rs.RoundedButton("SET", mouseover_colors=('white',rs.theme_background_color()), size_image=(100,25), border_width=0, button_color=('white',sg.theme_background_color()), font = STAND_FONT)], [rs.RoundedButton("GET", mouseover_colors=('white',rs.theme_background_color()), size_image=(100,25), border_width=0, button_color=('white',sg.theme_background_color()), font = STAND_FONT)],[],[rs.RoundedButton("START SCAN", mouseover_colors=('white',rs.theme_background_color()), size_image=(100,25), border_width=0, button_color=('white',sg.theme_background_color()), font = STAND_FONT)],[rs.RoundedButton("STOP SCAN", mouseover_colors=('white',rs.theme_background_color()), size_image=(100,25), border_width=0, button_color=('white',sg.theme_background_color()), font = STAND_FONT)]], justification='center', background_color=BKGN_FRAME_COL),
        sg.Column(layout=
            [[sg.Column(layout=
                [[sg.Column(layout=
                    [[sg.Text('Start frequency:',size=SZ_LABEL,font=STAND_FONT, background_color=BKGN_FRAME_COL), sg.InputText(key='f_start',size=SZ_IN_TEXT, default_text=F_START_INI, enable_events = True,font=STAND_FONT, background_color=BKGN_FRAME_COL)],
                    [sg.Text('Stop frequency:',size=SZ_LABEL,font=STAND_FONT, background_color=BKGN_FRAME_COL), sg.InputText(key='f_stop',size=SZ_IN_TEXT, default_text=F_STOP_INI, enable_events = True,font=STAND_FONT, background_color=BKGN_FRAME_COL)]], background_color=BKGN_FRAME_COL),
                sg.Column(layout=
                    [[sg.Text('Central frequency:',size=SZ_LABEL,font=STAND_FONT, background_color=BKGN_FRAME_COL), sg.InputText(key='f_centrale',size=SZ_IN_TEXT, default_text=F_CENTRALE_INI, enable_events = True,font=STAND_FONT, background_color=BKGN_FRAME_COL)],
                    [sg.Text('Span:',size=SZ_LABEL,font=STAND_FONT, background_color=BKGN_FRAME_COL), sg.InputText(key='f_span',size=SZ_IN_TEXT, default_text=F_SPAN_INI, enable_events = True,font=STAND_FONT, background_color=BKGN_FRAME_COL)]], background_color=BKGN_FRAME_COL)]]
            ,justification='center', background_color=BKGN_FRAME_COL)],
            [sg.Column(layout=
                [[sg.Column(layout=
                    [[sg.Text('RBW:',font=STAND_FONT, background_color=BKGN_FRAME_COL), sg.InputText(key='RBW',size=SZ_IN_TEXT,default_text=RBW_INI,font=STAND_FONT, background_color=BKGN_FRAME_COL)],[sg.Text('(Resolution Bandwidth)',size=SZ_LABEL,font=DESC_FONT, background_color=BKGN_FRAME_COL)]], background_color=BKGN_FRAME_COL),
                 sg.Column(layout=
                    [[sg.Text('VBW:',font=STAND_FONT, background_color=BKGN_FRAME_COL), sg.InputText(key='VBW',size=SZ_IN_TEXT, default_text=VBW_INI,font=STAND_FONT, background_color=BKGN_FRAME_COL)],[sg.Text('(Video Bandwidth)',size=SZ_LABEL,font=DESC_FONT, background_color=BKGN_FRAME_COL)]], background_color=BKGN_FRAME_COL),
                 sg.Column(layout=
                    [[sg.Text('SWT:',font=STAND_FONT, background_color=BKGN_FRAME_COL), sg.InputText(key='SWT',size=SZ_IN_TEXT, default_text=SWT_INI,font=STAND_FONT, background_color=BKGN_FRAME_COL)],[sg.Text('(Sweep Time)',size=SZ_LABEL,font=DESC_FONT, background_color=BKGN_FRAME_COL)]], background_color=BKGN_FRAME_COL)
                ]], justification='center', background_color=BKGN_FRAME_COL)]], background_color=BKGN_FRAME_COL)]],key='COL_FREQ_PARAM', justification='center', expand_x=True, expand_y=True, background_color=BKGN_FRAME_COL)]],title='Frequency parameters',expand_x=True,font=DESC_FONT, element_justification='center', relief=sg.RELIEF_FLAT,pad=(0,0))],

        [sg.Frame(layout=
            [[sg.Column(layout=[
                [rs.RoundedButton("NCE01", mouseover_colors=('white',rs.theme_background_color()), size_image=(100,25), border_width=0, button_color=('white',sg.theme_background_color()), font = 'calibri 14 bold'), rs.RoundedButton("NCE02", mouseover_colors=('white',rs.theme_background_color()), size_image=(100,25), border_width=0, button_color=('white',sg.theme_background_color()), font = STAND_FONT), rs.RoundedButton("NCE05", mouseover_colors=('white',rs.theme_background_color()), size_image=(100,25), border_width=0, button_color=('white',sg.theme_background_color()), font = STAND_FONT)]]
        , justification='center')]],title='Normative pre-parametered scan',font=DESC_FONT,vertical_alignment='center', element_justification='center', expand_x=True)],

    [sg.Text('Scan progress:', font=STAND_FONT),
         sg.ProgressBar(max_value=100, orientation='h', size=(20, 20),
                        key='scan_progress', expand_x=True)],

    [sg.Column(layout=[[sg.Canvas(key='controls_cv', expand_x=True)], [sg.Canvas(key='fig_cv', size=(GRAPH_SIZE_X, GRAPH_SIZE_Y), expand_x=True, expand_y=True)], [sg.Text('File:', font=STAND_FONT), sg.InputText(key='file', default_text=DEFAULT_FILE_TEXT, font=DESC_FONT, expand_x=True), rs.RoundedButton("Save", mouseover_colors=('white', rs.theme_background_color()), size_image=(100, 25), border_width=0, button_color=('white', sg.theme_background_color()), font=STAND_FONT), rs.RoundedButton("Import", mouseover_colors=('white', rs.theme_background_color()), size_image=(100, 25), border_width=0, button_color=('white', sg.theme_background_color()), font=STAND_FONT), rs.RoundedButton("Clear graph", mouseover_colors=('white',rs.theme_background_color()), size_image=(100,25), border_width=0, button_color=('white',sg.theme_background_color()), font = STAND_FONT)]],expand_x=True, expand_y=True, pad=(0,20))],

    ]

    window = sg.Window(
        title='pySpectrumAnalyzer',
        font=STAND_FONT,
        layout=layout,
        finalize=True,
        location=(1,1),
        resizable=True,
    )

    wind_start_size = window.get_screen_size()
    window.set_min_size((X_WIND_MIN, Y_WIND_MIN))
    window['COL_COMMANDS'].ParentRowFrame.config(background=BKGN_FRAME_COL)
    fig = draw_figure_w_toolbar(window['fig_cv'].TKCanvas, set_plot(), window['controls_cv'].TKCanvas,False)

    # window.Maximize()
    preparam_scan = False

    init_timeout = True
    instruments_liste = []

    port = ''
    port_scanning = True
    freq_scanning = False
    reprise_port_scanning = False
    disp = True
    swp_mode = True
    loc_rem = False
    scn_inst = True
    updt_instruments = False
    trace_to_plot = False

    thread_tmt = threading.Thread(target=thread_scan_port_com, args=(instruments_liste, window), daemon=True)
    thread_tmt.start()

    while True:
        event, values = window.Read(timeout=0.5)

        if event in [None, 'Exit']:  # always,  always give a way out!
            break

        elif event == 'SET':
            port_scanning = False
            time.sleep(1)
            if port != '':
                spectrum_analyzer_set(port, rbw, vbw, swt, f_start, f_stop)
            else:
                pass
            reprise_port_scanning = True

        elif event == 'GET':
            port_scanning = False
            time.sleep(1)
            if port != '' and port.isOpen():
                try:
                    sa_conf = spectrum_analyzer_get_conf(port)
                    str_rbw = number_to_str(int(re.findall('b\'(\d+)', sa_conf['RBW'])[0]))
                    str_vbw = number_to_str(int(re.findall('b\'(\d+)', sa_conf['VBW'])[0]))
                    str_swt = number_to_str(int(re.findall('b\'(\d+)', sa_conf['SWT'])[0]))
                    str_f_start = number_to_str(int(re.findall('b\'(\d+)', sa_conf['F_START'])[0]))
                    str_f_stop = number_to_str(int(re.findall('b\'(\d+)', sa_conf['F_STOP'])[0]))
                    window['f_start'].update(str_f_start + UNITE_FREQ)
                    window['f_stop'].update(str_f_stop + UNITE_FREQ)
                    window['RBW'].update(str_rbw + UNITE_FREQ)
                    window['VBW'].update(str_vbw + UNITE_FREQ)
                    window['SWT'].update(str_swt + UNITE_TEMPS)
                    fspan = str_to_number(window['f_stop'].get()) - str_to_number(window['f_start'].get())
                    window['f_span'].update(number_to_str(fspan) + UNITE_FREQ)
                    fcentrale = str_to_number(window['f_start'].get()) + str_to_number(window['f_span'].get()) / 2
                    window['f_centrale'].update(number_to_str(fcentrale) + UNITE_FREQ)
                except:
                    pass
                reprise_port_scanning = True

        elif event == 'START SCAN':
            if port != '':
                port_scanning = False
                time.sleep(1)
                freq_scanning = True
                sweep_scan(port, swt)
                thread_scan = threading.Thread(target=start_scan, args=(port, rbw, f_start, f_stop, window['file'].get()), daemon=True)
                thread_scan.start()
            else:
                pass

        elif preparam_scan:
            if port != '':
                preparam_scan = False
                port_scanning = False
                time.sleep(1)
                freq_scanning = True
                thread_scan = threading.Thread(target=preparam_start_scan, args=(port, norm_range, window['file'].get()), daemon=True)
                thread_scan.start()
            else:
                pass

        elif event == 'STOP SCAN':
            freq_scanning = False
            pass

        elif event == 'NCE01':
            pass

        elif event == 'NCE02':
            limite, norm_range, nb_points = set_nce02()
            tracer_continue(limite[0], limite[1], fig, window)
            preparam_scan = True
            port_scanning = False
            time.sleep(1)
            freq_scanning = True
            preparam_name = 'NCEO2'

        elif event == 'NCE05':
            pass

        elif event == 'Clear graph':
            clear_plot()
            fig = draw_figure_w_toolbar(window['fig_cv'].TKCanvas, set_plot(), window['controls_cv'].TKCanvas,False)

        elif event == 'Save':
            pass

        elif event == 'Import':
            if window['file'].get() in [DEFAULT_FILE_TEXT, '']:
                pass
            else:
                file = window['file'].get()
                x_axis, y_axis = import_data(file)
                tracer_continue(x_axis, y_axis, fig, window)

        elif event == 'f_start':
            if str_to_number(window['f_start'].get()) < 10e3:
                pass
            if str_to_number(window['f_stop'].get()) > str_to_number(window['f_start'].get()):
                fspan = str_to_number(window['f_stop'].get()) - str_to_number(window['f_start'].get())
                window['f_span'].update(number_to_str(fspan) + UNITE_FREQ)
                fcentrale = str_to_number(window['f_start'].get()) + str_to_number(window['f_span'].get()) / 2
                window['f_centrale'].update(number_to_str(fcentrale) + UNITE_FREQ)

        elif event == 'f_stop':
            if str_to_number(window['f_stop'].get()) > str_to_number(window['f_start'].get()):
                fspan = str_to_number(window['f_stop'].get()) - str_to_number(window['f_start'].get())
                window['f_span'].update(number_to_str(fspan) + UNITE_FREQ)
                fcentrale = str_to_number(window['f_start'].get()) + str_to_number(window['f_span'].get()) / 2
                window['f_centrale'].update(number_to_str(fcentrale) + UNITE_FREQ)

        elif event == 'f_centrale':
            fstart = str_to_number(window['f_centrale'].get()) - str_to_number(window['f_span'].get()) / 2
            if fstart < 10e3:
                pass
            else:
                window['f_start'].update(number_to_str(fstart) + UNITE_FREQ)
                fstop = str_to_number(window['f_centrale'].get()) + str_to_number(window['f_span'].get()) / 2
                window['f_stop'].update(number_to_str(fstop) + UNITE_FREQ)

        elif event == 'f_span':
            fstart = str_to_number(window['f_centrale'].get()) - str_to_number(window['f_span'].get()) / 2
            if fstart < 10e3:
                pass
            else:
                window['f_start'].update(number_to_str(fstart) + UNITE_FREQ)
                fstop = str_to_number(window['f_centrale'].get()) + str_to_number(window['f_span'].get()) / 2
                window['f_stop'].update(number_to_str(fstop) + UNITE_FREQ)

        elif event =='InstList':
            instrument = window['InstList'].get()
            if len(instrument) > 0:
                for item in instruments_liste:
                    if item[0] == instrument:
                        port = item[1]
                        port_name = item[1].name
                        window['ComPort'].update(port_name)
                    else:
                        port = ''
                        port_name = ''
                        window['ComPort'].update(port_name)

        if updt_instruments:
            updt_instruments_liste(instruments_liste, window)
            updt_instruments = False

        elif reprise_port_scanning:
            port_scanning = True
            thread_tmt = threading.Thread(target=thread_scan_port_com, args=(instruments_liste, window), daemon=True)
            thread_tmt.start()
            reprise_port_scanning = False

        elif trace_to_plot:
            trace_to_plot = False
            tracer_continue(trace[0], trace[1], fig, window)

        elif event == 'DISPLAY ON/OFF':
            disp = display(disp, port)

        elif event == 'SWEEP MODE':
            swp_mode = sweep_mode(swp_mode, port)

        elif event == 'LOCAL/REMOTE':
            loc_rem = local_remote(loc_rem, port)

        elif event == 'SCAN INSTRUMENTS':
            scn_inst = scan_inst(scn_inst, port)

        elif event == '__TIMEOUT__':
            f_start = str_to_number(window['f_start'].get())
            f_stop = str_to_number(window['f_stop'].get())
            rbw = str_to_number(window['RBW'].get())
            vbw = str_to_number(window['VBW'].get())
            swt = str_to_number(window['SWT'].get())

    window.Close()

if __name__ == '__main__' :
    my_window()
    print('Exiting window')

