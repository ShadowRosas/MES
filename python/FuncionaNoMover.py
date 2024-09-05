import aiohttp
import asyncio
from pycomm3 import LogixDriver
import time
import threading
import requests

async def fetch_lines():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://127.0.0.1:5000/api/get-lines') as response:
                lines = await response.json()
                return lines
    except Exception as error:
        print(f'Error fetching lines: {error}')

#async with session.get('http://127.0.0.1:5000/api/get-line-data/${lineId}') as response:

async def fetch_Data_lines():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://127.0.0.1:5000/api/get-line-data/ef9ijklmnoqrs') as response:
                lines_data = await response.json()
                return lines_data
    except Exception as error:
        print(f'Error fetching lines: {error}')

# Ejemplo de uso
async def information():
    lines = await fetch_lines()
    linesdata = await fetch_Data_lines()
    print(lines, linesdata)

# Ejecutar la función principal
asyncio.run(information())

tags = []

# Lista de tags que queremos leer
tags_to_read = ['MoversUDT[{}]'.format(i) for i in range(10)]
tags_to_read2 = ['Frnt590UDT[{}]'.format(i) for i in range(10)]
tags_to_read3 = ['Rear590UDT[{}]'.format(i) for i in range(10)]
# URL a la que queremos enviar los datos
url = 'https://mes-web.goandsee.co/api/plcs'  # Reemplaza con la URL correcta

plc_ips = {
    1: '192.168.50.70',
    2: '192.168.50.10',
    3: '192.168.50.40'
}

# Convertir all_data a la estructura esperada
def convert_all_data_to_plc_format(all_data, plc_ips):
    plc_data = {ip: [] for ip in plc_ips.values()}
    
    for tag_data in all_data["data"]:
        plc_ip = tag_data.get('IP')  # O el método correcto para obtener la IP del PLC
        if plc_ip in plc_data:
            plc_data[plc_ip].append(tag_data)

    # Estructura final para enviar al servidor
    plc_list = [{'IP': ip, 'Tags': tags} for ip, tags in plc_data.items()]
    return {'PLCs': plc_list}


def read_and_send_tags(plc_address, tags, url):
    print("SE INICIA LA DEFINICIÓN", flush=True)
    while True:
        all_data = {"data": []}
        try:
            with LogixDriver(plc_address) as plc:
                for tag in tags:
                    # Leer el valor del trigger de la etiqueta actual
                    trigger_value = plc.read(f'{tag}.Trigger').value
                    if trigger_value:
                        # Leer toda la estructura de la etiqueta actual
                        data_structure = plc.read(tag).value
                        data_object = {subtag: str(value) for subtag, value in data_structure.items()}
                        all_data["data"].append = (data_object)
                        # Cambiar el valor de la etiqueta actual.Trigger a False
                        plc.write(f'{tag}.Trigger', False)
            # Preparar los datos para enviar
            formatted_data = convert_all_data_to_plc_format(all_data, plc_ips)
            if all_data:
                # Enviar los datos como JSON a la URL especificada
                try:
                    response = requests.post(url, json=formatted_data)
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
# Crear hilos para cada PLC
thread1 = threading.Thread(target=read_and_send_tags, args=('192.168.50.70', tags_to_read, url))
thread2 = threading.Thread(target=read_and_send_tags, args=('192.168.50.10', tags_to_read2, url))
thread3 = threading.Thread(target=read_and_send_tags, args=('192.168.50.40', tags_to_read3, url))
# Iniciar los hilos
thread1.start()
thread2.start()
thread3.start()
# Esperar a que los hilos terminen (en este caso, nunca terminarán)
thread1.join()
thread2.join()
thread3.join()