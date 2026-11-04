panier = [
    {"article": "Souris", "prix": 19.99, "quantite": 2},
    {"article": "Clavier", "prix": 49.99, "quantite": 1}
]

sous_total = 0

for ligne in panier:
    sous_total += ligne["prix"]  # ERREUR

print("Sous-total :", sous_total) 

panier = [
    {"article": "Souris", "prix": 19.99, "quantite": 2},
    {"article": "Clavier", "prix": 49.99, "quantite": 1}
]

sous_total = 0

for ligne in panier:
    sous_total += ligne["prix"] * ligne["quantite"]

print("Sous-total :", sous_total)