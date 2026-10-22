
from flask import Flask, jsonify, request
from flasgger import Swagger
import requests

app = Flask(__name__)
swagger = Swagger(app)

sucos = []


@app.route("/frutas/<nome>", methods=["GET"])
def get_fruta(nome):
    """
    Consulta os dados nutricionais de uma fruta.
    ---
    tags:
      - Frutas
    parameters:
      - name: nome
        in: path
        type: string
        required: true
        description: Nome da fruta em inglês.
    responses:
      200:
        description: Dados nutricionais da fruta.
      404:
        description: Fruta não encontrada.
      502:
        description: Erro na consulta externa.
    """
    url = f"https://www.fruityvice.com/api/fruit/{nome}"

    try:
        resposta = requests.get(url, timeout=10)
    except requests.RequestException:
        return jsonify({"erro": "Não foi possível conectar à API de frutas."}), 502

    if resposta.status_code == 404:
        return jsonify({"erro": f"{nome} não foi encontrado"}), 404
    elif resposta.status_code != 200:
        return jsonify({"erro": "Não foi possível efetuar a consulta"}), 502

    dados = resposta.json()
    nutrientes = dados["nutritions"]

    return jsonify({
        "nome": dados["name"],
        "calorias": nutrientes["calories"],
        "acucar": nutrientes["sugar"],
    })


@app.route("/sucos", methods=["POST"])
def cadastrar_suco():
    """
    Cadastra um suco e calcula seus valores nutricionais.
    ---
    tags:
      - Sucos
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nome
            - frutas
          properties:
            nome:
              type: string
              example: Vitamina Tropical
            frutas:
              type: array
              items:
                type: string
              example: ["banana", "strawberry"]
            tem_gosto_de:
              type: string
              example: Tamarindo
    responses:
      201:
        description: Suco cadastrado com sucesso.
      400:
        description: Dados inválidos.
      404:
        description: Fruta não encontrada.
      502:
        description: Erro na consulta externa.
    """
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie os dados do suco em formato JSON."}), 400

    if not isinstance(dados.get("nome"), str) or not dados["nome"].strip():
        return jsonify({"erro": "Informe um nome válido para o suco."}), 400

    frutas = dados.get("frutas")

    if not isinstance(frutas, list) or not frutas:
        return jsonify({"erro": "Frutas deve ser uma lista não vazia."}), 400

    if not all(isinstance(fruta, str) and fruta.strip() for fruta in frutas):
        return jsonify({"erro": "Cada fruta deve ser um nome válido."}), 400

    total_calorias = 0
    total_acucar = 0

    for fruta in frutas:
        url_fruta = f"https://www.fruityvice.com/api/fruit/{fruta.strip()}"

        try:
            resposta_fruta = requests.get(url_fruta, timeout=10)
        except requests.RequestException:
            return jsonify({
                "erro": "Não foi possível conectar à API de frutas."
            }), 502

        if resposta_fruta.status_code == 404:
            return jsonify({"erro": f"{fruta} não foi encontrada"}), 404
        elif resposta_fruta.status_code != 200:
            return jsonify({
                "erro": "Não foi possível consultar uma das frutas."
            }), 502

        dados_fruta = resposta_fruta.json()
        nutrientes = dados_fruta["nutritions"]

        total_calorias += nutrientes["calories"]
        total_acucar += nutrientes["sugar"]

    novo_suco = {
        "id": len(sucos) + 1,
        "nome": dados["nome"].strip(),
        "frutas": [fruta.strip() for fruta in frutas],
        "tem_gosto_de": dados.get("tem_gosto_de", ""),
        "total_calorias": total_calorias,
        "total_acucar": round(total_acucar, 2)
    }

    sucos.append(novo_suco)

    return jsonify(novo_suco), 201


@app.route("/sucos", methods=["GET"])
def listar_sucos():
    """
    Lista os sucos cadastrados.
    ---
    tags:
      - Sucos
    responses:
      200:
        description: Lista de sucos cadastrados.
    """
    return jsonify(sucos), 200


if __name__ == "__main__":
    app.run(debug=True)