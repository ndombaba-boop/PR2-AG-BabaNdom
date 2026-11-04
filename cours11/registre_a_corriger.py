"""
420-PR2-AG — Laboratoire de synthèse — partie 6 : la chasse aux défauts

Ce service démarre, répond, et fait globalement ce qu'on lui demande.
Il contient pourtant CINQ défauts. Deux sont des failles de sécurité,
deux sont des écarts au contrat REST, un est les deux à la fois.

    REGISTRE_BD=chasse.db python3 registre_a_corriger.py
    python3 verifier_lab.py

Le script d'auto-évaluation en attrape chacun. Mais ne vous contentez pas
de lire ses échecs : pour chaque défaut, écrivez d'abord la ligne fautive
et ce qu'un attaquant peut en faire. Corrigez ensuite.
"""

import os
import sqlite3
from datetime import datetime

from flask import Flask, g, jsonify, request

CHEMIN = os.environ.get("REGISTRE_BD", "registre.db")

GENRES = ("ordinateur", "projecteur", "cable")
ROLES = ("etudiant", "responsable")
TRIS = {
    "etiquette": "e.etiquette ASC",
    "genre": "e.genre ASC, e.etiquette ASC",
    "date": "e.cree_le DESC",
}
TAILLE_MAX = 50

app = Flask(__name__)


# ====================================================================
# Base de données
# ====================================================================
def cnx():
    c = sqlite3.connect(CHEMIN)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c


def preparer():
    with cnx() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS compte (
                matricule TEXT PRIMARY KEY,
                nom       TEXT NOT NULL,
                role      TEXT NOT NULL CHECK (role IN ('etudiant','responsable')));

            CREATE TABLE IF NOT EXISTS equipement (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                etiquette  TEXT NOT NULL UNIQUE,
                genre      TEXT NOT NULL
                           CHECK (genre IN ('ordinateur','projecteur','cable')),
                detail     TEXT NOT NULL,
                emprunteur TEXT REFERENCES compte(matricule),
                cree_le    TEXT NOT NULL);

            CREATE TABLE IF NOT EXISTS pret (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                id_equipement INTEGER NOT NULL REFERENCES equipement(id),
                matricule     TEXT NOT NULL REFERENCES compte(matricule),
                emprunte_le   TEXT NOT NULL,
                rendu_le      TEXT);
        """)
        if c.execute("SELECT COUNT(*) AS n FROM compte").fetchone()["n"] == 0:
            c.executemany(
                "INSERT INTO compte (matricule, nom, role) VALUES (?, ?, ?)",
                [("1234567", "Alice Tremblay", "etudiant"),
                 ("7654321", "Bruno Gagnon", "etudiant"),
                 ("1111111", "Chantal Roy", "responsable")])
            maintenant = datetime.now().isoformat(timespec="seconds")
            c.executemany(
                "INSERT INTO equipement (etiquette, genre, detail, cree_le) "
                "VALUES (?, ?, ?, ?)",
                [("PORT-014", "ordinateur", "Linux, 16 Go", maintenant),
                 ("PORT-015", "ordinateur", "Windows, 8 Go", maintenant),
                 ("PORT-016", "ordinateur", "Linux, 32 Go", maintenant),
                 ("PROJ-003", "projecteur", "3200 lumens", maintenant),
                 ("PROJ-004", "projecteur", "2000 lumens", maintenant),
                 ("CABL-021", "cable", "HDMI 3 m", maintenant),
                 ("CABL-022", "cable", "USB-C 1 m", maintenant),
                 ("CABL-023", "cable", "Ethernet 5 m", maintenant)])


# ====================================================================
# Erreurs : une seule forme sur toutes les routes
# ====================================================================
class DonneeInvalide(Exception):
    def __init__(self, message, champ=None):
        super().__init__(message)
        self.champ = champ


def echec(code_http, code, message, champ=None):
    corps = {"erreur": code, "message": message}
    if champ:
        corps["champ"] = champ
    return jsonify(corps), code_http


@app.errorhandler(404)
def introuvable(_):
    return echec(404, "introuvable", "Cette ressource n'existe pas.")


@app.errorhandler(405)
def methode(_):
    return echec(405, "methode_non_permise", "Méthode non permise sur ce chemin.")


# ====================================================================
# Identification de l'appelant
#
# ATTENTION : lire un matricule dans un en-tête n'est PAS de
# l'authentification. N'importe qui peut écrire n'importe quel matricule.
# On corrige cela à la séance 12, avec un jeton signé.
# ====================================================================
def identifier():
    matricule = request.headers.get("X-Matricule", "").strip()
    if not matricule:
        return None
    with cnx() as c:
        r = c.execute("SELECT matricule, nom, role FROM compte WHERE matricule = ?",
                      (matricule,)).fetchone()
    return dict(r) if r else None


def protege(fonction):
    def enveloppe(*args, **kwargs):
        g.appelant = identifier()
        if g.appelant is None:
            return echec(401, "non_authentifie",
                         "En-tête X-Matricule absent ou inconnu.")
        return fonction(*args, **kwargs)
    enveloppe.__name__ = fonction.__name__
    return enveloppe


# ====================================================================
# Validation — listes blanches et bornes
# ====================================================================
def texte(valeur, champ, mini=1, maxi=60):
    if not isinstance(valeur, str) or not mini <= len(valeur.strip()) <= maxi:
        raise DonneeInvalide(f"{champ} : de {mini} à {maxi} caractères.", champ)
    return valeur.strip()


def dans(valeur, permises, champ):
    if valeur not in permises:
        raise DonneeInvalide(
            f"{champ} doit valoir : {', '.join(permises)}.", champ)
    return valeur


def entier(valeur, defaut, mini, maxi, champ):
    if valeur is None:
        return defaut
    try:
        n = int(valeur)
    except (TypeError, ValueError):
        raise DonneeInvalide(f"{champ} doit être un entier.", champ)
    if not mini <= n <= maxi:
        raise DonneeInvalide(f"{champ} doit être entre {mini} et {maxi}.", champ)
    return n


def corps_json():
    donnees = request.get_json(silent=True)
    if not isinstance(donnees, dict):
        raise DonneeInvalide("Le corps doit être un objet JSON.")
    return donnees


@app.errorhandler(DonneeInvalide)
def donnee_invalide(e):
    return echec(422, "donnee_invalide", str(e), e.champ)


# ====================================================================
# Routes
# ====================================================================
@app.get("/sante")
def sante():
    return jsonify({"etat": "ok", "version": "1.0.0"}), 200


@app.get("/equipements")
@protege
def lister():
    genre = request.args.get("genre")
    if genre is not None:
        dans(genre, GENRES, "genre")
    libre = request.args.get("libre")
    if libre is not None:
        dans(libre, ("0", "1"), "libre")
    tri = request.args.get("tri", "e.etiquette ASC")
    page = entier(request.args.get("page"), 1, 1, 10_000, "page")
    taille = int(request.args.get("taille", 20))

    #   sont liées. Le tri vient de TRIS, jamais du client.
    conditions, params = ["1 = 1"], []
    if genre is not None:
        conditions.append("e.genre = ?")
        params.append(genre)
    if libre == "1":
        conditions.append("e.emprunteur IS NULL")
    elif libre == "0":
        conditions.append("e.emprunteur IS NOT NULL")
    params.extend([taille, (page - 1) * taille])

    sql = (f"SELECT e.id, e.etiquette, e.genre, e.detail, e.emprunteur "
           f"FROM equipement AS e WHERE {' AND '.join(conditions)} "
           f"ORDER BY {tri} LIMIT ? OFFSET ?")
    with cnx() as c:
        lignes = c.execute(sql, params).fetchall()
    return jsonify([dict(r) for r in lignes]), 200


@app.get("/equipements/<int:id_eq>")
@protege
def lire(id_eq):
    with cnx() as c:
        r = c.execute("SELECT id, etiquette, genre, detail, emprunteur, cree_le "
                      "FROM equipement WHERE id = ?", (id_eq,)).fetchone()
    return jsonify(dict(r) if r else None), 200


@app.post("/equipements")
@protege
def enregistrer():
    d = corps_json()
    etiquette = texte(d.get("etiquette"), "etiquette", 3, 20)
    genre = dans(d.get("genre"), GENRES, "genre")
    detail = texte(d.get("detail"), "detail", 1, 120)
    with cnx() as c:
        existe = c.execute("SELECT 1 FROM equipement WHERE etiquette = ?",
                           (etiquette,)).fetchone()
        if existe:
            return echec(409, "etiquette_prise", "Cette étiquette existe déjà.")
        cur = c.execute(
            "INSERT INTO equipement (etiquette, genre, detail, cree_le) "
            "VALUES (?, ?, ?, ?)",
            (etiquette, genre, detail,
             datetime.now().isoformat(timespec="seconds")))
        id_eq = cur.lastrowid
    return (jsonify({"id": id_eq, "etiquette": etiquette, "genre": genre,
                     "detail": detail, "emprunteur": None}), 201,
            {"Location": f"/equipements/{id_eq}"})


@app.post("/emprunts")
@protege
def emprunter():
    d = corps_json()
    id_eq = entier(d.get("id_equipement"), None, 1, 10**9, "id_equipement")
    if id_eq is None:
        raise DonneeInvalide("id_equipement est obligatoire.", "id_equipement")
    maintenant = datetime.now().isoformat(timespec="seconds")
    with cnx() as c:
        eq = c.execute("SELECT id, etiquette, emprunteur FROM equipement "
                       "WHERE id = ?", (id_eq,)).fetchone()
        if eq is None:
            return echec(404, "introuvable", "Cet équipement n'existe pas.")
        if eq["emprunteur"] is not None:
            return echec(409, "deja_prete",
                         "Cet équipement est déjà prêté.")
        c.execute("UPDATE equipement SET emprunteur = ? WHERE id = ?",
                  (g.appelant["matricule"], id_eq))
        cur = c.execute(
            "INSERT INTO pret (id_equipement, matricule, emprunte_le) "
            "VALUES (?, ?, ?)", (id_eq, g.appelant["matricule"], maintenant))
        id_pret = cur.lastrowid
    return (jsonify({"id_pret": id_pret, "id_equipement": id_eq,
                     "matricule": g.appelant["matricule"],
                     "emprunte_le": maintenant}), 201,
            {"Location": f"/emprunts/{id_eq}"})


@app.delete("/emprunts/<int:id_eq>")
@protege
def rendre(id_eq):
    maintenant = datetime.now().isoformat(timespec="seconds")
    with cnx() as c:
        eq = c.execute("SELECT id, emprunteur FROM equipement WHERE id = ?",
                       (id_eq,)).fetchone()
        if eq is None:
            return echec(404, "introuvable", "Cet équipement n'existe pas.")
        if eq["emprunteur"] is None:
            return echec(409, "non_prete", "Cet équipement n'est pas prêté.")
        c.execute("UPDATE equipement SET emprunteur = NULL WHERE id = ?", (id_eq,))
        c.execute("UPDATE pret SET rendu_le = ? "
                  "WHERE id_equipement = ? AND rendu_le IS NULL",
                  (maintenant, id_eq))
    return "", 204


@app.get("/prets")
@protege
def prets():
    if g.appelant["role"] != "responsable":
        return echec(403, "acces_refuse",
                     "L'historique des prêts est réservé aux responsables.")
    if request.args.get("resume") == "1":
        with cnx() as c:
            lignes = c.execute(
                "SELECT e.genre, "
                "       COUNT(*) AS nombre, "
                "       SUM(CASE WHEN p.rendu_le IS NULL THEN 1 ELSE 0 END) "
                "         AS en_cours "
                "FROM pret AS p "
                "JOIN equipement AS e ON e.id = p.id_equipement "
                "GROUP BY e.genre ORDER BY nombre DESC").fetchall()
        return jsonify([dict(r) for r in lignes]), 200
    with cnx() as c:
        lignes = c.execute(
            "SELECT p.id, e.etiquette, e.genre, c.nom, p.emprunte_le, p.rendu_le "
            "FROM pret AS p "
            "JOIN equipement AS e ON e.id = p.id_equipement "
            "JOIN compte AS c ON c.matricule = p.matricule "
            "ORDER BY p.emprunte_le DESC, p.id DESC LIMIT 100").fetchall()
    return jsonify([dict(r) for r in lignes]), 200


preparer()

if __name__ == "__main__":
    # threaded=False : une seule requête à la fois, pour éviter les surprises
    # de SQLite entre fils d'exécution.
    app.run(port=int(os.environ.get("PORT", 5000)), debug=False, threaded=False)
