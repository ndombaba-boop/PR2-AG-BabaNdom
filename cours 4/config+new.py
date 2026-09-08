class Configuration:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialise()
        return cls._instance
    def _initialise(self):
        self.valeurs = {
            "seuil": 3,
            "mode": "test"
        }

c1=Configuration()
c2=Configuration()
c3=Configuration()
c1.valeurs["seuil"] = 5
print(c2.valeurs["seuil"])

print(c1 is c2)