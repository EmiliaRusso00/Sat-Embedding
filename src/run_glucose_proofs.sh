#!/bin/bash

# Cartella base dove ci sono le sottocartelle con i CNF
BASE_DIR="../outputs"

# Percorso all'eseguibile di Glucose
GLUCOSE="../glucose/simp/glucose_release"

# Controllo che l'eseguibile esista
if [ ! -f "$GLUCOSE" ]; then
    echo "Errore: non ho trovato $GLUCOSE"
    exit 1
fi

# Cicla su tutte le cartelle numerate in outputs
for DIR in "$BASE_DIR"/*; do
    if [ -d "$DIR" ]; then
        # Cerca il file .cnf dentro la cartella
        CNF_FILE=$(find "$DIR" -maxdepth 1 -name "*.cnf")
        if [ -f "$CNF_FILE" ]; then
            # Nome del file proof
            PROOF_FILE="$DIR/proof.txt"

            echo "Eseguo Glucose su $CNF_FILE, scrivo proof in $PROOF_FILE"
            
            # Esegui Glucose
            "$GLUCOSE" -model -verb=0 -proof="$PROOF_FILE" "$CNF_FILE"

            echo "Done!"
        else
            echo "Nessun file .cnf trovato in $DIR"
        fi
    fi
done

echo "Tutti i CNF elaborati."
