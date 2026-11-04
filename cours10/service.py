from flask import Flask, jsonify, request

app = Flask(__name__)
SECRETS = {}        
PROCHAIN = 1
  #en mémoire, pour aujourd'hui
@app.get("/secrets")
def lister():
    return jsonify(list(SECRETS.values())), 200
@app.post("/secrets")
def creer():
    global PROCHAIN
    donnees = request.get_json()
    if "libelle" not in donnees:
        return jsonify({"erreur": "libelle_requis"}), 400
    donnees["id"] = PROCHAIN
    SECRETS[PROCHAIN] = donnees
    PROCHAIN += 1
    return jsonify(donnees), 201, {"Location": f"/secrets/{donnees['id']}"}
app.run(port=5000, debug=True)