import pandas as pd
import networkx as nx
import dash
from dash import html, dcc, Input, Output, State
import dash_cytoscape as cyto
import random

# Load the CSV file
df = pd.read_csv("C:\\Users\\evely\\OneDrive\\Desktop\\McGill Courses and Prereqs9.csv")

# Ensure all data is treated as string and handle missing values
df['Course Code'] = df['Course Code'].astype(str)
df['Prerequisites'] = df['Prerequisites'].astype(str).replace('nan', '')  # Replace NaN with empty string

# Handle multiple prerequisites separated by commas
df['Prerequisites'] = df['Prerequisites'].str.split(', ')
df_exploded = df.explode('Prerequisites')

# Create a directed graph
G = nx.DiGraph()

# Add edges based on the prerequisite data, skip adding edges where prerequisites are empty
for index, row in df_exploded.iterrows():
    if row['Prerequisites'].strip():  # Only add edge if there is a prerequisite
        G.add_edge(row['Course Code'], row['Prerequisites'])


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
                    'width': 2
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
            detailed_nodes = [
                {'data': {'id': node, 'label': node}, 'style': {'background-color': prefix_colors[node.split(' ')[0]]}}
                for node in G.nodes() if node.startswith(prefix)
            ]
            detailed_edges = [
                {'data': {'source': edge[1], 'target': edge[0]}}  # Reverse the direction for display
                for edge in G.edges() if edge[1].startswith(prefix) and edge[0].startswith(prefix)
            ]
            return detailed_nodes + detailed_edges, {'name': 'cose'}

        else:  # Class node click
            node_id = node_data['id']
            updated_nodes = []
            updated_edges = []
            connected_nodes = set()
            for edge in G.edges():
                if node_id in edge:
                    connected_nodes.update(edge)
                    edge_style = {'line-color': 'red', 'width': 4}
                    updated_edges.append({'data': {'source': edge[1], 'target': edge[0]}, 'style': edge_style})  # Reverse the direction for display
            for node in connected_nodes:
                node_style = {'background-color': prefix_colors[node.split(' ')[0]]}
                updated_nodes.append({'data': {'id': node, 'label': node}, 'style': node_style})

            return updated_nodes + updated_edges, {'name': 'cose'}

    return cluster_elements, {'name': 'grid'}



if __name__ == '__main__':
    app.run_server(debug=True)
