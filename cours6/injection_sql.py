

import sqlite3 


def chercher_employe(nom):
    conn = sqlite3.connect('employer.db')
    request = f"SELECT * FROM employer WHERE nom = ?"
    result = conn.execute(request, (nom,)).fetchall()
    conn.close()
    return result

print(chercher_employe("x' OR '1'='1"))  # Example usage