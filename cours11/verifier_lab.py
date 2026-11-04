#!/usr/bin/env python3
"""
420-PR2-AG — Laboratoire de synthèse — auto-évaluation

Lancez votre service dans un terminal, puis ce script dans un autre.

    python3 registre_depart.py
    python3 verifier_lab.py

Il regroupe ses 26 contrôles par partie du laboratoire. Au début, tout
échoue : c'est normal, vous n'avez rien écrit. Relancez-le après chaque
route terminée et regardez la ligne de total monter.

Aucune bibliothèque à installer.
"""

import json
import sys
import time
import urllib.error
import urllib.request

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:5000"
ALICE = "1234567"        # étudiante
BRUNO = "7654321"        # étudiant
CHANTAL = "1111111"      # responsable

resultats = []
_partie = [""]


def partie(nom):
    _partie[0] = nom
    print(f"\n{nom}")
    print("-" * len(nom))


def verifier(libelle, condition, detail=""):
    resultats.append((_partie[0], libelle, bool(condition)))
    print(f"  {'RÉUSSI ' if condition else 'ÉCHEC  '} {libelle}")
    if not condition and detail:
        print(f"           → {detail}")


def appeler(methode, chemin, corps=None, matricule=None):
    entetes = {}
    donnees = None
    if corps is not None:
        donnees = json.dumps(corps).encode()
        entetes["Content-Type"] = "application/json"
    if matricule is not None:
        entetes["X-Matricule"] = matricule
    requete = urllib.request.Request(BASE + chemin, data=donnees,
                                     headers=entetes, method=methode)
    try:
        with urllib.request.urlopen(requete, timeout=10) as r:
            return r.status, _json(r.read()), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, _json(e.read()), dict(e.headers)
    except Exception as e:
        return 0, {"erreur_transport": str(e)}, {}


def _json(brut):
    if not brut:
        return None
    try:
        return json.loads(brut)
    except Exception:
        return {"corps_non_json": brut[:160].decode("utf-8", "replace")}


def attendre():
    for _ in range(30):
        if appeler("GET", "/sante")[0] == 200:
            return True
        time.sleep(0.5)
    return False


def etiquette_neuve():
    return "LAB-" + str(int(time.time()) % 100000)


def main():
    print(f"Auto-évaluation du service à {BASE}")
    if not attendre():
        print("\nAucune réponse sur GET /sante. Le service est-il démarré ?")
        raise SystemExit(2)

    # ================================================================
    partie("Partie 2 — Lire")
    # ================================================================
    code, corps, _ = appeler("GET", "/sante")
    verifier("GET /sante répond 200 sans en-tête", code == 200, f"reçu {code}")

    code, _, _ = appeler("GET", "/equipements")
    verifier("GET /equipements sans X-Matricule répond 401", code == 401,
             f"reçu {code}")

    code, liste, _ = appeler("GET", "/equipements", matricule=ALICE)
    verifier("GET /equipements répond 200 et renvoie une liste",
             code == 200 and isinstance(liste, list), f"reçu {code}")
    verifier("La liste contient les huit équipements d'essai",
             isinstance(liste, list) and len(liste) >= 8,
             f"{len(liste) if isinstance(liste, list) else '?'} élément(s)")

    code, eq, _ = appeler("GET", "/equipements/1", matricule=ALICE)
    verifier("GET /equipements/1 répond 200 avec l'équipement",
             code == 200 and isinstance(eq, dict) and "etiquette" in eq,
             f"reçu {code} — {eq}")

    code, _, _ = appeler("GET", "/equipements/999999", matricule=ALICE)
    verifier("GET /equipements/999999 répond 404", code == 404, f"reçu {code}")

    # ================================================================
    partie("Partie 3 — Créer, emprunter, rendre")
    # ================================================================
    code, _, _ = appeler("POST", "/equipements",
                         {"etiquette": etiquette_neuve() + "A", "genre": "cable",
                          "detail": "essai"}, matricule=ALICE)
    verifier("Un étudiant ne peut pas enregistrer un équipement (403)",
             code == 403, f"reçu {code}")

    etiq = etiquette_neuve() + "B"
    code, cree, entetes = appeler("POST", "/equipements",
                                  {"etiquette": etiq, "genre": "cable",
                                   "detail": "essai"}, matricule=CHANTAL)
    id_neuf = cree.get("id") if isinstance(cree, dict) else None
    verifier("Un responsable enregistre un équipement (201)", code == 201,
             f"reçu {code}")
    verifier("La création renvoie un en-tête Location",
             "Location" in entetes or "location" in entetes,
             "aucun en-tête Location dans la réponse")

    code, _, _ = appeler("POST", "/equipements",
                         {"etiquette": etiq, "genre": "cable", "detail": "essai"},
                         matricule=CHANTAL)
    verifier("Une étiquette déjà prise répond 409", code == 409, f"reçu {code}")

    code, _, _ = appeler("POST", "/equipements",
                         {"etiquette": "X", "genre": "avion", "detail": ""},
                         matricule=CHANTAL)
    verifier("Un genre hors liste blanche répond 422, jamais 500",
             code == 422, f"reçu {code}")

    code, _, _ = appeler("POST", "/emprunts", {"id_equipement": id_neuf},
                         matricule=ALICE)
    verifier("Alice emprunte l'équipement (201)", code == 201, f"reçu {code}")

    code, _, _ = appeler("POST", "/emprunts", {"id_equipement": id_neuf},
                         matricule=BRUNO)
    verifier("Bruno ne peut pas emprunter le même équipement (409)",
             code == 409, f"reçu {code}")

    code, _, _ = appeler("POST", "/emprunts", {"id_equipement": 999999},
                         matricule=ALICE)
    verifier("Emprunter un équipement inexistant répond 404", code == 404,
             f"reçu {code}")

    code, _, _ = appeler("DELETE", f"/emprunts/{id_neuf}", matricule=BRUNO)
    verifier("Bruno ne peut pas rendre l'emprunt d'Alice (403)", code == 403,
             f"reçu {code}")

    code, corps, _ = appeler("DELETE", f"/emprunts/{id_neuf}", matricule=ALICE)
    verifier("Alice rend son emprunt : 204 et aucun corps",
             code == 204 and not corps, f"reçu {code}, corps={corps}")

    code, _, _ = appeler("DELETE", f"/emprunts/{id_neuf}", matricule=ALICE)
    verifier("Rendre un équipement non prêté répond 409", code == 409,
             f"reçu {code}")

    # ================================================================
    partie("Partie 4 — Filtrer, trier, paginer")
    # ================================================================
    code, liste, _ = appeler("GET", "/equipements?genre=cable", matricule=ALICE)
    verifier("Le filtre genre ne renvoie que ce genre",
             code == 200 and isinstance(liste, list) and liste
             and all(e.get("genre") == "cable" for e in liste),
             f"reçu {code} — {liste}")

    code, liste, _ = appeler("GET", "/equipements?taille=3", matricule=ALICE)
    verifier("Le paramètre taille limite le nombre d'éléments",
             code == 200 and isinstance(liste, list) and len(liste) == 3,
             f"{len(liste) if isinstance(liste, list) else '?'} élément(s)")

    code, p1, _ = appeler("GET", "/equipements?taille=2&page=1", matricule=ALICE)
    code2, p2, _ = appeler("GET", "/equipements?taille=2&page=2", matricule=ALICE)
    ids1 = [e.get("id") for e in p1] if isinstance(p1, list) else []
    ids2 = [e.get("id") for e in p2] if isinstance(p2, list) else []
    verifier("La page 2 ne répète pas la page 1",
             code == 200 and code2 == 200 and ids1 and ids2
             and not set(ids1) & set(ids2),
             f"page 1 : {ids1}, page 2 : {ids2}")

    code, liste, _ = appeler("GET", "/equipements?tri=etiquette&taille=50",
                             matricule=ALICE)
    etiquettes = [e.get("etiquette") for e in liste] if isinstance(liste, list) else []
    verifier("Le tri par étiquette renvoie une liste ordonnée",
             code == 200 and etiquettes == sorted(etiquettes),
             f"reçu {code} — {etiquettes[:4]}")

    code, _, _ = appeler("GET", "/equipements?tri=1;DROP%20TABLE%20equipement--",
                         matricule=ALICE)
    code_apres, _, _ = appeler("GET", "/equipements", matricule=ALICE)
    verifier("Un tri hors liste blanche est refusé et la table survit",
             code in (400, 422) and code_apres == 200,
             f"tri {code}, lecture après {code_apres}")

    code, _, _ = appeler("GET", "/equipements?taille=abc", matricule=ALICE)
    verifier("Une taille non numérique répond 422, jamais 500", code == 422,
             f"reçu {code}")

    # ================================================================
    partie("Partie 5 — Jointure et agrégat")
    # ================================================================
    code, _, _ = appeler("GET", "/prets", matricule=ALICE)
    verifier("Un étudiant ne peut pas lire l'historique des prêts (403)",
             code == 403, f"reçu {code}")

    code, lignes, _ = appeler("GET", "/prets", matricule=CHANTAL)
    a_jointure = (isinstance(lignes, list) and lignes
                  and all(k in lignes[0] for k in ("etiquette", "nom")))
    verifier("GET /prets joint les prêts aux équipements et aux comptes",
             code == 200 and a_jointure,
             f"reçu {code} — la réponse doit porter l'étiquette ET le nom")

    code, resume, _ = appeler("GET", "/prets?resume=1", matricule=CHANTAL)
    a_agregat = (isinstance(resume, list) and resume
                 and "genre" in resume[0] and "nombre" in resume[0])
    verifier("GET /prets?resume=1 renvoie un décompte par genre",
             code == 200 and a_agregat, f"reçu {code} — {resume}")

    # ================================================================
    print()
    print("=" * 58)
    for nom in ["Partie 2", "Partie 3", "Partie 4", "Partie 5"]:
        lot = [r for r in resultats if r[0].startswith(nom)]
        n = sum(1 for _, _, ok in lot if ok)
        print(f"  {lot[0][0]:<44} {n:>2} / {len(lot)}")
    reussis = sum(1 for _, _, ok in resultats if ok)
    print("=" * 58)
    print(f"  TOTAL {reussis} / {len(resultats)}")
    print()
    raise SystemExit(0 if reussis == len(resultats) else 1)


if __name__ == "__main__":
    main()
