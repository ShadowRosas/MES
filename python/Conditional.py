

from pycomm3 import LogixDriver
import time
import threading
import requests

# Lista de tags que queremos leer
tags_to_read = ['MoversUDT[{}]'.format(i) for i in range(17)]
tags_to_read2 = ['Frnt590UDT[{}]'.format(i) for i in range(17)]
tags_to_read3 = ['Rear590UDT[{}]'.format(i) for i in range(17)]
# URL a la que queremos enviar los datos
url = 'https://mes-web.goandsee.co/api/plcs'  # Reemplaza con la URL correcta

plc_ips = {
    1: '192.168.50.70',
    2: '192.168.50.10',
    3: '192.168.50.40'
}

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

                    if Trigger == True:
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
                        print("\nDatos enviados exitosamente desde", plc_address, flush=True)
                    else:
                        print("\nError al enviar datos desde", plc_address, ": ", response.status_code, response.text, flush=True)
                except requests.exceptions.RequestException as e:
                    print("\nExcepción durante la solicitud POST desde", plc_address, ": ", e, flush=True)
            else:
                print("\nNo hay datos para enviar desde", plc_address, flush=True)

        except Exception as ex:
            print("\nError durante la comunicación con el PLC en", plc_address, ":", ex, flush=True)
        
        # Esperar 2 minutos antes de la próxima lectura
        time.sleep(0.2)



# Crear hilos para cada PLC
thread1 = threading.Thread(target=read_and_send_tags, args=('192.168.50.70', tags_to_read, url,plc_ips))
thread2 = threading.Thread(target=read_and_send_tags, args=('192.168.50.10', tags_to_read2, url,plc_ips))
thread3 = threading.Thread(target=read_and_send_tags, args=('192.168.50.40', tags_to_read3, url,plc_ips))
# Iniciar los hilos
thread1.start()
thread2.start()
thread3.start()
# Esperar a que los hilos terminen (en este caso, nunca terminarán)
thread1.join()
thread2.join()
thread3.join()