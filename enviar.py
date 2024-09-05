import requests
import random
import json
import time
from datetime import datetime

plc1Indexes = [None] * 9
plc2Indexes = [None] * 6
plc3Indexes = [None] * 14

plc1IP = '192.168.1.10'
plc2IP = '192.168.1.11'
plc3IP = '192.168.1.12'

MoversUDT = ['Operation1', 'Operation2', 'Operation3', 'Operation4', 'Operation5', 'Operation6', 'Operation7', 'Operation8', 'Operation9', 'Operation10', 'Operation11', 'Operation12', 'Operation13', 'Operation14']
Frnt590UDT = ['FrontOperation1', 'FrontOperation2', 'FrontOperation3', 'FrontOperation4', 'FrontOperation5', 'FrontOperation6', 'FrontOperation7', 'FrontOperation8', 'FrontOperation9']
Rear590UDT = ['RearOperation1', 'RearOperation2', 'RearOperation3', 'RearOperation4', 'RearOperation5', 'RearOperation6']

url = 'https://mes-web.goandsee.co/api/plcs'

counter = 0

def update_serial_numbers():
    serial_number1 = f"MFF{random.randint(0, 9999):04d}AC;{random.randint(0, 9999):04d}B"
    serial_number2 = f"MFR{random.randint(0, 9999):04d}AC;{random.randint(0, 9999):04d}B"
    
    plc1Indexes.insert(0, serial_number1)
    plc3Indexes.insert(0, plc1Indexes[9])
    plc1Indexes.pop()
    plc3Indexes.pop()
    plc2Indexes.insert(0, serial_number2)
    plc2Indexes.pop()

def generate_plc_data(plc_number, number_of_stations):
    global counter
    tags = []
    
    for i in range(number_of_stations):
        if plc_number == 1:
            serial_number = plc1Indexes[i]
            tag_name = Frnt590UDT[i]
        elif plc_number == 2:
            serial_number = plc2Indexes[i]
            tag_name = Rear590UDT[i]
        elif plc_number == 3:
            serial_number = plc3Indexes[i]
            tag_name = MoversUDT[i]

        station_data = {
            'OperationName': tag_name,
            'ST_ID': counter,
            'PassFail': 1 if serial_number else None,
            'StartTm': datetime.now().isoformat(),
            'EndTm': datetime.now().isoformat(),
            'Sn': serial_number,
            'VarData': random.randint(0, 100),
            'TestSpec': random.randint(0, 100),
            'Trigger': True
        }

        counter += 1
        tags.append(station_data)

    return tags

def send_data(data):
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response.raise_for_status()

        response_data = response.json()
        print('Respuesta del servidor:', response_data['message'], response.status_code)
    except requests.exceptions.RequestException as error:
        print('Error al enviar la solicitud:', error)

def send_data_periodically():
    global counter

    while True:
        counter = 0
        update_serial_numbers()

        plc1_data = generate_plc_data(1, 9)
        plc2_data = generate_plc_data(2, 6)
        plc3_data = generate_plc_data(3, 14)

        PLCs = [
            {'IP': plc1IP, 'Tags': plc1_data},
            {'IP': plc2IP, 'Tags': plc2_data},
            {'IP': plc3IP, 'Tags': plc3_data}
        ]

        data = {'PLCs': PLCs}
        send_data(data)

        time.sleep(4)

# Iniciar el envío periódico de datos
send_data_periodically()
