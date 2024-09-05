import requests
from pycomm3 import LogixDriver
import time
import threading
import sys

def fetch_lines():
    try:
        response = requests.get('http://127.0.0.1:5000/api/get-lines')
        response.raise_for_status()
        lines = response.json()
        print("Líneas obtenidas exitosamente.")
        return lines
    except requests.RequestException as error:
        print(f'Error al obtener las líneas: {error}')
        return []
    
lineID = "bc7asdfdjskld"

def fetch_Data_lines():
    try:
        response = requests.get(f'http://127.0.0.1:5000/api/get-line-data/{lineID}')
        response.raise_for_status()
        lines_data = response.json()
        print("Datos de líneas obtenidos exitosamente.")
        return lines_data
    except requests.RequestException as error:
        print(f'Error al obtener los datos de las líneas: {error}')
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


def read_and_send_tags(plc_address, tags, url):
    while True:
        all_data = {"data": []}
        try:
            with LogixDriver(plc_address) as plc:
                for tag in tags:
                    # Leer el valor del trigger de la etiqueta actual
                    trigger_value = plc.read(f'{tag}.Trigger').value
                    print(f"Valor del trigger para {tag}: {trigger_value}", flush=True)
                    if trigger_value:
                        # Leer toda la estructura de la etiqueta actual
                        print(f"Trigger desactivado para {tag}", flush=True)
                        data_structure = plc.read(tag).value
                        data_object = {subtag: str(value) for subtag, value in data_structure.items()}
                        all_data["data"].append(data_object)
                        # Cambiar el valor de la etiqueta actual.Trigger a False
                        plc.write(f'{tag}.Trigger', False)
            # Preparar los datos para enviar
            formatted_data = convert_all_data_to_plc_format(all_data, plc_ips)
            if all_data:
                # Enviar los datos como JSON a la URL especificada
                try:
                    response = requests.post(url, json=formatted_data)
                    print(f"Datos enviados: {formatted_data}", flush=True)
                    print(formatted_data)
                    if response.status_code == 200:
                        response_data = response.json()
                        print("\nDatos enviados exitosamente desde", plc_address, response_data['message'],response.status_code , flush=True)
                    else:
                        print("\nError al enviar datos desde", plc_address, ": ", response.status_code, response.text, flush=True)
                except requests.exceptions.RequestException as e:
                    print("\nExcepción durante la solicitud POST desde", plc_address, ": ", e, flush=True)
        except Exception as ex:
            print("\nError durante la comunicación con el PLC en", plc_address, ":", ex, flush=True)
        # Esperar 2 minutos antes de la próxima lectura
        time.sleep(120)

def process_information():
    lines = fetch_lines()
    linesdata = fetch_Data_lines()
    print("Procesando líneas y datos de líneas...")

    threads = []

    for index, item in enumerate(linesdata, start=1):
        ip = item['IP']
        plc_ips[index] = ip
        operations = item['operations']
        num_tags = len(operations)
        print(f"IP: {ip} - Número de Tags: {num_tags}")

        tags_to_read = [f'{operation}' for operation in operations]

        thread = threading.Thread(target=read_and_send_tags, args=(ip, tags_to_read, url))
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print("Todos los datos han sido enviados exitosamente desde los tres PLCs.")

# Ejecutar la función principal
process_information()
