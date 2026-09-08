class Salle :
    def __init__(self, nom, capacite):
        self.nom = nom
        self.capacite = capacite
    def  afficher(self):
        return f"{self.nom} ({self.capacite})"
    def est_disponible(self):
        return True


class Reservation:
    def __init__(self, date, heure_debut, heure_fin):
        self.date = date
        self.heure_debut = heure_debut
        self.heure_fin = heure_fin
    def afficher(self):
        return f"{self.date} ({self.heure_debut} - {self.heure_fin})"
annuler = Reservation("2024-06-15", "10:00", "12:00")
print(annuler.afficher())


class employe:
    def __init__(self, nom, numero):
        self.nom = nom
        self.numero = numero
    def afficher(self):
        return f"{self.nom} ({self.numero})"
    
reserver = employe("Baba Ndom", "12345")
print(reserver.afficher()) 