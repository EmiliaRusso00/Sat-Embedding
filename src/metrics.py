import json
from datetime import datetime

def write_experiment_output(exp_id, config, logical_graph, physical_graph,
                            num_vars, num_clauses, encoding_type,
                            solver_name, time_cnf, time_sat, status,
                            solution=None, solver_error=None,
                            unsat_clauses=None, output_dir="outputs"):
    """
    Scrive il risultato di un esperimento in JSON.
    Se il problema è UNSAT, include le clausole che generano UNSAT.
    """
    out = {
        "experiment_id": exp_id,
        "timestamp": datetime.now().isoformat(),
        "config": config,
        "logical_graph": {
            "num_vertices": logical_graph.number_of_nodes(),
            "num_edges": logical_graph.number_of_edges()
        },
        "physical_graph": {
            "num_vertices": physical_graph.number_of_nodes(),
            "num_edges": physical_graph.number_of_edges()
        },
        "sat_encoding": {
            "num_variables": num_vars,
            "num_clauses": num_clauses,
            "encoding_type": encoding_type
        },
        "solver": {
            "name": solver_name,
            "status": status,
            "time_cnf_generation": time_cnf,
            "time_sat_solve": time_sat,
            "time_total": time_cnf + time_sat
        }
    }

    if solution is not None:
        out['solution'] = {str(k): v for k, v in solution.items()}

    if solver_error is not None:
        out['solver']['error'] = solver_error

    if unsat_clauses is not None:
        # Convertiamo le clausole in lista di liste di interi
        out['solver']['unsat_clauses'] = [
            f"[{', '.join(map(str, clause))}, {ctype}]" for clause, ctype in unsat_clauses
        ]
    # Salva JSON
    fname = f"{output_dir}/experiment_{exp_id:03d}.json"
    with open(fname, 'w') as f:
        json.dump(out, f, indent=4)

    return fname
