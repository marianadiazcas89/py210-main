from flask import Flask
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Importar el blueprint de rutas
    from app.routes.main_routes import main_bp
    app.register_blueprint(main_bp)

    return app

# Instancia la aplicación
app = create_app()

if __name__ == '__main__':
    # Ejecutar en modo desarrollo
    app.run(host='0.0.0.0', port=5000, debug=True)

