let lines = [];

    // Function to fetch lines from the server
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
      selectedLineId = line['_id']; // Guarda el ID de la línea en una variable
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

    // Function to handle line button clicks
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

        // Display the line data in the output2 div
        const output2 = document.getElementById('output2');
        output2.innerHTML = htmlContent;
      } catch (error) {
        console.error('Error fetching line data:', error);
      }
    }

    // Event listener for the "Lines" button
    document.getElementById('iniciar_sesion').addEventListener('click', function() {
      console.log('Lines button clicked');
      fetchLines();
    });

    document.addEventListener('DOMContentLoaded', function() {
      const dropdownButton = document.getElementById('iniciar_sesion');
      const dropdownContent = document.getElementById('iniciar_sesion');
    
      dropdownContent.addEventListener('mouseenter', function() {
        dropdownContent.style.display = 'block';
      });
    });

    

    
    
