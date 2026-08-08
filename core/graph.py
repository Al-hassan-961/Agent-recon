import networkx as nx
import json

def add_relation(graph_data, source, relation, target):
    graph_data.append((source, relation, target))

def generate_graph(graph_data, target):
    G = nx.DiGraph()
    for s, r, t in graph_data:
        G.add_node(s)
        G.add_node(t)
        G.add_edge(s, t, label=r)
    # Create HTML with vis.js
    nodes = []
    edges = []
    for i, n in enumerate(G.nodes):
        nodes.append({"id": i, "label": str(n), "title": str(n)})
    for u, v, d in G.edges(data=True):
        edges.append({"from": list(G.nodes).index(u), "to": list(G.nodes).index(v), "label": d.get("label","")})
    html = f"""
    <html><head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
    <style> #graph {{ width: 100%; height: 800px; border: 1px solid lightgray; }} </style>
    </head><body>
    <h2>OSINT Graph for {target}</h2>
    <div id="graph"></div>
    <script>
    var nodes = new vis.DataSet({json.dumps(nodes)});
    var edges = new vis.DataSet({json.dumps(edges)});
    var container = document.getElementById('graph');
    var data = {{nodes: nodes, edges: edges}};
    var options = {{layout: {{hierarchical: {{direction: "UD"}}}}, physics: false}};
    var network = new vis.Network(container, data, options);
    </script>
    </body></html>
    """
    return html
