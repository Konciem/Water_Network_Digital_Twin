from flask import Flask, render_template, jsonify
from neo4j import GraphDatabase
from network_model import create_network

app = Flask(__name__)

# --- KONFIGURACJA NEO4J ---
URI = "neo4j+s://8b7b73ab.databases.neo4j.io"
USER = "8b7b73ab"
PASSWORD = "1W3sAH8HRpTKTQn9obDqaozoquQuau23v_BIIruH6VY"

def upload_to_neo4j(wn):
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    with driver.session() as session:
        # Czyścimy bazę
        session.run("MATCH (n) DETACH DELETE n")
        
        # Import węzłów
        for node_name, node in wn.nodes():
            x, y = node.coordinates
            session.run("""
                CREATE (n:Node {name: $name, x: $x, y: $y, type: $type})
            """, name=node_name, x=float(x), y=float(y), type=str(type(node).__name__))
            
        # Import rur
        for pipe_name, pipe in wn.pipes():
            session.run("""
                MATCH (a:Node {name: $start}), (b:Node {name: $end})
                CREATE (a)-[:PIPE {name: $p_name, diameter: $diam}]->(b)
            """, start=pipe.start_node_name, end=pipe.end_node_name, 
                 p_name=pipe_name, diam=pipe.diameter)
    driver.close()

@app.route('/')
def index():
    wn, results = create_network()
    
    # Przesyłamy sieć do bazy przy każdym odświeżeniu (lub raz na starcie)
    try:
        upload_to_neo4j(wn)
        db_status = "Połączono z Neo4j AuraDB"
    except:
        db_status = "Błąd połączenia z bazą"

    # Wyciągamy ciśnienie z Dom_A
    p_a = results.node['pressure'].loc[3600, 'Dom_A']
    
    # Renderujemy szablon i przekazujemy dane
    return render_template('index.html', 
                           status=db_status, 
                           pressure=round(p_a, 2))

if __name__ == '__main__':
    app.run(debug=True)