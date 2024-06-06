import pandas as pd
import networkx as nx
import dash
from dash import html, dcc, Input, Output, State
import dash_cytoscape as cyto
import random

# Load the CSV file
df = pd.read_csv("C:\\Users\\evely\\OneDrive\\Desktop\\Formatted McGill Courses and Prereqs.csv")

# Ensure all data is treated as string and handle missing values
df['Course Code'] = df['Course Code'].astype(str)
df['Prerequisites'] = df['Prerequisites'].astype(str).replace('nan', '')  # Replace NaN with empty string

# Handle multiple prerequisites separated by commas
df['Prerequisites'] = df['Prerequisites'].str.split(', ')
df_exploded = df.explode('Prerequisites')

# Create a directed graph
G = nx.DiGraph()

# Assuming df_exploded is your DataFrame with courses and their prerequisites
for index, row in df_exploded.iterrows():
    if row['Prerequisites'].strip():  # Only add edge if there is a prerequisite
        # Reverse the direction here by switching the order of addition
        G.add_edge(row['Prerequisites'], row['Course Code'])

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
                'style': {                    'content': 'data(label)',
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
    Output('cytoscape-graph', 'elements'),
    Output('cytoscape-graph', 'layout'),
    [Input('cytoscape-graph', 'tapNodeData'),
     Input('reset-button', 'n_clicks')],
    State('cytoscape-graph', 'elements')
)
def display_cluster_details(node_data, n_clicks, current_elements):
    ctx = dash.callback_context

    # Check what triggered the callback
    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Reset the graph to initial state if the reset button was clicked
        if trigger_id == 'reset-button':
            return cluster_elements, {'name': 'grid'}  # Return elements with 'grid' layout

    if node_data:
        prefix = node_data['id']
        if ' ' not in prefix:  # Cluster node click
            cluster_nodes = [
                {'data': {'id': node, 'label': node}, 'style': {'background-color': prefix_colors[node.split(' ')[0]]}}
                for node in G.nodes() if node.startswith(prefix)
            ]
            # Since the graph now inherently has the correct direction, adjust the cluster_edges definition
            cluster_edges = [
                {'data': {'source': edge[0], 'target': edge[1]}}  # Use direct edge data without reversing
                for edge in G.edges() if edge[0].startswith(prefix)
            ]

            # Additional nodes connected to the nodes in the cluster
            additional_nodes = []
            for edge in G.edges():
                if edge[0] in [node['data']['id'] for node in cluster_nodes] or edge[1] in [node['data']['id'] for node in cluster_nodes]:
                    additional_nodes.extend([edge[0], edge[1]])
            additional_nodes = set(additional_nodes) - set([node['data']['id'] for node in cluster_nodes])
            additional_node_elements = [
                {'data': {'id': node, 'label': node}, 'style': {'background-color': prefix_colors[node.split(' ')[0]]}}
                for node in additional_nodes
            ]
            return cluster_nodes + additional_node_elements + cluster_edges, {'name': 'cose'}
        
        else:  # Class node click
            node_id = node_data['id']
            updated_nodes = {node_id: {'data': {'id': node_id, 'label': node_id}, 'style': {'background-color': prefix_colors[node_id.split(' ')[0]]}}}
            updated_edges = []
            # Fetch outgoing edges from the clicked node to get the courses for which it is a prerequisite
            for edge in G.edges(node_id):  # This retrieves only outgoing edges from the clicked node
                target_id = edge[1]
                # Ensure the target node is added
                if target_id not in updated_nodes:
                    updated_nodes[target_id] = {'data': {'id': target_id, 'label': target_id}, 'style': {'background-color': prefix_colors[target_id.split(' ')[0]]}}
                # Add edge
                edge_style = {'line-color': 'red', 'width': 4}
                updated_edges.append({'data': {'source': node_id, 'target': target_id}, 'style': edge_style})  # Correctly direct the edge from source to target
            # Convert updated_nodes dictionary to list
            updated_node_elements = list(updated_nodes.values())
            
            return updated_node_elements + updated_edges, {'name': 'cose'}

    return cluster_elements, {'name': 'grid'}

if __name__ == '__main__':
    app.run_server(debug=True)
