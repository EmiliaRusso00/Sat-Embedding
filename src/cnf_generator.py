from itertools import combinations

class CNFGenerator:
    def __init__(self, G_log, G_phys, allow_shared_physical=False):
        self.G_log = G_log
        self.G_phys = G_phys
        self.allow_shared_physical = allow_shared_physical

        # Ordinamento dei nodi
        self.logical_nodes = list(sorted(G_log.nodes()))
        self.physical_nodes = list(sorted(G_phys.nodes()))

        self.n = len(self.logical_nodes)
        self.m = len(self.physical_nodes)

        # Mappa variabili SAT: (log_node, phys_node) → id univoco
        self.var_map = {}
        vid = 1
        for i in self.logical_nodes:
            for a in self.physical_nodes:
                self.var_map[(i, a)] = vid
                vid += 1

        self.num_vars = vid - 1
        self.clauses = []
        self.clause_type = []   # Nuova lista per il tipo di clausola

    def x(self, i, a):
        """Restituisce l'id della variabile SAT x{i,a}"""
        return self.var_map[(i, a)]

    def add_clause(self, lits, ctype="generic"):
        """Aggiunge clausola con tipo"""
        self.clauses.append(lits)
        self.clause_type.append(ctype)

    # ----------------------------------------------------------------------
    # 1) Ogni nodo logico deve mappare esattamente su un nodo fisico
    # ----------------------------------------------------------------------
    def encode_exactly_one_per_logical(self):
        for i in self.logical_nodes:
            # almeno uno
            lits = [self.x(i, a) for a in self.physical_nodes]
            self.add_clause(lits, "at_least_one")

            # al massimo uno (pairwise)
            for a, b in combinations(self.physical_nodes, 2):
                self.add_clause([-self.x(i, a), -self.x(i, b)], "at_most_one")

    # ----------------------------------------------------------------------
    # 2) Nessuna condivisione del nodo fisico (optional)
    # ----------------------------------------------------------------------
    def encode_mutual_exclusion_on_physical(self):
        if self.allow_shared_physical:
            return

        for a in self.physical_nodes:
            for i, j in combinations(self.logical_nodes, 2):
                self.add_clause([-self.x(i, a), -self.x(j, a)], "mutual_exclusion")

    # ----------------------------------------------------------------------
    # 3) Edge consistency
    # ----------------------------------------------------------------------
    def encode_edge_consistency(self):
        phys_edges = set(tuple(sorted(e)) for e in self.G_phys.edges())

        for i, j in self.G_log.edges():
            for a in self.physical_nodes:
                for b in self.physical_nodes:
                    if a == b or (min(a, b), max(a, b)) not in phys_edges:
                        self.add_clause([-self.x(i, a), -self.x(j, b)], "edge_consistency")

    # ----------------------------------------------------------------------
    # Generazione CNF
    # ----------------------------------------------------------------------
    def generate(self):
        self.encode_exactly_one_per_logical()
        self.encode_mutual_exclusion_on_physical()
        self.encode_edge_consistency()
        return self.num_vars, len(self.clauses)

    # ----------------------------------------------------------------------
    # Scrittura in formato DIMACS con ID clausole e tipo
    # ----------------------------------------------------------------------
    def write_dimacs(self, path):
        with open(path, 'w') as f:
            f.write(f"p cnf {self.num_vars} {len(self.clauses)}\n")
            for idx, (c, ctype) in enumerate(zip(self.clauses, self.clause_type), start=1):
                f.write(f"c id {idx} type {ctype}\n")  # commento con ID e tipo
                f.write(' '.join(str(l) for l in c) + ' 0\n')
        print(f"Wrote DIMACS CNF with {self.num_vars} vars and {len(self.clauses)} clauses to {path}")
