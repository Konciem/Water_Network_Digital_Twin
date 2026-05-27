from flask import Flask, render_template, request
from neo4j import GraphDatabase
from network_model import create_network

app = Flask(__name__)

# --- KONFIGURACJA NEO4J ---
URI = "neo4j://127.0.0.1:7687"
USER = "neo4j"
PASSWORD = "haslohaslo"

def upload_data_transaction(tx, wn):
    tx.run("MATCH (n) DETACH DELETE n")
    for node_name, node in wn.nodes():
        x, y = node.coordinates
        tx.run("CREATE (n:Node {name: $name, x: $x, y: $y, type: $type})", 
               name=node_name, x=float(x), y=float(y), type=str(type(node).__name__))
    for pipe_name, pipe in wn.pipes():
        tx.run("""
            MATCH (a:Node {name: $start}), (b:Node {name: $end})
            CREATE (a)-[:PIPE {name: $p_name, diameter: $diam}]->(b)
        """, start=pipe.start_node_name, end=pipe.end_node_name, p_name=pipe_name, diam=pipe.diameter)

def upload_to_neo4j(wn):
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    with driver.session() as session:
        session.execute_write(upload_data_transaction, wn)
    driver.close()

def get_graph_for_frontend():
    nodes = []
    edges = []
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    with driver.session() as session:
        result_relations = session.run("MATCH (n:Node)-[r:PIPE]->(m:Node) RETURN n, r, m")
        node_ids = set()
        for record in result_relations:
            n = record["n"]
            m = record["m"]
            r = record["r"]
            if n["name"] not in node_ids:
                color = "red" if n["type"] == "Reservoir" else "blue"
                nodes.append({"id": n["name"], "label": n["name"], "x": n["x"] * 50, "y": -n["y"] * 50, "color": color, "size": 20})
                node_ids.add(n["name"])
            if m["name"] not in node_ids:
                color = "red" if m["type"] == "Reservoir" else "blue"
                nodes.append({"id": m["name"], "label": m["name"], "x": m["x"] * 50, "y": -m["y"] * 50, "color": color, "size": 20})
                node_ids.add(m["name"])
            edges.append({"from": n["name"], "to": m["name"], "label": r["name"], "width": 2})

        result_nodes = session.run("""
            MATCH (n:Node)
            OPTIONAL MATCH (n)-[out:PIPE]->(next:Node)
            OPTIONAL MATCH (prev:Node)-[inc:PIPE]->(n)
            RETURN n.name AS name, 
                   n.type AS type, 
                   n.x AS x, 
                   n.y AS y,
                   collect(distinct next.name) + collect(distinct prev.name) AS connected_nodes,
                   collect(distinct out.name) + collect(distinct inc.name) AS connected_pipes
        """)
        table_data = []
        for record in result_nodes:
            connections = ", ".join(record["connected_nodes"]) + " (rury: " + ", ".join(record["connected_pipes"]) + ")"
            table_data.append({
                "name": record["name"],
                "type": record["type"],
                "x": round(record["x"], 1),
                "y": round(record["y"], 1),
                "connections": connections
            })
    driver.close()
    return {"nodes": nodes, "edges": edges, "table_data": table_data}

def seconds_to_time_string(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours:02d}:{minutes:02d}"

@app.route('/')
def index():
    _, results = create_network()
    step_index = request.args.get('step', default=0, type=int)
    raw_seconds_list = list(results.node['pressure'].index)
    
    if step_index < 0 or step_index >= len(raw_seconds_list):
        step_index = 0
        
    time_seconds = raw_seconds_list[step_index]
    readable_times_list = [seconds_to_time_string(s) for s in raw_seconds_list]
    current_time_str = readable_times_list[step_index]

    try:
        graph_data = get_graph_for_frontend()
        db_status = "Polaczono z Neo4j"
    except Exception as e:
        db_status = "Brak polaczenia"
        graph_data = {"nodes": [], "edges": [], "table_data": []}

    try:
        pressures_dict = results.node['pressure'].loc[time_seconds].to_dict()
        demands_dict = results.node['demand'].loc[time_seconds].to_dict()
        heads_dict = results.node['head'].loc[time_seconds].to_dict()
        quality_dict = results.node['quality'].loc[time_seconds].to_dict() if 'quality' in results.node else {}
    except Exception as e:
        pressures_dict, demands_dict, heads_dict, quality_dict = {}, {}, {}, {}

    for row in graph_data.get("table_data", []):
        node_name = row["name"]
        row["pressure"] = round(pressures_dict.get(node_name, 0.0), 2)
        row["demand"] = round(demands_dict.get(node_name, 0.0) * 1000, 3)
        row["head"] = round(heads_dict.get(node_name, 0.0), 2)
        row["quality"] = round(quality_dict.get(node_name, 0.0) / 3600, 1)
    
    return render_template('index.html', 
                           status=db_status, 
                           graph_data=graph_data,
                           current_time_str=current_time_str,
                           step_index=step_index,
                           available_times=readable_times_list)

if __name__ == '__main__':
    wn, _ = create_network()
    try:
        upload_to_neo4j(wn)
    except:
        print("Blad bazy")
    app.run(debug=True, use_reloader=False)