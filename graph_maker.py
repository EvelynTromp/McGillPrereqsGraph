import pandas as pd
import networkx as nx
import plotly.graph_objects as go

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

# Position nodes using the spring layout
pos = nx.spring_layout(G, k=0.5)  # k controls the spacing between nodes

# For each node and edge, extract the positions
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines')

node_x = []
node_y = []
node_text = []
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(node)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    hoverinfo='text',
    marker=dict(
        showscale=False,
        colorscale='YlGnBu',
        size=10,
        line_width=2))

node_trace.text = node_text

fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=0,l=0,r=0,t=0),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )

fig.update_layout(title='Interactive Course Prerequisite Graph', title_x=0.5)
fig.show()
