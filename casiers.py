class LocationInvalide(Exception):
    pass


class Casier:
    def __init__(self, numero, pavillon,):
        self.__numero = numero
        self.__pavillon = pavillon
        self.__occupe = False

    def get_numero(self):
        return self.__numero

    def get_pavillon(self):
        return self.__pavillon

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


casier_1 = Casier(1, "A")
casier_2 = Casier(2, "B")
etudiant = Etudiant("E001", "Alice")
etudiant_international = EtudiantInternational("E002", "Bob")

import tkinter as tk
from tkinter import messagebox, ttk


class ApplicationCasiers:
    def __init__(self, fenetre):
        self.fenetre = fenetre
        self.fenetre.title("Gestion des casiers")
        self.fenetre.geometry("760x500")
        self.fenetre.minsize(680, 430)

        self.casiers = [Casier(1, "A"), Casier(2, "B")]
        self.etudiants = [
            Etudiant("E001", "Alice"),
            EtudiantInternational("E002", "Bob"),
        ]
        self.locations = []

        self.creer_interface()
        self.actualiser_tableau()

    def creer_interface(self):
        cadre_principal = ttk.Frame(self.fenetre, padding=16)
        cadre_principal.pack(fill="both", expand=True)

        ttk.Label(
            cadre_principal,
            text="Gestion des locations de casiers",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w", pady=(0, 14))

        cadre_formulaire = ttk.LabelFrame(
            cadre_principal, text="Nouvelle location", padding=12
        )
        cadre_formulaire.pack(fill="x", pady=(0, 14))

        ttk.Label(cadre_formulaire, text="Étudiant").grid(row=0, column=0, sticky="w")
        self.etudiant_var = tk.StringVar()
        self.etudiant_combo = ttk.Combobox(
            cadre_formulaire,
            textvariable=self.etudiant_var,
            state="readonly",
            width=24,
            values=[f"{etudiant.get_nom()} ({etudiant.__class__.__name__})"
                    for etudiant in self.etudiants],
        )
        self.etudiant_combo.grid(row=1, column=0, padx=(0, 12), pady=(4, 0))
        self.etudiant_combo.current(0)

        ttk.Label(cadre_formulaire, text="Casier disponible").grid(
            row=0, column=1, sticky="w"
        )
        self.casier_var = tk.StringVar()
        self.casier_combo = ttk.Combobox(
            cadre_formulaire,
            textvariable=self.casier_var,
            state="readonly",
            width=18,
        )
        self.casier_combo.grid(row=1, column=1, padx=(0, 12), pady=(4, 0))

        ttk.Label(cadre_formulaire, text="Date de début").grid(
            row=0, column=2, sticky="w"
        )
        self.date_var = tk.StringVar(value="2026-09-01")
        ttk.Entry(cadre_formulaire, textvariable=self.date_var, width=15).grid(
            row=1, column=2, padx=(0, 12), pady=(4, 0)
        )

        ttk.Label(cadre_formulaire, text="Durée (mois)").grid(
            row=0, column=3, sticky="w"
        )
        self.duree_var = tk.StringVar(value="1")
        ttk.Spinbox(
            cadre_formulaire, from_=1, to=12, textvariable=self.duree_var, width=8
        ).grid(row=1, column=3, padx=(0, 12), pady=(4, 0))

        ttk.Button(
            cadre_formulaire, text="Louer le casier", command=self.creer_location
        ).grid(row=1, column=4, pady=(4, 0))

        self.casier_combo.bind("<<ComboboxSelected>>", self.actualiser_duree_max)
        self.actualiser_casiers_disponibles()

        cadre_locations = ttk.LabelFrame(
            cadre_principal, text="Locations actives", padding=10
        )
        cadre_locations.pack(fill="both", expand=True)

        colonnes = ("casier", "pavillon", "etudiant", "date", "duree")
        self.tableau = ttk.Treeview(
            cadre_locations, columns=colonnes, show="headings", height=10
        )
        titres = {
            "casier": "Casier",
            "pavillon": "Pavillon",
            "etudiant": "Étudiant",
            "date": "Début",
            "duree": "Durée",
        }
        largeurs = {"casier": 80, "pavillon": 90, "etudiant": 180, "date": 120, "duree": 100}
        for colonne in colonnes:
            self.tableau.heading(colonne, text=titres[colonne])
            self.tableau.column(colonne, width=largeurs[colonne], anchor="center")
        self.tableau.pack(fill="both", expand=True)

        ttk.Button(
            cadre_principal, text="Libérer la location sélectionnée",
            command=self.liberer_location,
        ).pack(anchor="e", pady=(10, 0))

    def trouver_etudiant(self):
        return self.etudiants[self.etudiant_combo.current()]

    def trouver_casier(self):
        index = self.casier_combo.current()
        if index < 0:
            return None
        casiers_disponibles = [casier for casier in self.casiers if not casier.est_occupe()]
        return casiers_disponibles[index]

    def actualiser_casiers_disponibles(self):
        casiers_disponibles = [
            f"{casier.get_numero()} (pavillon {casier.get_pavillon()})"
            for casier in self.casiers if not casier.est_occupe()
        ]
        self.casier_combo["values"] = casiers_disponibles
        if casiers_disponibles:
            self.casier_combo.current(0)
        else:
            self.casier_var.set("Aucun casier disponible")
        self.actualiser_duree_max()

    def actualiser_duree_max(self, _evenement=None):
        if self.etudiants:
            etudiant = self.trouver_etudiant()
            self.duree_var.set(min(int(self.duree_var.get() or 1), etudiant.duree_max()))

    def creer_location(self):
        try:
            casier = self.trouver_casier()
            if casier is None:
                raise LocationInvalide("Aucun casier n'est disponible.")
            nombre_mois = int(self.duree_var.get())
            location = Location(
                self.trouver_etudiant(), casier, self.date_var.get(), nombre_mois
            )
            self.locations.append(location)
            messagebox.showinfo("Location créée", location.resume())
            self.actualiser_tableau()
        except (LocationInvalide, ValueError) as erreur:
            messagebox.showerror("Location impossible", str(erreur))

    def actualiser_tableau(self):
        for element in self.tableau.get_children():
            self.tableau.delete(element)
        for index, location in enumerate(self.locations):
            self.tableau.insert(
                "", "end", iid=str(index),
                values=(
                    location.casier.get_numero(),
                    location.casier.get_pavillon(),
                    location.etudiant.get_nom(),
                    location.date_debut,
                    f"{location.nombre_mois} mois",
                ),
            )
        self.actualiser_casiers_disponibles()

    def liberer_location(self):
        selection = self.tableau.selection()
        if not selection:
            messagebox.showwarning("Aucune sélection", "Sélectionne une location à libérer.")
            return
        location = self.locations.pop(int(selection[0]))
        location.casier.liberer()
        location.status = "terminee"
        location.etudiant.locations.remove(location)
        self.actualiser_tableau()



fenetre = tk.Tk()
ApplicationCasiers(fenetre)
fenetre.mainloop()