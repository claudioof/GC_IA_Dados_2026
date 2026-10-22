from flask import Flask, jsonify, request
import requests

app = Flask(__name__)
sucos = []

@app.route("/frutas/<nome>", methods=["GET"])
def get_fruta(nome):
    url = f"https://fruityvice.com/api/fruit/{nome}"
    resposta = requests.get(url, timeout=10)
    if resposta.status_code == 404:
        return jsonify({"erro": f"{nome} não foi encontrado"}), 404
    elif resposta.status_code != 200:
        return jsonify({"erro": "Não foi possivel efetuar a consulta"}), 502
    
    dados = resposta.json()
    nutrientes = dados["nutritions"]

    return jsonify({
        "nome": dados["name"],
       "calorias": nutrientes["calories"],
       "acucar": nutrientes["sugar"],
    })

@app.route("/sucos", methods=["POST"])
def cadastrar_suco():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "dados do suco invalidos."}), 400
    if not dados.get("nome") or  not dados.get("frutas"):
        return jsonify({"erro": "informe o nome do suco e frutas."}), 400

    total_calorias = 0
    total_acucar = 0
    for fruta in dados["frutas"]:
        url_fruta = f"https://fruityvice.com/api/fruit/{fruta}"
        resposta_fruta = requests.get(url_fruta, timeout=10)
        if resposta_fruta.status_code == 404:
            return jsonify({"erro": f"{fruta} nao foi encontrado"}), 404
        elif resposta_fruta.status_code != 200:
            return jsonify({"erro": "não foi possivel encontrar uma das frutas."}), 502
        dados_fruta = resposta_fruta.json()
        total_calorias += dados_fruta["nutritions"]["calories"]
        total_acucar += dados_fruta["nutritions"]["sugar"]
    novo_suco = {
        "id": len(sucos) + 1,
        "nome": dados["nome"],
        "frutas": dados["frutas"],
        "tem_gosto_de": dados.get("tem_gosto_de", ""),
        "total_calorias": total_calorias,
        "total_acucar": round(total_acucar, 2)
    }
    sucos.append(novo_suco)
    return jsonify(novo_suco), 201


@app.route("/sucos", methods=["GET"])
def listar_sucos():
    return jsonify(sucos)    
        

if __name__ == "__main__":
    app.run(debug=True)