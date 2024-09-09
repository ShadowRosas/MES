import sys

# FUNCTIONS
def write_variable_to_log(file_path, variable_name, value):
    # Leer el contenido actual del archivo
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Sobrescribir la variable si ya existe o añadirla si no existe
    with open(file_path, 'w') as file:
        variable_written = False
        for line in lines:
            if line.startswith(f'{variable_name}='):
                file.write(f'{variable_name}={value}\n')
                variable_written = True
            else:
                file.write(line)
        
        # Si la variable no se encontró, añadirla al final
        if not variable_written:
            file.write(f'{variable_name}={value}\n')
    
    print("Line changed to:", value, flush=True)

def read_variable_from_log(file_path, variable_name):
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith(f'{variable_name}='):
                # Extraer y devolver el valor después del '='
                return line.split('=', 1)[1].strip()
    return None  # Devuelve None si la variable no se encuentra

# Archivo y variable
file_path = 'example.log'  # Cambia esto por la ruta de tu archivo .log
variable_name = 'VARIABLE_NAME'

# Leer la variable desde el archivo
value = read_variable_from_log(file_path, variable_name)

# Mostrar el valor obtenido o pedir un nuevo valor
if value:  # Esto evalúa si 'value' no es None ni una cadena vacía
    print(f'The value of the line is: {value}')
else:
    line = sys.stdin.readline().strip()
    write_variable_to_log(file_path, variable_name, line)





