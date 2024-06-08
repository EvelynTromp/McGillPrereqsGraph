import dash
import dash_cytoscape as cyto
import networkx as nx
import pandas as pd
import random
from dash import html, dcc, Input, Output, State
#from src.utils.settings import COURSES_CSV

df = pd.read_csv("C:\\Users\\evely\\OneDrive\\Desktop\\Formatted McGill Courses and Prereqs.csv")


print("FFHFHHFFHFHFHFHFHFHFHFH")

# Ensure all data is treated as string and handle missing values
df['Course Code'] = df['Course Code'].astype(str)
df['Prerequisites'] = df['Prerequisites'].astype(str).replace('nan', '')  # Replace NaN with empty string

# Handle multiple prerequisites separated by commas
df['Prerequisites'] = df['Prerequisites'].str.split(', ')
df_exploded = df.explode('Prerequisites')

# Create a directed graph
G = nx.DiGraph()

# Function to extract and label course level
def label_with_level(course_code):
    parts = course_code.split()
    if len(parts) > 1 and parts[1].isdigit():
        level = int(parts[1][0])  # Assuming the level is the first digit of the course number
        return f"lvl {level} - {course_code}"
    return course_code

# Add every course as a node with level labeling
for course in df['Course Code'].unique():
    course_label = label_with_level(course)
    G.add_node(course, label=course_label)  # Set label attribute here

# Adding edges with prerequisites
for index, row in df_exploded.iterrows():
    if row['Prerequisites'].strip():  # Only add edge if there is a prerequisite
        G.add_edge(row['Prerequisites'], row['Course Code'])

# Define a function to generate light colors
def generate_light_color():
    return f"#{random.randint(100, 255):02x}{random.randint(100, 255):02x}{random.randint(100, 255):02x}"

# Determine colors and create cluster nodes
prefix_colors = {}
cluster_elements = []
seen_prefixes = set()
for node in G.nodes():
    node_label = G.nodes[node].get('label', node) 
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

# Sort cluster elements alphabetically by their labels
cluster_elements.sort(key=lambda x: x['data']['label'])

app = dash.Dash(__name__)
app.layout = html.Div([
    html.Button("All Codes", id="reset-button", n_clicks=0),
    html.P("Click on a cluster to view its courses:"),
    cyto.Cytoscape(
        id='cytoscape-graph',
        elements=cluster_elements,
        style={'width': '100%', 'height': '500px'},
        layout={'name': 'grid'},
        stylesheet=[
            {
                'selector': '.cluster',
                'style': {
                    'content': 'data(label)',
                    'text-valign': 'center',
                    'color': 'white',
                    'text-outline-width': 2,
                    'text-outline-color': '#888',
                    'width': '60px',
                    'height': '60px'
                }
            },
            {
                'selector': 'node',
                'style': {
                    'background-color': '#888',
                    'label': 'data(label)',
                    'color': '#000',
                    'text-outline-color': '#fff',
                    'text-outline-width': 1
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'line-color': '#ccc',
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'width': 2,
                }
            }
        ]
    )
])
@app.callback(
    [Output('cytoscape-graph', 'elements'),
     Output('cytoscape-graph', 'layout')],
    [Input('cytoscape-graph', 'tapNodeData'),
     Input('reset-button', 'n_clicks')],
    State('cytoscape-graph', 'elements')
)
def display_cluster_details(node_data, n_clicks, current_elements):
    ctx = dash.callback_context

    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'reset-button':
            return cluster_elements, {'name': 'grid'}

    if node_data:
        prefix = node_data['id']
        if ' ' not in prefix:  # Cluster node click
            nodes_in_cluster = [node for node in G.nodes() if node.startswith(prefix)]
            # Identify all nodes and edges that need to be displayed
            additional_nodes = set(nodes_in_cluster)
            for node in nodes_in_cluster:
                connected_nodes = {edge[1] for edge in G.edges(node)} | {edge[0] for edge in G.in_edges(node)}
                additional_nodes.update(connected_nodes)

            # Create elements for all these nodes
            cluster_nodes = [
                {'data': {'id': node, 'label': G.nodes[node].get('label', node)}, 
                 'style': {'background-color': prefix_colors[node.split(' ')[0]]}}
                for node in additional_nodes
            ]

            # Collect all relevant edges
            cluster_edges = [
                {'data': {'source': edge[0], 'target': edge[1]}}
                for edge in G.edges() if edge[0] in additional_nodes and edge[1] in additional_nodes
            ]

            return cluster_nodes + cluster_edges, {'name': 'cose'}

        else:  # Class node click
            node_id = node_data['id']
            updated_nodes = {
                node_id: {'data': {'id': node_id, 'label': G.nodes[node_id].get('label', node_id)}, 'style': {'background-color': prefix_colors[node_id.split(' ')[0]]}}
            }
            updated_edges = []
            for edge in G.edges(node_id):
                if edge[1] in G.nodes:
                    updated_nodes[edge[1]] = {
                        'data': {'id': edge[1], 'label': G.nodes[edge[1]].get('label', edge[1])},
                        'style': {'background-color': prefix_colors[edge[1].split(' ')[0]]}
                    }
                    updated_edges.append({'data': {'source': node_id, 'target': edge[1]}, 'style': {'line-color': 'red', 'width': 4}})

            updated_node_elements = list(updated_nodes.values())
            return updated_node_elements + updated_edges, {'name': 'cose'}

    return cluster_elements, {'name': 'grid'}


if __name__ == '__main__':
    app.run_server(debug=True)
