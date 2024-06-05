import pandas as pd
import networkx as nx
import dash
from dash import html, dcc, Input, Output
import dash_cytoscape as cyto

# Load the CSV file
df = pd.read_csv("C:\\Users\\evely\\OneDrive\\Desktop\\prerequisite_relationships1.csv")

# Handle multiple prerequisites separated by commas
df['Is a Prerequisite for'] = df['Is a Prerequisite for'].str.split(', ')
df_exploded = df.explode('Is a Prerequisite for')

# Create a directed graph
G = nx.DiGraph()

# Add edges based on the prerequisite data
for index, row in df_exploded.iterrows():
    G.add_edge(row['Course Code'], row['Is a Prerequisite for'])

# Convert the graph into a format that can be used by Dash Cytoscape
elements = []
for node in G.nodes():
    elements.append({'data': {'id': node, 'label': node}})
for edge in G.edges():
    elements.append({'data': {'source': edge[0], 'target': edge[1]}})

app = dash.Dash(__name__)
app.layout = html.Div([
    html.P("Click on a node to highlight its connections:"),
    cyto.Cytoscape(
        id='cytoscape-graph',
        elements=elements,
        style={'width': '100%', 'height': '400px'},
        layout={'name': 'cose'},
        stylesheet=[
            {'selector': 'node',
             'style': {
                 'label': 'data(label)',
                 'background-color': '#0074D9'}},
            {'selector': 'edge',
             'style': {'line-color': '#CCCCCC'}},
            {'selector': '.highlighted',
             'style': {'background-color': '#FF4136', 'line-color': '#FF4136'}}
        ]
    )
])

@app.callback(
    Output('cytoscape-graph', 'stylesheet'),
    Input('cytoscape-graph', 'tapNodeData')
)
def generate_stylesheet(node_data):
    if not node_data:
        return [{
            'selector': 'node',
            'style': {
                'background-color': '#0074D9'
            }},
            {'selector': 'edge',
             'style': {
                 'line-color': '#CCCCCC'
            }}
        ]
    stylesheet = [
        {'selector': 'node',
         'style': {
             'background-color': '#0074D9'
         }},
        {'selector': f'node[id = "{node_data["id"]}"]',
         'style': {
             'background-color': '#FF4136'
         }},
        {'selector': f'edge[source = "{node_data["id"]}"]',
         'style': {
             'line-color': '#FF4136'
         }},
        {'selector': 'edge',
         'style': {'line-color': '#CCCCCC',
                   'curve-style': 'bezier'}}
    ]
    return stylesheet

if __name__ == '__main__':
    app.run_server(debug=True)
