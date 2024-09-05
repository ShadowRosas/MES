const fetch = require('isomorphic-fetch');

let plc1Indexes = Array(9).fill(null);
let plc2Indexes = Array(6).fill(null);
let plc3Indexes = Array(14).fill(null);
//const url = 'https://mes-web.goandsee.co/plcs';
const url = 'https://mes-web.goandsee.co/api/plcs';
//const url = 'https://f87d-189-201-171-61.ngrok-free.app/api/plcs';

// Definir las variables UDTs
const MoversUDT = [
    'Operation1',
    'Operation2',
    // ... completa con más nombres de operaciones
];

const Frnt590UDT = [
    'FrontOperation1',
    'FrontOperation2',
    // ... completa con más nombres de operaciones
];

const Rear590UDT = [
    'RearOperation1',
    'RearOperation2',
    // ... completa con más nombres de operaciones
];

const plc1IP = '192.168.1.10';
const plc2IP = '192.168.1.11';
const plc3IP = '192.168.1.12';

const plcIPs = ['192.168.1.10', '192.168.1.11', '192.168.1.12'];

const plc3Tags = Array.from({length: 14}, (v, i) => MoversUDT[i]);
const plc1Tags = Array.from({length: 9}, (v, i) => Frnt590UDT[i]);
const plc2Tags = Array.from({length: 6}, (v, i) => Rear590UDT[i]);


let counter = 0;

// Función para generar un número de serie único para cada estación
function updateSerialNumbers() {
    const serialNumber1 = `MFF${Math.floor(Math.random() * 10000).toString().padStart(4, '0')}AC;${Math.floor(Math.random() * 10000).toString().padStart(4, '0')}B`;
    const serialNumber2 = `MFR${Math.floor(Math.random() * 10000).toString().padStart(4, '0')}AC;${Math.floor(Math.random() * 10000).toString().padStart(4, '0')}B`;    
    
    plc1Indexes.unshift(serialNumber1);
    plc3Indexes.unshift(plc1Indexes[9]);
    plc1Indexes.pop();
    plc3Indexes.pop();
    plc2Indexes.unshift(serialNumber2);
    plc2Indexes.pop();
}


// Función para generar el array con los datos simulados para un PLC y sus estaciones
function generatePLCData(plcNumber, numberOfStations) {
    const Tags = [];

    for (let i = 0; i < numberOfStations; i++) {

        let serialNumber;
        let tagName;

        switch (plcNumber) {
            case 1:
                serialNumber = plc1Indexes[i];
                tagName = plc1Tags[i];
                break;
            case 2:
                serialNumber = plc2Indexes[i];
                tagName = plc2Tags[i];
                break;
            case 3:
                serialNumber = plc3Indexes[i];
                tagName = plc3Tags[i];
                break;
        }

        const stationData = {
            OperationName: tagName,
            ST_ID: counter,
            PassFail: serialNumber != null ? 1 : null,
            StartTm: new Date(),
            EndTm: new Date(),
            Sn: serialNumber,
            VarData: Math.floor(Math.random() * 100),
            TestSpec: Math.floor(Math.random() * 100),
            Trigger: true,
        };

        counter = counter + 1;

        Tags.push(stationData);

    }

    return ( Tags );

}

// Función para enviar el array mediante una petición POST
async function sendData(data) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const responseData = await response.json();
            console.error('Error: ' + responseData.message);
            return
        }

        const responseData = await response.json();
        console.log('Respuesta del servidor:', responseData.message);
    } catch (error) {
        console.error('Error al enviar la solicitud:', error.message);
    }
}

// Función para generar y enviar los datos cada 4 segundos
function sendDataPeriodically() {

    setInterval(() => {

        counter = 0;

        updateSerialNumbers();
        
        const plc1Data = generatePLCData(1, 9);
        const plc2Data = generatePLCData(2, 6);
        const plc3Data = generatePLCData(3, 14);

        //const tags = plc1Data.concat(plc2Data, plc3Data);
        const PLCs = [{ IP: plc1IP, Tags: plc1Data }, { IP: plc2IP, Tags: plc2Data }, { IP: plc3IP, Tags: plc3Data }];

        const data = {PLCs};

        // Enviar datos del PLC
        sendData(data);

    }, 4000);
}

// Iniciar el envío periódico de datos
sendDataPeriodically();