
import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import math
from collections import deque
import time

# === Data Kampus dan Posisi Node ===
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

def bfs(graph, start, goal):
    visited = set()
    queue = deque([(start, [start])])
    while queue:
        node, path = queue.popleft()
        if node == goal:
            return path
        if node not in visited:
            visited.add(node)
            for neighbor in sorted(graph.neighbors(node)):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
    return []

def greedy(graph, start, goal):
    visited = set()
    path = [start]
    current = start
    while current != goal:
        visited.add(current)
        neighbors = list(graph.neighbors(current))
        min_dist = float("inf")
        next_node = None
        for neighbor in neighbors:
            if neighbor not in visited:
                dist = graph[current][neighbor]['weight']
                if dist < min_dist:
                    min_dist = dist
                    next_node = neighbor
        if next_node is None:
            return []
        path.append(next_node)
        current = next_node
    return path

def draw_graph(G, path=[]):
    edge_x, edge_y = [], []
    edge_text = []
    for edge in G.edges(data=True):
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        dist_meters = edge[2]['weight'] * UNIT_METER
        edge_text.append(f"{dist_meters:.0f} m")

    node_x, node_y = [], []
    node_labels = []
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)
        node_labels.append(G.nodes[node]['label'])

    fig = go.Figure()

    # edges
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#777'),
        hoverinfo='text',
        mode='lines',
        text=edge_text,
        hoverlabel=dict(bgcolor="white")
    ))

    # nodes
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_labels,
        textposition="top center",
        marker=dict(
            size=25,
            color='rgb(0, 123, 255)',
            line=dict(width=2, color='DarkBlue'),
            symbol="circle"
        ),
        hoverinfo="text",
        hoverlabel=dict(bgcolor="lightyellow")
    ))

    # highlight path
    if path:
        path_x, path_y = [], []
        for i in range(len(path) - 1):
            x0, y0 = G.nodes[path[i]]['pos']
            x1, y1 = G.nodes[path[i + 1]]['pos']
            path_x.extend([x0, x1, None])
            path_y.extend([y0, y1, None])
        fig.add_trace(go.Scatter(
            x=path_x, y=path_y,
            mode='lines',
            line=dict(width=7, color='crimson', dash='solid'),
            name='Route',
            hoverinfo='none',
        ))

    fig.update_layout(
        title="Campus Map",
        title_font_size=26,
        font_family="Montserrat, sans-serif",
        font_size=14,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(245,245,245,1)',
        margin=dict(l=40, r=40, t=70, b=40),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        hovermode="closest",
        height=600
    )
    return fig

# === Streamlit Page Setup ===
st.set_page_config(
    page_title="🏫 Campus Navigator",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === Inject Google Fonts and CSS for dark/light mode ===
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&display=swap" rel="stylesheet">

    <style>
    /* Dark mode */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background-color: #121212;
            color: #eeeeee;
        }
        .sidebar .css-1d391kg {
            background: linear-gradient(180deg, #283593 0%, #1a237e 100%);
            color: #fff;
        }
        .stButton > button {
            background-color: #bb86fc;
            color: #121212;
            border-radius: 12px;
            font-weight: 700;
            transition: background-color 0.4s ease;
            box-shadow: 0 4px 12px rgba(187, 134, 252, 0.5);
        }
        .stButton > button:hover {
            background-color: #9a68f9;
            cursor: pointer;
        }
    }

    /* Light mode */
    @media (prefers-color-scheme: light) {
        .stApp {
            background-color: #fafafa;
            color: #212121;
        }
        .sidebar .css-1d391kg {
            background: linear-gradient(180deg, #4a90e2 0%, #357abd 100%);
            color: #fff;
        }
        /* Paksa tombol selalu biru - berlaku untuk dark dan light mode */
        .stButton > button {
            background-color: #0073e6 !important; /* biru utama */
            color: #ffffff !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            transition: background-color 0.3s ease, box-shadow 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(0, 115, 230, 0.5) !important;
            border: none !important;
        }

        .stButton > button:hover {
            background-color: #005bbb !important; /* biru lebih gelap saat hover */
            box-shadow: 0 6px 16px rgba(0, 91, 187, 0.6) !important;
            cursor: pointer !important;
        }

    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        font-family: 'Montserrat', sans-serif;
        padding: 2rem 1.5rem 3rem;
        border-right: 1px solid #ccc;
        min-width: 280px;
    }

    /* Sidebar headers */
    [data-testid="stSidebar"] h2 {
        font-weight: 700;
        font-size: 1.8rem;
        margin-bottom: 1rem;
        text-align: center;
    }

    /* Selectbox styling */
    div[data-baseweb="select"] > div {
        border-color: #0073e6 !important;
        box-shadow: 0 0 0 2px rgba(0, 115, 230, 0.3) !important;
    }

    /* Main Title and Subtitle */
    .main-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 3.2rem;
        margin-bottom: 0.1rem;
        color: #222222;
    }
    .subtitle {
        font-family: 'Montserrat', sans-serif;
        font-weight: 500;
        font-size: 1.3rem;
        margin-bottom: 2rem;
        color: #555555;
    }

    /* Result card */
    .result-card {
        background: white;
        padding: 1.8rem 2rem;
        border-radius: 18px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12);
        margin-bottom: 2rem;
        font-size: 1.15rem;
    }

    /* Route list hover */
    .route-list-item {
        padding: 8px 12px;
        margin-bottom: 6px;
        border-radius: 12px;
        transition: background-color 0.3s ease;
        font-weight: 600;
        cursor: default;
    }
    .route-list-item:hover {
        background-color: #f0f4ff;
        color: #0056b3;
        box-shadow: 0 3px 8px rgba(0, 86, 179, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# === Layout ===
with st.sidebar:
    st.markdown("## Select Route")
    start = st.selectbox("Start", list(nodes.keys()), format_func=lambda x: nodes[x]["name"])
    goal = st.selectbox("Destination", list(nodes.keys()), format_func=lambda x: nodes[x]["name"])
    algo = st.selectbox("Algorithm", ["DFS", "BFS", "Greedy Nearest Neighbor"])
    find_route = st.button("Find Route")

with st.container():
    st.markdown('<h1 class="main-title">🏫 Campus Navigator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explore the campus and find your best path using graph algorithms.</p>', unsafe_allow_html=True)

    if find_route:
        if start == goal:
            st.warning("❗ Starting and destination building cannot be the same.")
        else:
            with st.spinner("Calculating the best route... ⏳"):
                time.sleep(1)  # simulate loading
                if algo == "DFS":
                    route = dfs(G, start, goal)
                elif algo == "BFS":
                    route = bfs(G, start, goal)
                else:
                    route = greedy(G, start, goal)

        if route:
            total_m = sum(G[route[i]][route[i+1]]['weight'] * UNIT_METER for i in range(len(route)-1))
            total_km = total_m / 1000
            route_names = [nodes[r]["name"] for r in route]

            route_html = f"""
            <div class="result-card">
                <div><strong>✅ Route found:</strong> {' → '.join(route_names)}</div>
                <div><strong>📏 Total distance:</strong> {total_m:.0f} meters ({total_km:.2f} km)</div>
                <br/>
                {"".join(f'<div class="route-list-item">{i+1}. {loc}</div>' for i, loc in enumerate(route_names))}
            </div>
            """
            st.markdown(route_html, unsafe_allow_html=True)

            fig = draw_graph(G, path=route)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("❌ No route found between the selected buildings.")

    else:
        st.info("⬅ Please select start, destination, and algorithm, then click Find Route.")
