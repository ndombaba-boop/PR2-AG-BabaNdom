"""
420-PR2-AG - Seance 7 - Bloc 2
Micro-exercice 2 : fermer une XSS et une CSRF.

Fichier de depart -- NE CORRIGEZ RIEN avant d'avoir repondu a la question 1.
Le harnais ci-dessous (Commentaire, DepotFictif, RequeteFictive) est deja
fourni pour que vous puissiez executer et tester ce fichier tel quel.

Consignes (voir diapo 27) :
1. Nommez les deux defauts et indiquez, pour chacun, la ligne exacte qui
   le porte.
2. Corrigez la XSS par un echappement adapte a chacun des deux contextes
   d'insertion.
3. Ecrivez la charge utile qui exploitait l'attribut auteur, et verifiez
   qu'elle ne fonctionne plus une fois corrigee.
4. Corrigez la CSRF : passez l'action en POST et ajoutez un jeton de
   synchronisation verifie.
5. Bonus : quel en-tete de cookie auriez-vous ajoute, et qu'aurait-il
   change pour chacun des deux defauts ?
"""

# --------------------------------------------------------------------------
# Harnais minimal -- ne pas modifier, sert seulement a executer/tester
# --------------------------------------------------------------------------
class Commentaire:
    def __init__(self, auteur, texte):
        self.auteur = auteur
        self.texte = texte


class DepotFictif:
    def __init__(self):
        self.comptes = {"ana": {"solde": 100}}

    def supprimer(self, utilisateur):
        self.comptes.pop(utilisateur, None)
        print(f"[depot] compte '{utilisateur}' supprime -- comptes restants : {list(self.comptes)}")


class RequeteFictive:
    def __init__(self, methode, session, donnees_formulaire=None):
        self.methode = methode
        self.session = session
        self.form = donnees_formulaire or {}


depot = DepotFictif()


# --------------------------------------------------------------------------
# TODO question 1 : sur quelles lignes, exactement, se trouvent les deux
# defauts ? Notez-les ici en commentaire avant de continuer.
# --------------------------------------------------------------------------

def page_commentaires(commentaires):
    lignes = [f"<li class={c.auteur}>{c.texte}</li>" for c in commentaires]
    return "<ul>" + "".join(lignes) + "</ul>"


def supprimer_compte(requete):                      # appelee par GET /compte/supprimer
    depot.supprimer(requete.session["utilisateur"])
    return "Compte supprime"


# --------------------------------------------------------------------------
# Zone de test -- executez ce fichier avant ET apres votre correction pour
# constater que les deux exploits ci-dessous cessent de fonctionner.
# --------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Test XSS ===")
    # TODO question 3 : completez la charge utile qui exploite l'attribut
    # auteur (indice : il manque des guillemets autour de l'attribut class)
    # commentaire_piege = Commentaire(auteur="???", texte="commentaire normal")
    # print(page_commentaires([commentaire_piege]))

    print()
    print("=== Test CSRF ===")
    # Une page piegee sur un autre site peut soumettre cette requete GET
    # sans qu'Ana ait rien clique de suspect -- tant que ce test supprime
    # bien le compte, le defaut n'est pas corrige.
    requete_piegee = RequeteFictive(methode="GET", session={"utilisateur": "ana"})
    print(supprimer_compte(requete_piegee))

    print()
    print("Une fois vos corrections faites, relancez ce fichier :")
    print(" - le test XSS ne doit plus produire de code HTML/JS actif")
    print(" - le test CSRF doit etre rejete (methode ou jeton invalide)")