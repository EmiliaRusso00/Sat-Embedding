import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import networkx as nx
from utils import ensure_dir

# ================================================================
#  POSIZIONI AUTOMATICHE 2D/3D
# ================================================================
def compute_positions(G):
    """
    Restituisce posizioni per nodi 2D/3D.
    - Se i nodi sono tuple 2D/3D, usa le coordinate già presenti.
    - Altrimenti usa spring_layout.
    """
    nodes = list(G.nodes())
    if all(isinstance(n, tuple) and len(n) == 2 for n in nodes):
        return {n: (n[0], n[1]) for n in nodes}, 2
    if all(isinstance(n, tuple) and len(n) == 3 for n in nodes):
        return {n: (n[0], n[1], n[2]) for n in nodes}, 3
    return nx.spring_layout(G, seed=42), 2


# ================================================================
#  GENERIC PLOT (2D/3D)
# ================================================================
def plot_graph(G, pos, dim, title="Graph", node_colors=None,
               node_labels=None, edge_colors=None, edge_widths=None,
               figsize=(6, 6), save_path=None):
    fig = plt.figure(figsize=figsize)

    if node_labels is None:
        node_labels = {n: str(n) for n in G.nodes()}
    if edge_colors is None:
        edge_colors = ['gray'] * len(G.edges())
    if edge_widths is None:
        edge_widths = [1] * len(G.edges())

    if dim == 3:
        ax = fig.add_subplot(111, projection='3d')
        xs = [pos[n][0] for n in G.nodes()]
        ys = [pos[n][1] for n in G.nodes()]
        zs = [pos[n][2] for n in G.nodes()]
        ax.scatter(xs, ys, zs, c=node_colors, s=80)
        for (u, v), ec, ew in zip(G.edges(), edge_colors, edge_widths):
            x = [pos[u][0], pos[v][0]]
            y = [pos[u][1], pos[v][1]]
            z = [pos[u][2], pos[v][2]]
            ax.plot(x, y, z, color=ec, linewidth=ew)
        for n in G.nodes():
            x, y, z = pos[n]
            ax.text(x, y, z, node_labels[n], color='black')
        ax.set_title(title)
    else:
        ax = fig.add_subplot(111)
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths, alpha=0.8, ax=ax)
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=600, ax=ax)
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_color='white', font_weight='bold', ax=ax)
        plt.title(title)

    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
    plt.close()


# ================================================================
#  PLOT COMPLETO LOGICAL → PHYSICAL
# ================================================================
def plot_embedding(G_logical, G_physical, solution_map, save_dir, exp_id):
    """
    Disegna grafo logico, fisico e embedding.
    Funziona con qualsiasi grafo NetworkX.
    """
    ensure_dir(save_dir)

    # --------------------
    # Logical Graph
    # --------------------
    pos_log, dim_log = compute_positions(G_logical)
    logical_colors = ['skyblue'] * len(G_logical.nodes())
    plot_graph(G_logical, pos_log, dim_log,
               title="Logical Graph",
               node_colors=logical_colors,
               save_path=os.path.join(save_dir, f"exp_{exp_id}_logical.png"))

    # --------------------
    # Physical Graph
    # --------------------
    pos_phys, dim_phys = compute_positions(G_physical)
    physical_colors = ['lightgreen'] * len(G_physical.nodes())
    plot_graph(G_physical, pos_phys, dim_phys,
               title="Physical Graph",
               node_colors=physical_colors,
               save_path=os.path.join(save_dir, f"exp_{exp_id}_physical.png"))

    # --------------------
    # Embedding Graph
    # --------------------
    node_colors = []
    labels = {}
    edge_colors = []
    edge_widths = []

    used_edges = set()
    if solution_map:
        for u_log, v_log in G_logical.edges():
            if u_log in solution_map and v_log in solution_map:
                up = solution_map[u_log]
                vp = solution_map[v_log]
                used_edges.add(tuple(sorted((up, vp))))

    for n in G_physical.nodes():
        mapped = [l for l, p in solution_map.items() if p == n] if solution_map else []
        if mapped:
            node_colors.append("orange")
            labels[n] = ",".join(str(x) for x in mapped)
        else:
            node_colors.append("lightgray")
            labels[n] = str(n)

    for u, v in G_physical.edges():
        if tuple(sorted((u, v))) in used_edges:
            edge_colors.append("red")
            edge_widths.append(2.5)
        else:
            edge_colors.append("gray")
            edge_widths.append(1)

    plot_graph(G_physical, pos_phys, dim_phys,
               title="Embedding: Logical → Physical",
               node_colors=node_colors,
               node_labels=labels,
               edge_colors=edge_colors,
               edge_widths=edge_widths,
               save_path=os.path.join(save_dir, f"exp_{exp_id}_embedding.png"))
