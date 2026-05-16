# Crear entorno virtual en .venv
python3 -m venv .venv

# Activar entorno virtual (solo para instrucciones, no ejecutable en script)
./.venv/Scripts/activate

# Actualizar pip e instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
