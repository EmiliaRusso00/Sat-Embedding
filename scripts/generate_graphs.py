import networkx as nx
import os
import random
from itertools import product

try:
    import dwave_networkx as dnx
    DWAVE_AVAILABLE = True
except ImportError:
    DWAVE_AVAILABLE = False


# ---------------------------------------------------------
#   SALVATORE FILE TXT
# ---------------------------------------------------------
def save_graph_txt(G, path):
    """
    Salva un grafo in formato txt:
    - ogni riga: "u v" per un arco
    - nodi isolati: "u"
    """
    with open(path, 'w') as f:
        for u, v in G.edges():
            f.write(f"{u} {v}\n")
        for u in nx.isolates(G):
            f.write(f"{u}\n")
    print(f"[ OK ] Grafo salvato in {path}")


# ---------------------------------------------------------
#   GENERATORI STANDARD
# ---------------------------------------------------------
def gen_random_graph(n, p=0.3):
    return nx.erdos_renyi_graph(n, p)

def gen_tree(n):
    return nx.random_labeled_tree(n)

def gen_grid_2d(m, n):
    return nx.grid_2d_graph(m, n)

def gen_grid_3d(m, n, p):
    return nx.grid_graph(dim=[m, n, p])

def gen_clique(n):
    return nx.complete_graph(n)

def gen_bipartite(a, b):
    return nx.complete_bipartite_graph(a, b)

def gen_star(n):
    return nx.star_graph(n)

def gen_cycle(n):
    return nx.cycle_graph(n)

def gen_line(n):
    return nx.path_graph(n)

def gen_small_world(n, k, p):
    return nx.watts_strogatz_graph(n, k, p)

def gen_scale_free(n):
    return nx.barabasi_albert_graph(n, m=2)


# ---------------------------------------------------------
#   GENERATORI D-WAVE
# ---------------------------------------------------------
def require_dwave():
    if not DWAVE_AVAILABLE:
        raise RuntimeError("dwave_networkx NON è installato. Installa con: pip install dwave-networkx")


def gen_chimera(M, N, L):
    require_dwave()
    return dnx.chimera_graph(M, N, L)


def gen_pegasus(m):
    """
    Pegasus di dimensione m (tipicamente 3..16).
    """
    require_dwave()
    return dnx.pegasus_graph(m)


def gen_zephyr(m, t):
    """
    Zephyr: parametri:
        m = dimensione (tipico 3..20)
        t = dimensione bipartizione (tipico 4)
    """
    require_dwave()
    return dnx.zephyr_graph(m, t)


# ---------------------------------------------------------
#   MENU E GENERAZIONE
# ---------------------------------------------------------
def main():

    print("\n=== GENERATORE DI GRAFI ===")
    print("Tipi disponibili:")
    
    types = {
        "1": "Grafo random (Erdős–Rényi)",
        "2": "Albero",
        "3": "Griglia 2D",
        "4": "Griglia 3D",
        "5": "Clique",
        "6": "Bipartito",
        "7": "Stella",
        "8": "Ciclo",
        "9": "Linea (path)",
        "10": "Small-world",
        "11": "Scale-free",
        "12": "Chimera (D-Wave)",
        "13": "Pegasus (D-Wave)",
        "14": "Zephyr (D-Wave)"
    }

    for k, v in types.items():
        print(f"{k}) {v}")

    choice = input("\nScegli un tipo di grafo: ")

    # -----------------------------------------------------
    #   SCELTA TIPO DI GRAFO
    # -----------------------------------------------------
    if choice == "1":
        n = int(input("Numero nodi: "))
        p = float(input("Probabilità arco (0-1): "))
        G = gen_random_graph(n, p)

    elif choice == "2":
        n = int(input("Numero nodi: "))
        G = gen_tree(n)

    elif choice == "3":
        m = int(input("Righe: "))
        n = int(input("Colonne: "))
        G = gen_grid_2d(m, n)

    elif choice == "4":
        x = int(input("Dimensione X: "))
        y = int(input("Dimensione Y: "))
        z = int(input("Dimensione Z: "))
        G = gen_grid_3d(x, y, z)

    elif choice == "5":
        n = int(input("Numero nodi: "))
        G = gen_clique(n)

    elif choice == "6":
        a = int(input("Lato A: "))
        b = int(input("Lato B: "))
        G = gen_bipartite(a, b)

    elif choice == "7":
        n = int(input("Numero foglie: "))
        G = gen_star(n)

    elif choice == "8":
        n = int(input("Numero nodi: "))
        G = gen_cycle(n)

    elif choice == "9":
        n = int(input("Numero nodi: "))
        G = gen_line(n)

    elif choice == "10":
        n = int(input("Numero nodi: "))
        k = int(input("Numero vicini: "))
        p = float(input("Probabilità ri-wire (0-1): "))
        G = gen_small_world(n, k, p)

    elif choice == "11":
        n = int(input("Numero nodi: "))
        G = gen_scale_free(n)

    # -------------------------
    #       CHIMERA
    # -------------------------
    elif choice == "12":
        M = int(input("M (righe celle): "))
        N = int(input("N (colonne celle): "))
        L = int(input("L (dimensione bipartizione, tipicamente 4): "))
        G = gen_chimera(M, N, L)

    # -------------------------
    #       PEGASUS
    # -------------------------
    elif choice == "13":
        m = int(input("Dimensione m (es. 2..16): "))
        G = gen_pegasus(m)

    # -------------------------
    #       ZEPHYR
    # -------------------------
    elif choice == "14":
        m = int(input("Dimensione m (es. 3..20): "))
        t = int(input("Dimensione bipartizione t (tipicamente 4): "))
        G = gen_zephyr(m, t)

    else:
        print("Scelta non valida.")
        return

    # -----------------------------------------------------
    # SALVATAGGIO
    # -----------------------------------------------------
    os.makedirs("graphs", exist_ok=True)

    filename = input("\nNome file output (senza .txt): ")
    path = f"graphs/{filename}.txt"

    save_graph_txt(G, path)
    print("\nFatto!")


if __name__ == "__main__":
    main()
