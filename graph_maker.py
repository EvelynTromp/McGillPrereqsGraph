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

# Continue with your existing code
