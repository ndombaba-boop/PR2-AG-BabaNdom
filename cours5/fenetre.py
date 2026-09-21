import tkinter as tk # 1. la fenêtre
from tkinter import ttk 

'''fenetre = tk.Tk() # 2. le titre
fenetre.title("Reseau social") # 2. le titre
ttk.Label(fenetre, text="Username:").pack()
ttk.Entry(fenetre).pack() # 4. les champs de saisie

ttk.Label(fenetre, text="Password:").pack(side="left")
ttk.Entry(fenetre, show="*").pack() # 4. les champs

ttk.Label(fenetre, text="Observation:").pack()
tk.Text(fenetre, height=5, width=30).pack() # 4. les champs de saisie

ttk.Label(fenetre, text="type de compte:").pack() # 5. la liste déroulante
ttk.Combobox(fenetre, values=[ "admin", "user", "client"]).pack() # 5. la liste déroulante

ttk .Button(fenetre, text="OK", command=fenetre.destroy).pack() # 3

fenetre.mainloop() # la boucle principale de l'interface graphique  '''


# 1. creation de la fenetre
fenetre = tk.Tk()

# 2. le titre
fenetre.title("Reseau social")

# 4. les champs de saisie
ttk.Label(fenetre, text="Username:").grid(row=0, column=0, padx=5, pady=10)
ttk.Entry(fenetre).grid(row=0, column=1, padx=5, pady=10)

ttk.Label(fenetre, text="Password:").grid(row=1, column=0, padx=5, pady=10)
champ_password = ttk.Entry(fenetre, show="*")
champ_password.grid(row=1, column=1, padx=5, pady=10)

def voir_password():
    if afficher.get():
        champ_password.config(show="")
    else:
        champ_password.config(show="*")

# Case à cocher
afficher = tk.BooleanVar()

ttk.Checkbutton(
    fenetre,
    text="Afficher le mot de passe",
    variable=afficher,
    command=voir_password
).grid(row=2, column=1)


# 4. les champs de saisie
ttk.Label(fenetre, text="Observation:").grid(row=2, column=0, padx=5, pady=10)
tk.Text(fenetre, height=5, width=30).grid(row=2, column=1, padx=5, pady=10)

# 5. la liste déroulante
ttk.Label(fenetre, text="type de compte:").grid(row=3, column=0, padx=5, pady=10)
ttk.Combobox(fenetre, values=["admin", "user", "client"]).grid(row=3, column=1, padx=5, pady=10)

# 3. bouton
ttk.Button(fenetre, text="ENTER", command=fenetre.destroy).grid(row=4, column=1)

fenetre.mainloop() 