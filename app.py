from flask import Flask

from routes.categories import categories_bp
from routes.products import products_bp

app = Flask(__name__)

# Registrar módulos de la aplicación
app.register_blueprint(categories_bp)
app.register_blueprint(products_bp)

@app.route('/')
def home():
    return "Sistema de Cafeteria y Reposteria funcionando"

if __name__ == '__main__':
    app.run(debug=True, port=4000)
