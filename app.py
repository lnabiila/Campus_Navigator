import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import math
from collections import deque

# --- Campus buildings data (coordinates in arbitrary units)
nodes = {
    "A": {"name": "Engineering Faculty", "pos": (0, 0)},
    "B": {"name": "Economics Faculty", "pos": (2, 3)},
    "C": {"name": "Library", "pos": (4, 1)},
    "D": {"name": "Rectorate Building", "pos": (6, 0)},
    "E": {"name": "Computer Science Faculty", "pos": (8, 3)},
    "F": {"name": "Campus Mosque", "pos": (10, 0)},
    "G": {"name": "Student Center", "pos": (5, 5)},
    "H": {"name": "Sports Hall", "pos": (7, 6)},
    "I": {"name": "Auditorium", "pos": (9, 5)},
    "J": {"name": "Cafeteria", "pos": (3, 7)},
}

UNIT_METER = 100

def euclidean(a, b):
    xa, ya = a
    xb, yb = b
    return math.hypot(xa - xb, ya - yb)

edges = []
keys = list(nodes.keys())
for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        d = euclidean(nodes[keys[i]]["pos"], nodes[keys[j]]["pos"])
        if d < 5:
            edges.append((keys[i], keys[j], d))

G = nx.Graph()
for k, v in nodes.items():
    G.add_node(k, label=v["name"], pos=v["pos"])
G.add_weighted_edges_from(edges)

def dfs(graph, start, goal):
    visited = set()
    stack = [(start, [start])]
    while stack:
        node, path = stack.pop()
        if node == goal:
            return path
        if node not in visited:
            visited.add(node)
            for neighbor in sorted(graph.neighbors(node), reverse=True):
                if neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))
    return []

def draw_graph(G, path=[]):
    edge_x, edge_y = [], []
    for edge in G.edges(data=True):
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    node_x, node_y, node_labels = [], [], []
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)
        node_labels.append(G.nodes[node]['label'])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='lightgray'),
        hoverinfo='none',
        mode='lines'))

    for edge in G.edges(data=True):
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        mid_x, mid_y = (x0+x1)/2, (y0+y1)/2
        dist_meters = edge[2]['weight'] * UNIT_METER
        fig.add_annotation(
            x=mid_x, y=mid_y,
            text=f"{dist_meters:.0f} m",
            showarrow=False,
            font=dict(size=10, color="gray"),
            bgcolor="white",
            opacity=0.7,
        )

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_labels,
        textposition="top center",
        marker=dict(size=18, color='dodgerblue', line=dict(width=2, color='DarkSlateGrey'))
    ))

    if path:
        path_x, path_y = [], []
        for i in range(len(path) - 1):
            x0, y0 = G.nodes[path[i]]['pos']
            x1, y1 = G.nodes[path[i+1]]['pos']
            path_x.extend([x0, x1, None])
            path_y.extend([y0, y1, None])
        fig.add_trace(go.Scatter(
            x=path_x, y=path_y,
            mode='lines',
            line=dict(width=5, color='crimson'),
            name='Route'
        ))

    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        height=600,
        title="Campus Map"
    )
    return fig

# --- Streamlit UI ---
st.set_page_config(page_title="Campus Navigator", page_icon="🏫", layout="wide")

st.title("🏫 Campus Navigator")
st.write("Find the best route between campus buildings using Depth-First Search (DFS) algorithm.")

with st.sidebar:
    st.header("Route Preferences")
    start = st.selectbox("Starting Building", list(nodes.keys()), format_func=lambda x: nodes[x]["name"])
    goal = st.selectbox("Destination Building", list(nodes.keys()), format_func=lambda x: nodes[x]["name"])
    btn = st.button("Find Route")

if btn:
    if start == goal:
        st.warning("Starting building and destination cannot be the same.")
    else:
        route = dfs(G, start, goal)
        if route:
            total_m = sum(G[route[i]][route[i+1]]['weight'] * UNIT_METER for i in range(len(route)-1))
            total_km = total_m / 1000
            route_names = [nodes[r]["name"] for r in route]

            st.success(f"Route found: {' → '.join(route_names)}")
            st.info(f"Total distance: {total_m:.0f} meters ({total_km:.2f} km)")

            fig = draw_graph(G, path=route)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("No route found between the selected buildings.")
else:
    st.info("Use the sidebar to select your route, then click 'Find Route'.")