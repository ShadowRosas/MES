let lines = [];
let isAuthenticated = false; // Bandera para verificar autenticación

document.addEventListener('DOMContentLoaded', () => {
  const openModalBtn = document.getElementById('lineSwitcher');
  const openModalBtn2 = document.getElementById('lineDetails');
  const modal = document.getElementById('authModal');
  const closeModal = document.querySelector('.close');
  const authForm = document.getElementById('authForm');
  const errorElem = document.getElementById('error');

  // Función para abrir el modal si no está autenticado
  function openModal() {
    if (!isAuthenticated) {
      modal.style.display = 'block';
    }
  }

  // Asignar la función openModal a ambos botones
  openModalBtn.addEventListener('click', openModal);
  openModalBtn2.addEventListener('click', openModal);

  // Función para cerrar el modal
  closeModal.addEventListener('click', () => {
    modal.style.display = 'none';
    errorElem.style.display = 'none'; // Ocultar mensaje de error al cerrar el modal
  });

  // Función para manejar el envío del formulario de autenticación
  authForm.addEventListener('submit', (event) => {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Credenciales válidas
    const validUsername = '123';
    const validPassword = '123';

    if (username === validUsername && password === validPassword) {
      isAuthenticated = true; // Usuario autenticado
      modal.style.display = 'none'; // Cerrar modal
      errorElem.style.display = 'none'; // Ocultar mensaje de error
      fetchLines(); // Cargar líneas después de autenticarse
    } else {
      errorElem.style.display = 'block'; // Mostrar mensaje de error si las credenciales no son válidas
    }
  });

  // Cerrar el modal si el usuario hace clic fuera de él
  window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = 'none';
      errorElem.style.display = 'none'; // Ocultar mensaje de error al hacer clic fuera del modal
    }
  };
});

// Función para obtener las líneas del servidor
async function fetchLines() {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/get-lines');
    lines = await response.json();
    displayLines();
  } catch (error) {
    console.error('Error fetching lines:', error);
  }
}

// Función para mostrar las líneas como botones en el dropdown
function displayLines() {
  const lineDetails = document.getElementById('lineDetails');
  lineDetails.innerHTML = ''; // Limpia el contenido previo

  lines.forEach(line => {
    const button = document.createElement('button');
    button.textContent = line['name'];
    button.onclick = () => {
      handleLineClick(line['_id']);
      const selectedLineId = line['_id']; // Guarda el ID de la línea
      console.log("Variable save", selectedLineId);

      // Guarda en localStorage
      localStorage.setItem('selectedLineId', selectedLineId);
    };
    lineDetails.appendChild(button);
  });

  // Muestra el contenido del dropdown después de cargar las líneas
  const dropdownContent = document.getElementById('lineDetails');
  dropdownContent.style.display = 'block';
}

// Función para manejar clics en los botones de líneas
async function handleLineClick(lineId) {
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/get-line-data/${lineId}`);
    const lineData = await response.json();
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

    // Mostrar los datos de la línea en el div output2
    const output2 = document.getElementById('output2');
    output2.innerHTML = htmlContent;
  } catch (error) {
    console.error('Error fetching line data:', error);
  }
}

// Listener para el botón de inicio de sesión
document.getElementById('iniciar_sesion').addEventListener('click', function() {
  const errorElem = document.getElementById('error');

  if (isAuthenticated) { // Si está autenticado, obtener las líneas
    fetchLines();
    modal.style.display = 'none';
  } else {
    errorElem.style.display = 'block'; // Mostrar mensaje de error si no está autenticado
  }
});

// Listener para mostrar el dropdown
document.addEventListener('DOMContentLoaded', function() {
  const dropdownContent = document.getElementById('iniciar_sesion');
  
  dropdownContent.addEventListener('mouseenter', function() {
    dropdownContent.style.display = 'block';
  });
});

    
    
