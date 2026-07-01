from neo4j import GraphDatabase

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