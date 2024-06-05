import pandas as pd
import networkx as nx
import dash
from dash import html, dcc, Input, Output
import dash_cytoscape as cyto
import random

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

# Generate a random light color
def generate_light_color():
    return f"#{random.randint(100, 255):02x}{random.randint(100, 255):02x}{random.randint(100, 255):02x}"

# Determine color based on course prefix
prefix_colors = {}
def get_color(course_code):
    prefix = course_code.split(' ')[0]  # Assumes space separates the prefix and the number
    if prefix not in prefix_colors:
        prefix_colors[prefix] = generate_light_color()
    return prefix_colors[prefix]

# Convert the graph into a format that can be used by Dash Cytoscape
elements = [
    {'data': {'id': node, 'label': node}, 'style': {'background-color': get_color(node), 'label': node}}
    for node in G.nodes()
]
elements += [
    {'data': {'source': edge[0], 'target': edge[1]}}
    for edge in G.edges()
]

app = dash.Dash(__name__)
app.layout = html.Div([
    html.P("Click on a node to highlight its connections:"),
    cyto.Cytoscape(
        id='cytoscape-graph',
        elements=elements,
        style={'width': '100%', 'height': '500px'},
        layout={'name': 'cose'},
        stylesheet=[
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)',
                    'text-valign': 'center',
                    'color': 'white',
                    'text-outline-width': 2,
                    'text-outline-color': '#888'
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'line-color': '#CCCCCC',
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle'
                }
            },
            {
                'selector': '.highlighted',
                'style': {
                    'background-color': '#FF4136',
                    'line-color': '#FF4136',
                    'target-arrow-color': '#FF4136'
                }
            },
            {
                'selector': '.highlighted-edge',
                'style': {
                    'line-color': '#FF4136',
                    'target-arrow-color': '#FF4136'
                }
            }
        ]
    )
])

@app.callback(
    Output('cytoscape-graph', 'stylesheet'),
    Input('cytoscape-graph', 'tapNodeData')
)
def generate_stylesheet(node_data):
    if not node_data:
        return [
            {
                'selector': 'node',
                'style': {
                    'background-color': '#AAAAAA',
                    'content': 'data(label)'
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'line-color': '#CCCCCC',
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle'
                }
            }
        ]
    stylesheet = [
        {
            'selector': 'node',
            'style': {
                'background-color': '#AAAAAA',
                'content': 'data(label)'
            }
        },
        {
            'selector': 'edge',
            'style': {
                'line-color': '#CCCCCC',
                'curve-style': 'bezier',
                'target-arrow-shape': 'triangle'
            }
        },
        {
            'selector': f'node[id = "{node_data["id"]}"]',
            'style': {
                'background-color': '#FF4136',
                'content': 'data(label)'
            }
        },
        {
            'selector': f'edge[source = "{node_data["id"]}"]',
            'style': {
                'line-color': '#FF4136',
                'target-arrow-color': '#FF4136'
            }
        }
    ]
    return stylesheet

if __name__ == '__main__':
    app.run_server(debug=True)
