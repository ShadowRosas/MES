document.addEventListener('DOMContentLoaded', () => {
    const openModalBtn = document.getElementById('lineSwitcher');
    const openModalBtn2 = document.getElementById('lineDetails');
    const modal = document.getElementById('authModal');
    const closeModal = document.querySelector('.close');
    const authForm = document.getElementById('authForm');
    const errorElem = document.getElementById('error');
    let isAuthenticated = false; // Bandera para verificar autenticación

    // Función para abrir el modal
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
    });

    // Función para manejar el envío del formulario
    authForm.addEventListener('submit', (event) => {
        event.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        // Aquí puedes definir las credenciales válidas
        const validUsername = '123';
        const validPassword = '123';

        if (username === validUsername && password === validPassword) {
            isAuthenticated = true; // Usuario autenticado
            modal.style.display = 'none';
        } else {
            errorElem.style.display = 'block';
        }
    });

    // Cerrar el modal si el usuario hace clic fuera de él
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    };
});
