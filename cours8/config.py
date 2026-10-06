import os


def secret_requis(nom):
    valeur = os.environ.get(nom)
    if not valeur:
        raise RuntimeError(
            f"Variable d'environnement manquante : {nom}")
    return valeur

def masquer(s, garde=4):
    return "*" * max(0, len(s) - garde) + s[-garde:]

CLE_API = secret_requis("CLE_API")
print("clé chargée :", masquer(CLE_API))