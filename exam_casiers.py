import tkinter as tk


class LocationInvalide(Exception):
    pass


class Casier:
    def __init__(self, numero, pavillon,):
        self.__numero = numero
        self.__pavillon = pavillon
        self.__occupe = False

    def get_numero(self):
        return self.__numero

    def est_occupe(self):
        return self.__occupe

    def occuper(self):
        if self.__occupe:
            raise LocationInvalide(
                f"Le casier {self.__numero} est déjà occupé."
            )
        self.__occupe = True

    def liberer(self):
        self.__occupe = False


class Etudiant:
    DUREE_MAX = 8

    def __init__(self, matricule, nom):
        self.__matricule = matricule
        self.__nom = nom
        self.locations = []

    def get_nom(self):
        return self.__nom

    def duree_max(self):
        return self.DUREE_MAX


class EtudiantInternational(Etudiant):
    def __init__(self, matricule, nom, mois_supplementaires=4):
        super().__init__(matricule, nom)
        self.__mois_supplementaires = mois_supplementaires

    def duree_max(self):
        return super().duree_max() + self.__mois_supplementaires


class Location:
    def __init__(self, etudiant, casier, date_debut, nombre_mois, status="active"):
        duree_max = etudiant.duree_max()
        if nombre_mois <= 0 or nombre_mois > duree_max:
            raise LocationInvalide(
                f"Durée demandée : {nombre_mois} mois; maximum autorisé : "
                f"{duree_max} mois."
            )

        casier.occuper()
        self.etudiant = etudiant
        self.status = status
        self.casier = casier
        self.date_debut = date_debut
        self.nombre_mois = nombre_mois
        etudiant.locations.append(self)

    def resume(self):
        return (
            f"{self.etudiant.get_nom()} loue le casier "
            f"{self.casier.get_numero()} à partir du {self.date_debut} "
            f"pour {self.nombre_mois} mois."
        )


def ouvrir_interface():
    casiers = {
        1: Casier(1, "A"),
        2: Casier(2, "B"),
    }

    fenetre = tk.Tk()
    fenetre.title("Location de casier")
    fenetre.resizable(True, True)

    tk.Label(fenetre, text="Nom de l'étudiant :").grid(
        row=0, column=0, padx=10, pady=5, sticky="w"
    )
    champ_nom = tk.Entry(fenetre)
    champ_nom.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(fenetre, text="Numéro du casier (1 ou 2) :").grid(
        row=1, column=0, padx=10, pady=5, sticky="w"
    )
    champ_casier = tk.Entry(fenetre)
    champ_casier.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(fenetre, text="Date de début (AAAA-MM-JJ) :").grid(
        row=2, column=0, padx=10, pady=5, sticky="w"
    )
    champ_date = tk.Entry(fenetre)
    champ_date.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(fenetre, text="Nombre de mois :").grid(
        row=3, column=0, padx=10, pady=5, sticky="w"
    )
    champ_mois = tk.Entry(fenetre)
    champ_mois.grid(row=3, column=1, padx=10, pady=5)

    resultat = tk.Label(fenetre, text="", wraplength=360)
    resultat.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

    def creer_location():
        nom = champ_nom.get().strip()

        if not nom:
            resultat.config(text="Écris le nom de l'étudiant.")
            return

        try:
            numero_casier = int(champ_casier.get())
            nombre_mois = int(champ_mois.get())

            if numero_casier not in casiers:
                raise ValueError("Le numéro du casier doit être 1 ou 2.")

            etudiant = Etudiant("E001", nom)
            location = Location(
                etudiant,
                casiers[numero_casier],
                champ_date.get().strip(),
                nombre_mois,
            )
        except ValueError as erreur:
            resultat.config(text=f"Vérifie les informations : {erreur}")
        except LocationInvalide as erreur:
            resultat.config(text=str(erreur))
        else:
            resultat.config(text=location.resume())

    tk.Button(
        fenetre,
        text="Créer la location",
        command=creer_location,
    ).grid(row=4, column=0, columnspan=2, pady=10)

    fenetre.mainloop()


ouvrir_interface() 