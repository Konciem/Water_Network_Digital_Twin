from flask import Flask, render_template, request, jsonify
import wntr
from neo4j import GraphDatabase

# Init Flaska
app = Flask(__name__)

# Konfiguracja polaczenia z neo4j
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "twoje_haslo")

# driver = GraphDatabase.driver(URI, auth=AUTH)

@app.route('/')
def index():
    project_name = "Cyfrowy Bliźniak Sieci Wodociągowej"

    # np. network_stats = pobierz_statystyki_sieci()

    return render_template('index.html', title=project_name)

if __name__ == '__main__':
    # Uruchomienie serwera w trybie debug automatycznie odswiezanie kodu po zmianach
    app.run(debug=True)