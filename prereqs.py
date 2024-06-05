import pandas as pd
import networkx as nx
import dash
from dash import html, Input, Output, State
import dash_cytoscape as cyto
import random

# Load the CSV file
df = pd.read_csv('your_file.csv')

# Handle multiple prerequisites separated by commas
df['Is a Prerequisite for'] = df['Is a Prerequisite for'].str.split(', ')
df_exploded = df.explode('Is a Prerequisite for')

# Create a directed graph
G = nx.DiGraph()

# Add edges based on the prerequisite data
for index, row in df_exploded.iterrows():
    G.add_edge(row['Course Code'], row['Is a Prerequisite for'])

# Define a function to generate light colors
def generate_light_color():
    return f"#{random.randint(100, 255):02x}{random.randint(100, 255):02x}{random.randint(100, 255):02x}"

# Determine colors and create cluster nodes
prefix_colors = {}
cluster_elements = []
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
                    'width': 2
                }
            }
        ]
    )
])

@app.callback(
    Output('cytoscape-graph', 'elements'),
    [Input('cytoscape-graph', 'tapNodeData'),
     Input('reset-button', 'n_clicks')],
    prevent_initial_call=True
)
def display_cluster_details(node_data, n_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        return cluster_elements

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'reset-button':
        return cluster_elements

    if not node_data or ' ' in node_data['id']:
        return cluster_elements

    try:
        prefix = node_data['id']
        detailed_nodes = {
            node: {'data': {'id': node, 'label': node}, 'style': {'background-color': prefix_colors[node.split(' ')[0]]}}
            for node in G.nodes() if node.startswith(prefix) or any(prereq.startswith(prefix) for prereq in G.predecessors(node))
        }
        detailed_edges = [
            {'data': {'source': edge[0], 'target': edge[1]}}
            for edge in G.edges() if edge[0] in detailed_nodes and edge[1] in detailed_nodes
        ]

        return list(detailed_nodes.values()) + detailed_edges + cluster_elements
    except Exception as e:
        print(f"Error: {e}")
        return cluster_elements

if __name__ == '__main__':
    app.run_server(debug=True)
