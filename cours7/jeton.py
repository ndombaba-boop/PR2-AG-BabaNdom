"""
420-PR2-AG - Seance 7 - Bloc 1
Micro-exercice 1 : fabriquer et verifier un jeton JWT a la main.

A COMPLETER : les fonctions marquees TODO. Le reste est deja fourni
pour que vous puissiez vous concentrer sur la partie cryptographique.

Consignes (voir diapo 13) :
1. Fabriquez un jeton pour "ana" avec le role "lecteur" et une expiration
   dans une heure, puis verifiez-le.
2. Decodez la charge, remplacez "lecteur" par "admin", re-encodez-la et
   recollez la signature d'origine.
3. Soumettez ce jeton falsifie a verifier() et notez le message obtenu.
4. Fabriquez un jeton dont l'en-tete annonce {"alg": "none"} et dont la
   signature est vide -- que fait votre verification ?
5. Creez un jeton dont l'expiration est deja passee, et verifiez qu'il
   est bien refuse.
6. Question (pas de code) : que se passerait-il si verifier() lisait la
   charge AVANT de controler la signature ?
"""
import base64
import hmac
import hashlib
from inspect import signature
import json
import time

# Le secret ne quitte JAMAIS le serveur : ni dans le jeton, ni cote client.
SECRET = b"cle-secrete-du-serveur"


def b64url(donnees: bytes) -> str:
    """Encode des octets en base64url, sans le remplissage '='."""
    return base64.urlsafe_b64encode(donnees).rstrip(b"=").decode()


def deb64(texte: str) -> bytes:
    """Decode une chaine base64url (remplissage '=' recalcule au besoin)."""
    return base64.urlsafe_b64decode(texte + "=" * (-len(texte) % 4))


def creer(charge: dict) -> str:
    """Fabrique un JWT signe a partir d'un dictionnaire de charge utile."""
    # TODO 1 : encoder l'en-tete {"alg": "HS256", "typ": "JWT"} avec b64url()
    entete = b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())

    # TODO 2 : encoder la charge (le parametre `charge`) avec b64url()
    corps = b64url(json.dumps(charge).encode())

    # TODO 3 : calculer la signature = HMAC-SHA256(entete + "." + corps, SECRET)
    #          (utilisez hmac.new(...).digest(), puis encodez le resultat en b64url)
    signature = b64url(hmac.new(SECRET, (entete + "." + corps).encode(), hashlib.sha256).digest()) 

    # TODO 4 : retourner le jeton complet "entete.corps.signature"
    return f"{entete}.{corps}.{signature}"



def verifier(jeton: str) -> dict:
    """Verifie un JWT et retourne sa charge si tout est valide.

    Ordre impose (voir diapo 12, colonne de droite) :
      1. Verifier la signature D'ABORD, avant de faire quoi que ce soit
         d'autre avec le contenu du jeton.
      2. Verifier l'expiration ENSUITE.
    """
    entete, corps, signature = jeton.split(".")

    # TODO 1 : recalculer la signature attendue, exactement comme dans creer()
    signature_attendue = b64url(hmac.new(SECRET, (entete + "." + corps).encode(), hashlib.sha256).digest())

    # TODO 2 : comparer `signature` a `signature_attendue`.
    #          Utilisez hmac.compare_digest(...) -- JAMAIS l'operateur ==
    #         (voir la note "compare_digest, jamais ==" de la diapo 12).
    #          Si la comparaison echoue : raise ValueError("Signature invalide")
    if not hmac.compare_digest(signature, signature_attendue):
        raise ValueError("Signature invalide")

    # TODO 3 : decoder la charge avec deb64() + json.loads(), SEULEMENT
    #          apres que la signature ait ete validee ci-dessus.
    charge = json.loads(deb64(corps))

    # TODO 4 : verifier charge.get("exp", 0) contre time.time().
    #          Si le jeton est expire : raise ValueError("Jeton expire")
    if charge.get("exp", 0) < time.time():
        raise ValueError("Jeton expire")

    return charge




# Etape 1 de l'exercice : decommentez et completez une fois creer()/verifier() prets
jeton = creer({"sub": "ana", "role": "lecteur", "exp": int(time.time()) + 3600})
print("Jeton fabrique :", jeton)
print("Jeton verifie  :", verifier(jeton))
pass 

def falsifier(jeton: str) -> str:
    """Falsifie un jeton en changeant le role de la charge utile."""
    entete, corps, signature = jeton.split(".")
    charge = json.loads(deb64(corps))
    charge["role"] = "admin"
    corps_falsifie = b64url(json.dumps(charge).encode())
    return f"{entete}.{corps_falsifie}.{signature}"


def jeton_none() -> str:
    """Fabrique un jeton avec l'algorithme 'none' et une signature vide."""
    entete = b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode())
    corps = b64url(json.dumps({"sub": "ana", "role": "lecteur", "exp": int(time.time()) + 3600}).encode())
    return f"{entete}.{corps}."

print("falsification :", falsifier(jeton))
print("Jeton  verifie :", verifier(jeton_none()))

def jeton_expire() -> str:
    """Fabrique un jeton deja expire."""
    entete = b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    corps = b64url(json.dumps({"sub": "ana", "role": "lecteur", "exp": int(time.time()) - 3600}).encode())
    signature = b64url(hmac.new(SECRET, (entete + "." + corps).encode(), hashlib.sha256).digest())
    return f"{entete}.{corps}.{signature}"

print("Jeton expire :", jeton_expire())
print("Jeton verifie :", verifier(jeton_expire()))
