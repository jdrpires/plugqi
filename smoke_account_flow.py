# examples/smoke_account_flow.py
# Fluxo completo: autentica -> lista contas -> simula crédito -> consulta detalhes
import sys, os, json, time

from qitech_client import QiTechClient, QiTechError

sys.path.append(os.path.dirname(os.path.dirname(__file__)))



# 🔧 Preencha aqui (ou use as variáveis de ambiente abaixo)
DOC_NUMBER = os.getenv("QI_OWNER_DOCUMENT_NUMBER", "22203015837")   # CPF/CNPJ válido no sandbox
ACCOUNT_NUMBER = os.getenv("QI_ACCOUNT_NUMBER", "68670834")          # número da conta válido no sandbox
SIMULATED_AMOUNT = int(os.getenv("QI_SIMULATED_AMOUNT", "100"))     # valor em centavos, se sua QI usar centavos; ajuste conforme docs (p.ex. 100 = R$1,00)

def jprint(title, payload):
    print("\n" + "="*62)
    print(f"🔹 {title}")
    print("="*62)
    try:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    except Exception:
        print(payload)

def main():
    print("🚀 Fluxo QiTech: autenticação → listar → simular → consultar")

    client = QiTechClient(
        # se preferir, force as credenciais aqui; senão, .env será usado
        # api_key="",
        # private_key_path="",
        # base_url="https://api-auth.sandbox.qitech.app",
    )

    try:
        # 1) Autenticação / conectividade
        post_test = client.post("/test", {"name": "QI Tech"})
        jprint("POST /test", post_test)

        get_test = client.get(f"/test/{client.api_key}")
        jprint(f"GET /test/{{api_key}}", get_test)

        # 2) Listar contas por documento + número de conta
        params = {
            "owner_document_number": DOC_NUMBER,
            "account_number": ACCOUNT_NUMBER
        }
        acc_list = client.get("/account", params=params)
        jprint("GET /account (lista por doc+conta)", acc_list)

        # defensivo: achar uma account_key
        account_key = None
        if isinstance(acc_list, dict):
            # formatos comuns: {"data":[{...}]}, {"accounts":[{...}]}, ou lista direta
            candidates = []
            if "data" in acc_list and isinstance(acc_list["data"], list):
                candidates = acc_list["data"]
            elif "accounts" in acc_list and isinstance(acc_list["accounts"], list):
                candidates = acc_list["accounts"]
            elif isinstance(acc_list, list):
                candidates = acc_list

            for item in candidates:
                if isinstance(item, dict) and "account_key" in item:
                    account_key = item["account_key"]
                    break

        if not account_key:
            print("\n⚠️  Nenhuma 'account_key' encontrada para os parâmetros informados.")
            print("    → Verifique se DOC_NUMBER e ACCOUNT_NUMBER existem no sandbox/QI.")
            return

        print(f"\n✅ account_key encontrada: {account_key}")

        # 3) Simular crédito (cenário de sandbox)
        # Atenção ao contrato do endpoint mock; se sua QI usa valor em centavos, ajuste SIMULATED_AMOUNT.
        sim_payload = {
            "target_account_key": account_key,
            "amount": SIMULATED_AMOUNT
        }
        sim_resp = client.post("/mock/account/transaction", sim_payload)
        # alguns mocks não retornam body; ainda assim mostramos o que vier
        jprint("POST /mock/account/transaction (simulação de crédito)", sim_resp or {"status":"no-content"})

        # Pequena espera para garantir que a simulação foi aplicada
        time.sleep(1)

        # 4) Consultar detalhes por account_key
        detail = client.get(f"/account/{account_key}")
        jprint("GET /account/{account_key} (detalhes + saldo)", detail)

        print("\n🎉 Fluxo concluído!")

    except QiTechError as e:
        print("\n❌ QiTechError")
        print("Status:", e.status)
        jprint("Payload de erro", e.payload)
    except Exception as e:
        print("\n❌ Erro inesperado:", repr(e))

if __name__ == "__main__":
    main()
