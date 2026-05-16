import os
import sys
import requests
from google import genai

# Uso: python gemini_batch.py <API_URL> <prompt_base.txt> <input.txt> <n_lineas> <output.txt>

def main():
    if len(sys.argv) < 5:
        print("Uso: python gemini_batch.py <prompt_base.txt> <input.txt> <n_lineas> <output.txt> [linea_inicial]")
        sys.exit(1)

    prompt_base_path = sys.argv[1]
    input_path = sys.argv[2]
    n_lines = int(sys.argv[3])
    output_path = sys.argv[4]
    linea_inicial = int(sys.argv[5]) if len(sys.argv) > 5 else 1

    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        print('Falta la variable de entorno GEMINI_API_KEY en el .env')
        sys.exit(1)
    
    client = genai.Client(api_key=GEMINI_API_KEY)


    with open(prompt_base_path, 'r', encoding='utf-8') as f:
        prompt_base = f.read()
    with open(input_path, 'r', encoding='utf-8') as f:
        input_lines = f.read().splitlines()
    # Ajustar el rango de líneas a procesar
    input_lines = input_lines[linea_inicial-1:]

    output_mode = 'a'
    if os.path.exists(output_path):
        print(f"El fichero de salida '{output_path}' ya existe.")
        while True:
            resp = input("¿Quieres recrearlo de cero (r) o continuar añadiendo líneas (c)? [r/c]: ").strip().lower()
            if resp == 'r':
                output_mode = 'w'
                break
            elif resp == 'c':
                output_mode = 'a'
                break
            else:
                print("Por favor, responde 'r' para recrear o 'c' para continuar.")

    with open(output_path, output_mode, encoding='utf-8') as out:


        for i in range(0, len(input_lines), n_lines):
            block = '\n'.join(input_lines[i:i+n_lines])
            prompt = f"{prompt_base}\n{block}"
            print(f"Procesando líneas {i+linea_inicial} a {min(i+n_lines+linea_inicial-1, len(input_lines)+linea_inicial-1)}...")
            result = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )

            out.write(result.text + '\n')
            # ask for user input to continue
            input("Presiona Enter para continuar con el siguiente bloque...")

    print('Procesamiento completado.')

if __name__ == "__main__":
    main()
