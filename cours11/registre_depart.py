"""
420-PR2-AG — Laboratoire de synthèse (séances 10 et 11) — À COMPLÉTER

Le registre de prêt d'équipement, publié comme service REST.

    pip install flask
    python3 registre_depart.py           # http://localhost:5000
    python3 verifier_lab.py              # dans un autre terminal

Ce qui est déjà fait, et que vous n'avez pas à écrire :
  - la base de données, son schéma et ses données d'essai ;
  - la forme unique des messages d'erreur ;
  - l'identification de l'appelant par l'en-tête X-Matricule ;
  - les quatre fonctions de validation : texte, dans, entier, corps_json ;
  - la route GET /sante, qui vous sert de modèle.

Ce qui vous reste : les six routes marquées « À FAIRE ».
Après chaque route terminée, relancez verifier_lab.py.
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
    # ------------------------------------------------------------------
    # À FAIRE — GET /equipements/{id} — partie 2
    #
    #   200 avec l'équipement, 404 s'il n'existe pas.
    #   Le paramètre id_eq vous est déjà donné par Flask.
    # ------------------------------------------------------------------
    return echec(501, "non_implemente", "Cette route reste à écrire.")



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
    # ------------------------------------------------------------------
    # À FAIRE — POST /equipements — partie 3
    #
    #   Réservé au rôle responsable : 403 sinon.
    #   Validez etiquette, genre et detail avec texte() et dans().
    #   409 si l'étiquette existe déjà.
    #   201 avec un en-tête Location vers la ressource créée.
    # ------------------------------------------------------------------
    return echec(501, "non_implemente", "Cette route reste à écrire.")



@app.post("/emprunts")
@protege
def emprunter():
    # ------------------------------------------------------------------
    # À FAIRE — POST /emprunts — partie 3
    #
    #   Le corps contient id_equipement.
    #   404 si l'équipement n'existe pas, 409 s'il est déjà prêté.
    #   Mettez à jour equipement.emprunteur ET insérez une ligne dans pret.
    #   201 avec un en-tête Location.
    # ------------------------------------------------------------------
    return echec(501, "non_implemente", "Cette route reste à écrire.")



@app.delete("/emprunts/<int:id_eq>")
@protege
def rendre(id_eq):
    # ------------------------------------------------------------------
    # À FAIRE — DELETE /emprunts/{id} — partie 3
    #
    #   404 si l'équipement n'existe pas, 409 s'il n'est pas prêté.
    #   403 si l'emprunt n'est pas le vôtre — sauf pour un responsable.
    #   Remettez emprunteur à NULL et datez rendu_le.
    #   204, et aucun corps.
    # ------------------------------------------------------------------
    return echec(501, "non_implemente", "Cette route reste à écrire.")



@app.get("/prets")
@protege
def prets():
    # ------------------------------------------------------------------
    # À FAIRE — GET /prets — partie 5
    #
    #   Réservé au rôle responsable : 403 sinon.
    #   Sans paramètre : une JOINTURE entre pret, equipement et compte.
    #   Avec ?resume=1 : un AGRÉGAT — GROUP BY sur le genre, avec COUNT.
    #   Dans les deux cas, c'est la base qui travaille, pas Python.
    # ------------------------------------------------------------------
    return echec(501, "non_implemente", "Cette route reste à écrire.")



preparer()

if __name__ == "__main__":
    # threaded=False : une seule requête à la fois, pour éviter les surprises
    # de SQLite entre fils d'exécution.
    app.run(port=int(os.environ.get("PORT", 5000)), debug=False, threaded=False)
