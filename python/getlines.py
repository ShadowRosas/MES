import sys

# Nombre del archivo
archivo = 'example.log'

# Leer la línea enviada desde Electron
line = sys.stdin.readline().strip()
print(f"Received line: {line}")

# Nombre de la variable y el nuevo valor
nombre_variable = 'VARIABLE_NAME'
nuevo_valor = line  # Usa el valor recibido en lugar de un valor fijo

# Leer el contenido actual del archivo
with open(archivo, 'r') as f:
    lineas = f.readlines()

# Abrir el archivo en modo de escritura
with open(archivo, 'w') as f:
    for linea in lineas:
        # Comprobar si la línea contiene la variable
        if linea.startswith(f"{nombre_variable}="):
            # Reescribir la línea con el nuevo valor
            f.write(f"{nombre_variable}={nuevo_valor}\n")
        else:
            # Escribir la línea original si no es la variable objetivo
            f.write(linea)

print(f"Line has been updated to '{nuevo_valor}' in '{archivo}'.")
