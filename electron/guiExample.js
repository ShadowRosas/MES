const { exec } = require("child_process");
const nodeConsole = require("console");
const { ipcRenderer } = require("electron");
const fs = require('fs');
const path = require('path');

// Ruta al archivo .log
const stepBackPath = path.resolve(__dirname, '..', 'example.log');

// Imprimir la ruta para verificar
console.log('File path .log:', stepBackPath);

// Función para leer la variable de un archivo .log
function readVariableFromLogFile(variableName) {
  try {
    // Verificar si el archivo existe
    if (!fs.existsSync(stepBackPath)) {
      console.error('The file does not exist in the path:', stepBackPath);
      return null;
    }

    // Leer el contenido del archivo
    const data = fs.readFileSync(stepBackPath, 'utf8');

    // Buscar la línea que contiene la variable
    const regex = new RegExp(`^${variableName}=(.*)$`, 'm');
    const match = data.match(regex);

    if (match && match[1]) {
      return match[1].trim(); // Devolver el valor de la variable
    } else {
      console.log(`Variable ${variableName}  not found in file.`);
      return null;
    }
  } catch (err) {
    console.error('Error reading file:', err);
    return null;
  }
}

const terminalConsole = new nodeConsole.Console(process.stdout, process.stderr);
let child;

ipcRenderer.send("run-command", "ls");
ipcRenderer.on("run-command-result", (event, result) => {
  if (result.error) {
    printBoth("Error: " + result.error);
  } else {
    printBoth("Output: " + result.output);
  }
});

let isBlinking = false;  // Variable para saber si está parpadeando
let intervalId = null;   // Variable para almacenar el ID del intervalo

const printBoth = (str) => {
  console.log(`${str}`);
  terminalConsole.log(`${str}`);
  printToScreen(`${str}`);  // Imprimir en la pantalla

  // Si el mensaje contiene "Error"
  if (str.includes("Error")) {
    // Si no está parpadeando, iniciar el parpadeo
    if (!isBlinking) {
      const body = document.body;
      let isRed = false;
      intervalId = setInterval(() => {
        body.style.backgroundColor = isRed ? "#F4F4F9" : "#FF0000";  // Alterna entre rojo y el color original
        isRed = !isRed;
      }, 500);  // Cambia de color cada 500ms

      // Detener el parpadeo al hacer clic en la pantalla
      const stopBlinking = () => {
        clearInterval(intervalId);  // Detiene el parpadeo
        body.style.backgroundColor = "#F4F4F9";  // Restablece el color original
        isBlinking = false;  // Actualiza el estado
        body.removeEventListener("click", stopBlinking);  // Elimina el evento de clic
      };

      body.addEventListener("click", stopBlinking);  // Agrega el evento de clic
      isBlinking = true;  // Marca que está parpadeando
    }
  } else {
    // Si el mensaje no es un error, detener el parpadeo si está activo
    if (isBlinking) {
      clearInterval(intervalId);  // Detiene el parpadeo
      document.body.style.backgroundColor = "#F4F4F9";  // Restablece el color original
      isBlinking = false;  // Marca que ya no está parpadeando
    }
  }
};


const printToScreen = (str) => {
  const outputDiv = document.getElementById("output");
  const message = document.createElement("p");

  message.textContent = str;

  // Si el mensaje contiene "Error", cambiar el color del texto a rojo
  if (str.includes("Error")) {
    message.style.color = "#FF0000";  // Rojo
    message.style.fontWeight = "bold"; // Opcional: Texto en negrita para mayor énfasis
  }

  // Añadir el mensaje al div
  outputDiv.appendChild(message);

  // Limitar a 100 mensajes en pantalla
  if (outputDiv.childElementCount > 100) {
    outputDiv.removeChild(outputDiv.firstChild);  // Elimina el primer mensaje para mantener solo 5
  }
};

const startCodeFunction = () => {
  // Ocultar el botón
  document.getElementById("start_code").style.display = "none";
  
  // Mostrar el mensaje de "Running program" en la parte superior
  const statusMessage = document.getElementById("status_message");
  statusMessage.textContent = "Running program...";
  statusMessage.style.display = "block";

  printBoth("Initiating program");

  child = exec("python -i ./python/variableSend.py", (error) => {
    if (error) {
      printBoth(`exec error: ${error}`);
    }
  });

  child = exec("python -i ./python/GeneralConditional.py", (error) => {
    if (error) {
      printBoth(`exec error: ${error}`);
    }
  });

  child.stdout.on("data", (data) => {
    printBoth(
      `${data.toString(
        "utf8"
      )}`
    );
  });
};

const sendToProgram = (str) => {
  child.stdin.write(str);
  child.stdout.on("data", (data) => {
  });
};
let variable = "";
const sendCodeFunction = () => {
  const storedLineId = localStorage.getItem('selectedLineId');
  variable = storedLineId;
  console.log("Stored Line ID:", storedLineId);
  sendToProgram(storedLineId);
  child.stdin.end();
};

const sendCodeFunction2 = () => {
  child = exec("python -i ./python/getlines.py", (error) => {
    if (error) {
      printBoth(`exec error: ${error}`);
    }
  });

  child.stdout.on("data", (data) => {
    printBoth(
      `${data.toString(
        "utf8"
      )}`
    );
  });
};

// Function to handle line button clicks
function handleLineClick(lineId) {
  try {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", `http://127.0.0.1:5000/api/get-line-data/${lineId}`, false); // false makes the request synchronous
    xhr.send();

    if (xhr.status === 200) {
      const lineData = JSON.parse(xhr.responseText);
      console.log('Line data:', lineData);

      const htmlContent = `
        <div class="line-data-container">
          ${lineData.map(data => `
            <div class="line-data-box">
              <p><strong>IP:</strong> ${data['IP']}</p>
              <p><strong>Tags:</strong></p>
              <ul>
                ${data['operations'].map(op => `<li>${op}</li>`).join('')}
              </ul>
            </div>
          `).join('')}
        </div>
      `;

      // Display the line data in the output2 div
      const output2 = document.getElementById('output2');
      output2.innerHTML = htmlContent;
    } else {
      console.error('Error fetching line data:', xhr.statusText);
    }
  } catch (error) {
    console.error('Error fetching line data:', error);
  }
}


document.addEventListener("DOMContentLoaded", () => {
  // Añadir listener al botón "start_code"
  document
    .getElementById("start_code")
    .addEventListener("click", () => {
      try {
        startCodeFunction();  // Llama a la función startCodeFunction
        // Ejemplo de uso
        const variableValue = readVariableFromLogFile('VARIABLE_NAME');
        console.log('VARIABLE_NAME:', variableValue);
        handleLineClick(variableValue);
      } catch (error) {
        printBoth("Error: " + error);
      }
    });

// Añadir listener al botón "lineDetails"
const lineDetailsButton = document.getElementById("lineDetails");

// Primer listener para ejecutar sendCodeFunction2
lineDetailsButton.addEventListener("click", sendCodeFunction2);

// Segundo listener para ejecutar sendCodeFunction y ocultar lineDetails
lineDetailsButton.addEventListener("click", () => {
  sendCodeFunction(); // Ejecutar la función

  // Ocultar lineDetails después de ejecutar sendCodeFunction
  const lineDetails = document.getElementById("lineDetails");
  lineDetails.style.display = 'none'; // Ocultar el elemento
});
});


