import argparse
import time
import yaml
import os

from parser import read_graph
from cnf_generator import CNFGenerator
from solver_interface import solve_dimacs_file
from metrics import write_experiment_output
from utils import ensure_dir
from plot_utils import plot_embedding  # funzioni di plotting importate

def run_experiment(cfg):
    exp_id = cfg.get('id', 0)
    G_log = read_graph(cfg['logical_graph'])
    G_phys = read_graph(cfg['physical_graph'])

    timeout = cfg.get('timeout_seconds', None)
    allow_shared = cfg.get('allow_shared_physical_qubits', False)

    exp_dir = os.path.join('outputs', str(exp_id))
    ensure_dir(exp_dir)

    # ----- GENERA CNF -----
    t0 = time.time()
    gen = CNFGenerator(G_log, G_phys, allow_shared_physical=allow_shared)
    num_vars, num_clauses = gen.generate()
    dimacs_path = os.path.join(exp_dir, f"exp_{exp_id}.cnf")
    gen.write_dimacs(dimacs_path)
    t1 = time.time()

    # ----- RISOLVI SAT -----
    res = solve_dimacs_file(dimacs_path, timeout_seconds=timeout, cnf_gen=gen)

    solution_map = None
    unsat_clauses_serializable = None

    # SAT → decodifica soluzione
    if res.get("status") == "SAT" and res.get("model"):
        rev = {vid: (i, a) for (i, a), vid in gen.var_map.items()}
        solution_map = {i: a for lit in res["model"] if lit > 0
                        for entry in [rev.get(lit)] if entry
                        for i, a in [entry]}

    # UNSAT → estrai clausole coinvolte
    elif res.get("status") == "UNSAT":
        if 'unsat_core' in res and res['unsat_core']:
            unsat_clauses_serializable = [(gen.clauses[idx], gen.clause_type[idx]) for idx in res['unsat_core']]
        else:
            # fallback: salva tutte le clausole
            unsat_clauses_serializable = [(list(clause), ctype) for clause, ctype in zip(gen.clauses, gen.clause_type)]

    # ----- Salva JSON risultato -----
    out_file = write_experiment_output(
        exp_id, cfg, G_log, G_phys,
        num_vars, num_clauses, 'pairwise',
        'glucose', t1 - t0, res.get('time', 0.0),
        res.get('status', 'ERROR'),
        solution=solution_map,
        unsat_clauses=unsat_clauses_serializable,
        solver_error=res.get('error'),
        output_dir=exp_dir
    )
    print(f"[INFO] Saved results to {out_file}")

    # ----- Plot embedding -----
    plot_embedding(G_log, G_phys, solution_map, exp_dir, exp_id)


# ================================================================
#  ENTRY POINT
# ================================================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config.yaml")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        cfg_all = yaml.safe_load(f)

    ensure_dir("outputs")

    for cfg in cfg_all.get("experiments", []):
        run_experiment(cfg)
