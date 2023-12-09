import serial
import datetime
import time

TIMEOUT_SERIAL_DEFAULT = 0.05
WAIT_READ = 0.5
WAIT_READ_ALL = 0.5

file = open('./my_log.txt', 'w+')

# def trusty_sleep(n):
#     start = time.time()
#     while (time.time() - start < float(n)):
#         time.sleep(n - (time.time() - start))

def serial_data_manager(com, display, log):
    if display:
        print(str(com['date']) + " | " + "port id : " + str(com['portSerie'].name) + " | " + "requete : " + str(
            com['requete']) + " | " + "réponse : " + str(com['reponse']))
    if log:
        file = open('./my_log.txt', 'w+')
        file.write(str(com))
        file.close()

def wait_readAll(port, log, display):
    data_read = b''
    wait = 0
    com = None
    try:
        while data_read == b'':
            time.sleep(WAIT_READ_ALL)
            wait += 1
            if type(wait/10) == int:
                print("waiting for data on port " +str(port)+ "for " +str(wait*WAIT_READ_ALL))
            data_read = port.read_all()
        com = {'date': str(datetime.datetime.now()),
               'portSerie': port,
               'requete': None,
               'reponse': str(data_read)}
        serial_data_manager(com, display, log)
    except Exception:
        pass
    return com

def exchange_line_serial(port, data, waitRep, log, display):
    com = []
    try:
        port.write(data)
        if waitRep:
            time.sleep(WAIT_READ)
            reponse = port.readline()
        else:
            reponse = port.readline()
        com = {'date'       : str(datetime.datetime.now()),
               'portSerie'  : port,
               'requete'    : data,
               'reponse'    : str(reponse)}
        serial_data_manager(com, display, log)
    except Exception:
        pass
    return com

def exchange_all_serial(port, data, waitRep, log, display):
    com = []
    try:
        port.write(data)
        if waitRep:
            time.sleep(WAIT_READ)
            reponse = port.read_all()
        else:
            reponse = port.read_all()
        com = {'date'       : str(datetime.datetime.now()),
               'portSerie'  : port,
               'requete'    : data,
               'reponse'    : str(reponse)}
        serial_data_manager(com, display, log)
    except Exception:
        pass
    return com