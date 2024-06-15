import dash
import dash_cytoscape as cyto
import networkx as nx
import pandas as pd
import random
from dash import html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
from src.utils.settings import COURSES_CSV

def load_course_data(filepath):
    """Load course data from CSV, process and return the DataFrame."""
    df = pd.read_csv(filepath)
    df['Course Code'] = df['Course Code'].astype(str).str.strip()
    df['Prerequisites'] = df['Prerequisites'].astype(str).replace('nan', '').str.split(', ').apply(lambda x: [prereq.strip() for prereq in x])
    return df.explode('Prerequisites')

def create_course_graph(df):
    """Create and return a directed graph from the course data."""
    G = nx.DiGraph()

    # Add all nodes first
    for course in df['Course Code'].unique():
        G.add_node(course, label=label_with_level(course), level=course_level(course))

    # Add edges
    for _, row in df.iterrows():
        if row['Prerequisites']:
            G.add_edge(row['Prerequisites'], row['Course Code'])
    
    return G

def course_level(course_code):
    """Extract and return the level of the course based on its code."""
    parts = course_code.split()
    return int(parts[1][0]) if len(parts) > 1 and parts[1][0].isdigit() else 0

def label_with_level(course_code):
    """Return the course code with a level prefix and indicate if not offered."""
    not_offered = course_code.startswith('*')
    if not_offered:
        course_code = course_code[1:]  # Remove the asterisk

    level = course_level(course_code)
    level_label = f"lvl {level} - {course_code}" if level else course_code
    return f"{level_label} (not offered)" if not_offered else level_label

def generate_light_color():
    """Generate and return a light color in hex format."""
    return f"#{random.randint(100, 255):02x}{random.randint(100, 255):02x}{random.randint(100, 255):02x}"

app = dash.Dash(__name__)
df = load_course_data(COURSES_CSV)
G = create_course_graph(df)

prefix_colors, cluster_elements = {}, []
seen_prefixes = set()

for node in G.nodes():
    prefix = node.split(' ')[0].lstrip('*')
    if prefix not in prefix_colors:
        prefix_colors[prefix] = generate_light_color()
    if prefix not in seen_prefixes:
        cluster_elements.append({'data': {'id': prefix, 'label': prefix}, 'classes': 'cluster', 'style': {'background-color': prefix_colors[prefix]}})
        seen_prefixes.add(prefix)
cluster_elements.sort(key=lambda x: x['data']['label'])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Button("Back", id="back-button", n_clicks=0),
    html.Button("All Codes", id="reset-button", n_clicks=0),
    html.P("Click on a cluster to view its courses:"),
    cyto.Cytoscape(
        id='cytoscape-graph', 
        elements=cluster_elements, 
        style={'width': '100%', 'height': '500px'}, 
        layout={'name': 'preset'}, 
        stylesheet=[
            {'selector': '.cluster', 'style': {'content': 'data(label)', 'text-valign': 'center', 'color': 'white', 'text-outline-width': 2, 'text-outline-color': '#888', 'width': '60px', 'height': '60px'}},
            {'selector': 'node', 'style': {'shape': 'rectangle', 'background-color': '#888', 'label': 'data(label)', 'color': '#000', 'text-outline-color': '#fff', 'text-outline-width': 1, 'text-valign': 'center', 'width': 'mapData(width, 5, 15)', 'height': '50px'}},
            {'selector': 'edge', 'style': {'line-color': '#ccc', 'curve-style': 'bezier', 'target-arrow-shape': 'triangle', 'width': 2}}
        ]
    )
])

@app.callback(
    Output('url', 'pathname'),
    Input('back-button', 'n_clicks'),
    State('url', 'pathname')
)
def go_back(n_clicks, pathname):
    if n_clicks > 0:
        return '/'
    raise PreventUpdate

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
        node_id = node_data['id']
        print(f"Node clicked: {node_id}")  # Debugging
        
        if node_id in seen_prefixes:
            return update_cluster_view(node_id), {'name': 'preset'}
        
        elif ' ' in node_id:
            return update_class_view(node_id), {'name': 'preset'}
        
    return cluster_elements, {'name': 'grid'}
def update_cluster_view(prefix):
    """Update and return cluster elements based on selected cluster prefix."""
    nodes_in_cluster = [node for node in G.nodes() if node.startswith(prefix)]
    
    additional_nodes = set(nodes_in_cluster)
    for node in nodes_in_cluster:
        additional_nodes.update(G.successors(node))
        additional_nodes.update(G.predecessors(node))
    
    cluster_nodes = []
    other_nodes = []
    level_nodes = {level: [] for level in range(10)}
    
    for node in additional_nodes:
        node_data = {'data': {'id': node, 'label': label_with_level(node)},
                     'style': {'background-color': prefix_colors[node.split(' ')[0].lstrip('*')],
                               'width': len(label_with_level(node)) * 5 + 10,
                               'height': '50px'}}
        
        if node.lstrip('*').startswith(prefix):
            level = course_level(node)
            level_nodes[level].append(node_data)
        else:
            other_nodes.append(node_data)
    
    # Find the maximum level that has nodes
    max_level = max([level for level in level_nodes if level_nodes[level]], default=0)
    
    position = {'x': 0, 'y': 0}
    x_increment = 300  # Increased spacing for columns
    y_increment = 120  # Increased spacing for rows
    max_per_col = 10
    
    # Keeps track of how many levels required more than 1 column
    spillover_levels = 0
    for level in range(10):
        if level_nodes[level]:
            spillover = 0

            for i, node_data in enumerate(level_nodes[level]):
                # Add any spillover to the current spillover amount
                spillover = i // max_per_col

                node_data['position'] = {'x': position['x'] + ((level + spillover_levels) * x_increment) + (i // max_per_col) * x_increment, 'y': position['y'] + (i % max_per_col) * y_increment}
            cluster_nodes.extend(level_nodes[level])
            
            spillover_levels += spillover
            
    # Position other nodes in the far right column
    right_column_x = position['x'] + ((max_level + spillover_levels + 1) * x_increment)
    for i, node_data in enumerate(other_nodes):
        node_data['position'] = {'x': right_column_x + (i // max_per_col) * x_increment, 'y': position['y'] + (i % max_per_col) * y_increment}
    cluster_nodes.extend(other_nodes)
    
    cluster_edges = [{'data': {'source': edge[0], 'target': edge[1]}}
                     for edge in G.edges() if edge[0] in additional_nodes and edge[1] in additional_nodes]
    
    cluster_nodes.sort(key=lambda x: (course_level(x['data']['id']), x['data']['label']))
    
    return cluster_nodes + cluster_edges

def update_class_view(node_id):
    connected_nodes = set()
    for edge in G.edges(node_id):
        connected_nodes.update(edge)
    connected_nodes.add(node_id)

    class_nodes = [{'data': {'id': node, 'label': label_with_level(node)}, 'style': {'background-color': prefix_colors[node.split(' ')[0].lstrip('*')], 'width': len(label_with_level(node)) * 5 + 10, 'height': '50px'}} for node in connected_nodes]
    class_edges = [{'data': {'source': edge[0], 'target': edge[1]}} for edge in G.edges() if edge[0] in connected_nodes and edge[1] in connected_nodes]
    class_nodes.sort(key=lambda x: (course_level(x['data']['id']), x['data']['label']))
    
    position = {'x': 0, 'y': 0}
    x_increment = 300  # Increased spacing for columns
    y_increment = 120  # Increased spacing for rows
    max_per_col = 10
    for i, node_data in enumerate(class_nodes):
        node_data['position'] = {'x': position['x'] + (course_level(node_data['data']['id']) * x_increment) + (i // max_per_col) * x_increment, 'y': position['y'] + (i % max_per_col) * y_increment}
    
    return class_nodes + class_edges

if __name__ == '__main__':
    app.run_server(debug=True)
