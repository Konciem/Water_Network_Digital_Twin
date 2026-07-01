from flask import Flask, render_template, request
from network_model import create_network
# Importujemy funkcje z naszego nowego modułu bazodanowego
from database import upload_to_neo4j, get_graph_for_frontend

app = Flask(__name__)

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