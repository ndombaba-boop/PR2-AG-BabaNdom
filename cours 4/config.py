class Configuration:
    def __init__(self):
        self.valeurs = {
            "seuil": 3,
            "mode": "test"
        }

c1=Configuration()
c2=Configuration()
c3=Configuration()
c1.valeurs["seuil"] = 5
print(c2.valeurs["seuil"])
print(c1.valeurs["seuil"])