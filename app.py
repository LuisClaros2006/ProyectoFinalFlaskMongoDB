from flask import Flask
import database as dbase

app = Flask(__name__)

db = dbase.dbConnection()

@app.route('/')
def home():
    return "Sistema de Cafeteria y Reposteria funcionando"

if __name__ == '__main__':
    app.run(debug=True, port=4000)
