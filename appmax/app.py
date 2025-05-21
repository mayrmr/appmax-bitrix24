from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route("/")
def index():
    return "🟢 AppMax-Bitrix24 Webhook ativo!"

BITRIX_WEBHOOK_URL = "https://SEU_DOMINIO.bitrix24.com.br/rest/USUARIO_ID/SEU_TOKEN/"

CAMPOS_PERSONALIZADOS = {
    "telefone": "UF_CRM_1741981238931",
    "cpf": "UF_CRM_67C6426C757A8",
    "cupom": "UF_CRM_681E486559C7A",
    "produto": "UF_CRM_1747665660345",
    "numero_pedido": "UF_CRM_1747253174105",
    "logradouro": "UF_CRM_67BBBA0926C8D",
    "numero": "UF_CRM_67BBBA092FB0A",
    "complemento": "UF_CRM_67BBBA09383B5",
    "bairro": "UF_CRM_67BBBA0941B47",
    "cidade": "UF_CRM_67BBBA094C8C2",
    "uf": "UF_CRM_67D17E5BC9E35",
    "cep": "UF_CRM_67BBBA095D263",
    "fonte": "SOURCE_DESCRIPTION",
}

def buscar_contato_por_cpf(cpf):
    url = f"{BITRIX_WEBHOOK_URL}/crm.contact.list.json"
    params = {
        f"filter[{CAMPOS_PERSONALIZADOS['cpf']}]": cpf,
        "select[]": "ID"
    }
    r = requests.get(url, params=params)
    data = r.json()
    if data["result"]:
        return data["result"][0]["ID"]
    return None

def criar_contato(dados):
    payload = {
        "fields": {
            "NAME": dados["nome"],
            "EMAIL": [{"VALUE": dados["email"], "VALUE_TYPE": "WORK"}],
            CAMPOS_PERSONALIZADOS["telefone"]: dados["telefone"],
            CAMPOS_PERSONALIZADOS["cpf"]: dados["cpf"],
            CAMPOS_PERSONALIZADOS["logradouro"]: dados["logradouro"],
            CAMPOS_PERSONALIZADOS["numero"]: dados["numero"],
            CAMPOS_PERSONALIZADOS["complemento"]: dados["complemento"],
            CAMPOS_PERSONALIZADOS["bairro"]: dados["bairro"],
            CAMPOS_PERSONALIZADOS["cidade"]: dados["cidade"],
            CAMPOS_PERSONALIZADOS["uf"]: dados["uf"],
            CAMPOS_PERSONALIZADOS["cep"]: dados["cep"],
            CAMPOS_PERSONALIZADOS["fonte"]: "APPMAX",
        }
    }
    r = requests.post(f"{BITRIX_WEBHOOK_URL}/crm.contact.add.json", json=payload)
    return r.json()["result"]

def criar_negocio(dados, contato_id):
    payload = {
        "fields": {
            "TITLE": f"Compra #{dados['numero_pedido']} - {dados['produto']}",
            "CONTACT_ID": contato_id,
            "OPPORTUNITY": dados["valor"],
            "CURRENCY_ID": "BRL",
            "CATEGORY_ID": 29,
            "STAGE_ID": "C29:NEW",
            CAMPOS_PERSONALIZADOS["produto"]: dados["produto"],
            CAMPOS_PERSONALIZADOS["cupom"]: dados["cupom"],
            CAMPOS_PERSONALIZADOS["numero_pedido"]: dados["numero_pedido"],
            CAMPOS_PERSONALIZADOS["fonte"]: "APPMAX",
        }
    }
    r = requests.post(f"{BITRIX_WEBHOOK_URL}/crm.deal.add.json", json=payload)
    return r.json()["result"]

def vincular_contato_ao_negocio(deal_id, contact_id):
    payload = {
        "id": deal_id,
        "items": [
            {
                "CONTACT_ID": contact_id,
                "IS_PRIMARY": "Y"
            }
        ]
    }
    r = requests.post(f"{BITRIX_WEBHOOK_URL}/crm.deal.contact.items.set.json", json=payload)
    print("🔗 Vínculo do contato ao negócio:", r.json())

@app.route("/webhook/appmax", methods=["POST"])
def receber_webhook():
    dados = request.json
    print("🔥 Webhook chegou:", dados)

    if dados.get("event") != "OrderPaid":
        print("🚫 Ignorado, evento não é OrderPaid:", dados.get("event"))
        return jsonify({"status": "ignorado", "motivo": "Evento não é OrderPaid"}), 200

    try:
        info = dados.get("data", {})
        cliente = info.get("customer", {})
        produto = info.get("bundles", [{}])[0].get("name", "Produto não informado")

        print("🧾 CHAVES DO CLIENTE:", list(cliente.keys()))

        compra = {
            "nome": cliente.get("fullname") or f"{cliente.get('firstname', '')} {cliente.get('lastname', '')}",
            "email": cliente.get("email"),
            "telefone": cliente.get("telephone"),
            "cpf": cliente.get("document_number"),
            "logradouro": cliente.get("address_street"),
            "numero": cliente.get("address_street_number"),
            "complemento": cliente.get("address_street_complement"),
            "bairro": cliente.get("address_street_district"),
            "cidade": cliente.get("address_city"),
            "uf": cliente.get("address_state"),
            "cep": cliente.get("postcode"),
            "produto": produto,
            "cupom": None,
            "numero_pedido": str(info.get("id")),
            "valor": float(str(info.get("total", 0)).replace(",", ".")),
            "data_compra": cliente.get("created_at"),
        }

        print("📦 DADOS TRATADOS PARA CRM:", compra)

        if not compra["cpf"]:
            return jsonify({"status": "erro", "mensagem": "CPF ausente"}), 400

        contato_id = buscar_contato_por_cpf(compra["cpf"])
        if not contato_id:
            contato_id = criar_contato(compra)

        negocio_id = criar_negocio(compra, contato_id)
        vincular_contato_ao_negocio(negocio_id, contato_id)

        return jsonify({"status": "ok", "contato_id": contato_id, "negocio_id": negocio_id})

    except Exception as e:
        print("❌ Erro ao processar webhook:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)