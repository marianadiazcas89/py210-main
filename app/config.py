import os
from dotenv import load_dotenv

# Carga las variables definidas en el archivo .env
load_dotenv()

# Obtiene la URI desde la variable de entorno; si no se encuentra, utiliza un valor por defecto.
MONGO_URI = os.getenv("MONGO_URI")

