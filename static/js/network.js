// Suwak czasu
var slider = document.getElementById('time-slider');
if (slider) {
    slider.addEventListener('change', function() {
        window.location.href = "/?step=" + this.value;
    });
}

// Inicjalizacja Vis.js grafu mapy
var container = document.getElementById('mapa-sieci');
var data = {
    nodes: new vis.DataSet(graphData.nodes),
    edges: new vis.DataSet(graphData.edges)
};

var options = {
    nodes: { 
        shape: 'dot', 
        font: { size: 13, face: 'Arial' } 
    },
    edges: { 
        arrows: 'to', 
        font: { size: 9, align: 'top' },
        color: { color: '#cccccc', highlight: '#0d6efd' }
    },
    physics: { enabled: false }
};
var network = new vis.Network(container, data, options);

// Reakcja na kliknięcie grafu
network.on("click", function(params) {
    if (params.nodes.length > 0) {
        showNodeDetails(params.nodes[0]);
    }
});

// Wypełnianie kafelka detali danymi telemetrycznymi
function showNodeDetails(nodeName) {
    var matchedObject = graphData.table_data.find(function(item) {
        return item.name === nodeName;
    });

    if (matchedObject) {
        document.getElementById('det-name').innerText = matchedObject.name;
        document.getElementById('det-type').innerText = matchedObject.type === "Reservoir" ? "Reservoir (Źródło)" : "Junction (Węzeł)";
        document.getElementById('det-coords').innerText = "(" + matchedObject.x + ", " + matchedObject.y + ")";
        document.getElementById('det-connections').innerText = matchedObject.connections;
        
        document.getElementById('det-pressure').innerText = matchedObject.pressure;
        document.getElementById('det-demand').innerText = matchedObject.demand;
        document.getElementById('det-head').innerText = matchedObject.head;
        document.getElementById('det-quality').innerText = matchedObject.quality;

        document.getElementById('detail-panel').style.display = 'block';
    }
}

// Wybór wiersza z tabeli
function selectNodeFromTable(nodeName) {
    network.selectNodes([nodeName]);
    showNodeDetails(nodeName);
}