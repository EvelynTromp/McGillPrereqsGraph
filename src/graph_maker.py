import dash
import dash_cytoscape as cyto
import networkx as nx
import pandas as pd
import random
from dash import html, dcc, Input, Output, State

# Load and process course data
def load_course_data(filepath):
    df = pd.read_csv(filepath)
    df['Course Code'] = df['Course Code'].astype(str)
    df['Prerequisites'] = df['Prerequisites'].astype(str).replace('nan', '')
    df['Prerequisites'] = df['Prerequisites'].str.split(', ')
    return df.explode('Prerequisites')

# Create a directed graph from the data
def create_course_graph(df):
    G = nx.DiGraph()
    for course in df['Course Code'].unique():
        G.add_node(course, label=label_with_level(course))
    for _, row in df.iterrows():
        if row['Prerequisites'].strip():
            G.add_edge(row['Prerequisites'], row['Course Code'])
    return G

# Label course with its level
def label_with_level(course_code):
    parts = course_code.split()
    return f"lvl {parts[1][0]} - {course_code}" if len(parts) > 1 and parts[1].isdigit() else course_code

# Function to generate light colors
def generate_light_color():
    return f"#{random.randint(100, 255):02x}{random.randint(100, 255):02x}{random.randint(100, 255):02x}"

# Application initialization
app = dash.Dash(__name__)
df = load_course_data("C:\\Users\\evely\\OneDrive\\Desktop\\Formatted McGill Courses and Prereqs.csv")
G = create_course_graph(df)

# Assign colors and prepare clusters
prefix_colors, cluster_elements = {}, []
seen_prefixes = set()
for node in G.nodes():
    prefix = node.split(' ')[0]
    if prefix not in prefix_colors:
        prefix_colors[prefix] = generate_light_color()
    if prefix not in seen_prefixes:
        cluster_elements.append({
            'data': {'id': prefix, 'label': prefix},
            'classes': 'cluster',
            'style': {'background-color': prefix_colors[prefix]}
        })
        seen_prefixes.add(prefix)

cluster_elements.sort(key=lambda x: x['data']['label'])  # Sort clusters alphabetically by label

# Define the application layout
app.layout = html.Div([
    html.Button("All Codes", id="reset-button", n_clicks=0),
    html.P("Click on a cluster to view its courses:"),
    cyto.Cytoscape(
        id='cytoscape-graph',
        elements=cluster_elements,
        style={'width': '100%', 'height': '500px'},
        layout={'name': 'grid'},
        stylesheet=[
            {'selector': '.cluster', 'style': {'content': 'data(label)', 'text-valign': 'center', 'color': 'white', 'text-outline-width': 2, 'text-outline-color': '#888', 'width': '60px', 'height': '60px'}},
            {'selector': 'node', 'style': {'background-color': '#888', 'label': 'data(label)', 'color': '#000', 'text-outline-color': '#fff', 'text-outline-width': 1}},
            {'selector': 'edge', 'style': {'line-color': '#ccc', 'curve-style': 'bezier', 'target-arrow-shape': 'triangle', 'width': 2}}
        ]
    )
])

# Callback to handle node and reset button interactions
@app.callback(
    [Output('cytoscape-graph', 'elements'), Output('cytoscape-graph', 'layout')],
    [Input('cytoscape-graph', 'tapNodeData'), Input('reset-button', 'n_clicks')],
    State('cytoscape-graph', 'elements')
)
def display_cluster_details(node_data, n_clicks, current_elements):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    if trigger_id == 'reset-button':
        return cluster_elements, {'name': 'grid'}
    elif node_data:
        prefix = node_data['id']
        if ' ' not in prefix:  # Handle cluster node click
            return update_cluster_view(prefix), {'name': 'cose'}
        else:  # Handle individual class node click
            return update_class_view(node_data['id']), {'name': 'cose'}
    return cluster_elements, {'name': 'grid'}
    

def update_cluster_view(prefix):
    # Extract nodes and edges for the clicked cluster
    nodes_in_cluster = [node for node in G.nodes() if node.startswith(prefix)]
    additional_nodes = set(nodes_in_cluster)
    for node in nodes_in_cluster:
        additional_nodes.update(G.neighbors(node))
        additional_nodes.update(G.predecessors(node))
    
    # Using get with a default value to avoid KeyError
    cluster_nodes = [{'data': {'id': node, 'label': G.nodes[node].get('label', node)}, 'style': {'background-color': prefix_colors[node.split(' ')[0]]}} for node in additional_nodes]
    cluster_edges = [{'data': {'source': edge[0], 'target': edge[1]}} for edge in G.edges() if edge[0] in additional_nodes and edge[1] in additional_nodes]
    return cluster_nodes + cluster_edges

def update_class_view(node_id):
    # Extract nodes and edges for the clicked class node
    connected_nodes = {edge[1] for edge in G.edges(node_id)} | {edge[0] for edge in G.in_edges(node_id)}
    connected_nodes.add(node_id)
    # Using get with a default value to avoid KeyError
    class_nodes = [{'data': {'id': node, 'label': G.nodes[node].get('label', node)}, 'style': {'background-color': prefix_colors[node.split(' ')[0]]}} for node in connected_nodes]
    class_edges = [{'data': {'source': edge[0], 'target': edge[1]}} for edge in G.edges() if edge[0] in connected_nodes and edge[1] in connected_nodes]
    return class_nodes + class_edges

if __name__ == '__main__':
    app.run_server(debug=True)
