from abc import ABC, abstractmethod

class Sonde(ABC):

    @abstractmethod
    def mesurer(self):
        pass

class sondeTemperature(Sonde):
    def mesurer(self):
        return f"Température mesurée : {25}°C"

class sondepression(Sonde):
    def mesurer(self):
        return f"Pression mesurée : {1013} hPa"

class sondeHumidite(Sonde):
    def mesurer(self):
        return f"Humidité mesurée : {60}%"


class fabriqueSonde:
    _sonde = {
        "temperature": sondeTemperature,
        "pression": sondepression,
        "humidite": sondeHumidite
    }

    @classmethod
    def creerSonde(cls, type_sonde):
        if type_sonde in cls._sonde:
            return cls._sonde[type_sonde]()
        else:
            raise ValueError(f"Type de sonde '{type_sonde}' non reconnu.")

#for type_sonde in ["temperature", "pression", "humidite"]:
    #sonde = fabriqueSonde.creerSonde(type_sonde)
   # print(sonde.mesurer())

s_temp = fabriqueSonde.creerSonde("temperature")
s_pression = fabriqueSonde.creerSonde("pression")
s_humidite = fabriqueSonde.creerSonde("humidite")
print(s_temp.mesurer())
print(s_pression.mesurer())
print(s_humidite.mesurer())
