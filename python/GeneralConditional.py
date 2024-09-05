import requests
from pycomm3 import LogixDriver
import time
import threading
import sys

# Archivo y variable
file_path = 'example.log'  # Cambia esto por la ruta de tu archivo .log
variable_name = 'VARIABLE_NAME'

def read_variable_from_log(file_path, variable_name):
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith(f'{variable_name}='):
                # Extraer y devolver el valor después del '='
                return line.split('=', 1)[1].strip()
    return None  # Devuelve None si la variable no se encuentra

# Leer la variable desde el archivo
lineID = read_variable_from_log(file_path, variable_name)

def fetch_lines():
    try:
        response = requests.get('http://127.0.0.1:5000/api/get-lines')
        response.raise_for_status()
        lines = response.json()
        print("Lines successfully obtained.")
        return lines
    except requests.RequestException as error:
        print(f'Error al obtener las líneas: {error}')
        return []

def fetch_Data_lines():
    try:
        response = requests.get(f'http://127.0.0.1:5000/api/get-line-data/{lineID}')
        response.raise_for_status()
        lines_data = response.json()
        print("Line data successfully obtained.")
        return lines_data
    except requests.RequestException as error:
        print(f'Error when obtaining data from the lines: {error}')
        return []

# URL a la que queremos enviar los datos
url = 'https://mes-web.goandsee.co/api/plcs'  # Reemplaza con la URL correcta

plc_ips = {}

# Convertir all_data a la estructura esperada
def convert_all_data_to_plc_format(all_data, plc_ips):
    plc_data = {ip: [] for ip in plc_ips.values()}
    
    # Asumiendo que all_data es un diccionario con claves como IPs de PLC y valores como listas de datos
    for plc_ip, tags_list in all_data.items():
        if plc_ip in plc_data:
            plc_data[plc_ip].extend(tags_list)
    
    # Estructura final para enviar al servidor
    plc_list = [{'IP': ip, 'Tags': tags} for ip, tags in plc_data.items()]
    return {'PLCs': plc_list}

def read_and_send_tags(plc_address, tags, url, plc_ips):
    print("Starting", flush=True)
    while True:
        all_data = {ip: [] for ip in plc_ips.values()}  # Estructura para almacenar los datos por IP
        try:
            with LogixDriver(plc_address) as plc:
                for tag in tags:
                    print(f"Reading tag: {tag}", flush=True)  # Mensaje de depuración
                    # Leer el valor del trigger de la etiqueta actual
                    ST_ID = plc.read(f'{tag}.ST_ID').value
                    PassFail = plc.read(f'{tag}.PassFail').value
                    StartTm = plc.read(f'{tag}.StartTm').value
                    EndTm = plc.read(f'{tag}.EndTm').value
                    Sn = plc.read(f'{tag}.Sn').value
                    VarData = plc.read(f'{tag}.VarData').value
                    TestSpec = plc.read(f'{tag}.TestSpec').value
                    Trigger = plc.read(f'{tag}.Trigger').value
                    PartStatus = plc.read(f'{tag}.PartStatus').value

                    print(f"Read values - ST_ID: {ST_ID}, PassFail: {PassFail}, StartTm: {StartTm}, EndTm: {EndTm}, Sn: {Sn}, VarData: {VarData}, TestSpec: {TestSpec}, Trigger: {Trigger}, PartStatus: {PartStatus}", flush=True)  # Mensaje de depuración

                    if Trigger == False:
                        # Leer toda la estructura de la etiqueta actual
                        data_structure = plc.read(tag).value
                        data_object = {
                            'ST_ID': str(ST_ID),
                            'PassFail': str(PassFail),
                            'StartTm': str(StartTm),
                            'EndTm': str(EndTm),
                            'Sn': str(Sn),
                            'VarData': str(VarData),
                            'TestSpec': str(TestSpec),
                            'Trigger': str(Trigger),
                            'PartStatus': str(PartStatus),
                            **{subtag: str(value) for subtag, value in data_structure.items()}
                        }
                        plc_ip = plc_address  # Cambia esto si la IP está en 'data_object'
                        if plc_ip in all_data:
                            all_data[plc_ip].append(data_object)
                            print(f"Data appended for IP {plc_ip}: {data_object}", flush=True)  # Mensaje de depuración
                        else:
                            print(f"IP {plc_ip} not in all_data keys", flush=True)  # Mensaje de depuración
                        # Cambiar el valor de la etiqueta actual.Trigger a False
                        plc.write(f'{tag}.Trigger', False)
        
            # Preparar los datos para enviar
            formatted_data = {'PLCs': [{'IP': ip, 'Tags': tags} for ip, tags in all_data.items()]}
            print(f"Formatted data to send: {formatted_data}", flush=True)  # Mensaje de depuración

            if any(all_data.values()):  # Verifica que haya datos para enviar
                # Enviar los datos como JSON a la URL especificada
                try:
                    response = requests.post(url, json=formatted_data)
                    if response.status_code == 200:
                        print("\nData successfully sent from", plc_address, flush=True)
                    else:
                        print("\nError sending data from", plc_address, ": ", response.status_code, response.text, flush=True)
                except requests.exceptions.RequestException as e:
                    print("\nException during POST request from", plc_address, ": ", e, flush=True)
            else:
                print("\nThere is no data to send from", plc_address, flush=True)

        except Exception as ex:
            print("\nError during communication with the PLC in", plc_address, ":", ex, flush=True)
        
        # Esperar 2 milisegundos antes de la próxima lectura
        time.sleep(0.2)

def process_information():
    lines = fetch_lines()
    linesdata = fetch_Data_lines()
    print("Processing lines and line data..")

    threads = []

    for index, item in enumerate(linesdata, start=1):
        ip = item['IP']
        plc_ips[index] = ip
        operations = item['operations']
        num_tags = len(operations)
        print(f"IP: {ip} - Number of Tags: {num_tags}")

        tags_to_read = [f'{operation}' for operation in operations]

        thread = threading.Thread(target=read_and_send_tags, args=(ip, tags_to_read, url,plc_ips))
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


# Ejecutar la función principal
process_information()