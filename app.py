import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import math
import heapq
from collections import deque
import time

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
    visited = set([start])
    queue = deque([(start, [start])])
    while queue:
        node, path = queue.popleft()
        if node == goal:
            return path
        for neighbor in sorted(graph.neighbors(node)):
            if neighbor not in visited:
                visited.add(neighbor)  
                queue.append((neighbor, path + [neighbor]))
    return []

def greedy(graph, start, goal):
    def heuristic(n):
        x1, y1 = graph.nodes[n]['pos']
        x2, y2 = graph.nodes[goal]['pos']
        return math.hypot(x1 - x2, y1 - y2)

    visited = set()
    frontier = []
    heapq.heappush(frontier, (heuristic(start), start, [start]))

    while frontier:
        h, current, path = heapq.heappop(frontier)

        if current == goal:
            return path

        if current in visited:
            continue

        visited.add(current)

        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                heapq.heappush(frontier, (heuristic(neighbor), neighbor, path + [neighbor]))

    return []

def draw_graph(G, path=[]):
    edge_x, edge_y = [], []
    edge_text = []
    edge_label_x, edge_label_y = [], []
    edge_label_text = []

    path_edge_label_x, path_edge_label_y = [], []
    path_edge_label_text = []

    for edge in G.edges(data=True):
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

        dist_meters = edge[2]['weight'] * UNIT_METER
        edge_text.append(f"{dist_meters:.0f} m")

        mid_x = (x0 + x1) / 2
        mid_y = (y0 + y1) / 2

        if path and edge[0] in path and edge[1] in path:
            is_in_path = False
            for i in range(len(path) - 1):
                if (path[i] == edge[0] and path[i+1] == edge[1]) or (path[i] == edge[1] and path[i+1] == edge[0]):
                    is_in_path = True
                    break
            if is_in_path:
                path_edge_label_x.append(mid_x)
                path_edge_label_y.append(mid_y + 0.15)  
                path_edge_label_text.append(f"{dist_meters:.0f} m")
            else:
                edge_label_x.append(mid_x)
                edge_label_y.append(mid_y)
                edge_label_text.append(f"{dist_meters:.0f} m")
        else:
            edge_label_x.append(mid_x)
            edge_label_y.append(mid_y)
            edge_label_text.append(f"{dist_meters:.0f} m")

    node_x, node_y = [], []
    icon_map = {
        "Engineering Faculty": "🏗",
        "Economics Faculty": "💼",
        "Library": "📚",
        "Rectorate Building": "🏢",
        "Computer Science Faculty": "💻",
        "Campus Mosque": "🕌",
        "Student Center": "🎓",
        "Sports Hall": "🏀",
        "Auditorium": "🎤",
        "Cafeteria": "🍽",
    }

    node_labels = []
    node_icons = []
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)
        label = G.nodes[node]['label']
        node_labels.append(label)  # hanya nama tanpa emoji
        node_icons.append(icon_map.get(label, "📍"))  # icon besar saja

    fig = go.Figure()

    # edges (garis)
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#777'),
        hoverinfo='text',
        mode='lines',
        text=edge_text,
        hoverlabel=dict(bgcolor="white")
    ))

    fig.add_trace(go.Scatter(
        x=edge_label_x,
        y=edge_label_y,
        mode='text',
        text=edge_label_text,
        textfont=dict(color='blue', size=10),
        hoverinfo='skip',
        showlegend=False
    ))

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

        fig.add_trace(go.Scatter(
            x=path_edge_label_x,
            y=path_edge_label_y,
            mode='text',
            text=path_edge_label_text,
            textfont=dict(color='blue', size=10),
            hoverinfo='skip',
            showlegend=False
        ))

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='text',
        text=node_icons,
        textposition="middle center",
        hoverinfo="text",
        hovertext=node_labels,
        hoverlabel=dict(bgcolor="lightyellow"),
        textfont=dict(size=30),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=node_x, y=[y + 0.3 for y in node_y], 
        mode='text',
        text=node_labels,
        textposition="top center",
        hoverinfo='skip',
        textfont=dict(size=12, color='black'),
        showlegend=False
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
    page_title=" Campus Navigator",
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
            color: #f5f5f5;
        }
        .sidebar .css-1d391kg {
            background: linear-gradient(180deg, #2d3e50 0%, #1c2833 100%);
            color: #ffffff;
        }

        /* Tombol tetap biru di dark mode */
        .stButton > button {
            background-color: #0073e6 !important;
            color: #ffffff !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            transition: background-color 0.3s ease, box-shadow 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(0, 115, 230, 0.5) !important;
            border: none !important;
        }

        .stButton > button:hover {
            background-color: #005bbb !important;
            box-shadow: 0 6px 16px rgba(0, 91, 187, 0.6) !important;
            cursor: pointer !important;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            font-family: 'Montserrat', sans-serif;
            padding: 2rem 1.5rem 3rem;
            border-right: 1px solid #444;
            min-width: 280px;
            background-color: #1e1e1e;
        }

        /* Sidebar headers */
        [data-testid="stSidebar"] h2 {
            font-weight: 700;
            font-size: 1.8rem;
            margin-bottom: 1rem;
            text-align: center;
            color: #ffffff;
        }

        /* Selectbox styling */
        div[data-baseweb="select"] > div {
            border-color: #3399ff !important;
            box-shadow: 0 0 0 2px rgba(51, 153, 255, 0.4) !important;
            background-color: #1e1e1e !important;
            color: #ffffff !important;
        }

        /* Main Title and Subtitle */
        .main-title {
            font-family: 'Montserrat', sans-serif;
            font-weight: 700;
            font-size: 3.2rem;
            margin-bottom: 0.1rem;
            color: #f0f0f0;
        }
        .subtitle {
            font-family: 'Montserrat', sans-serif;
            font-weight: 500;
            font-size: 1.3rem;
            margin-bottom: 2rem;
            color: #bbbbbb;
        }

        /* Result card */
        .result-card {
            background: #1c1c1c;
            padding: 1.8rem 2rem;
            border-radius: 18px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            margin-bottom: 2rem;
            font-size: 1.15rem;
            color: #2c2c2c;
        }

        /* Route list hover */
        .route-list-item {
            padding: 8px 12px;
            margin-bottom: 6px;
            border-radius: 12px;
            transition: background-color 0.3s ease;
            font-weight: 600;
            cursor: default;
            color: #2c2c2c;
        }
        .route-list-item:hover {
            background-color: #2a3b55;
            color: #66aaff;
            box-shadow: 0 3px 8px rgba(102, 170, 255, 0.2);
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
    algo = st.selectbox("Algorithm", ["DFS", "BFS", "Greedy BFS"])
    find_route = st.button("Find Route")

with st.container():
    st.markdown('<h1 class="main-title">🏫 Campus Navigator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Explore the campus and find your best path using graph algorithms.</p>', unsafe_allow_html=True)

    route = []
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
        st.info("⬅ Please select start, destination, and algorithm, then click Find Route.")
