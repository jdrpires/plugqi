# examples/boleto_example.py
import sys, os
from datetime import datetime, timedelta
import uuid

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from plugqi import PlugQi
from qitech_client import QiTechError

def main():
    # Inicializa o PlugQi
    plugqi = PlugQi()
    
    # Dados de exemplo (ajuste conforme necessário)
    account_key = "sua-account-key-aqui"
    requester_profile_key = "sua-carteira-key-aqui"
    
    try:
        # 1. Criar boleto simples
        boleto_data = plugqi.boleto.build_simple_boleto(
            request_control_key=str(uuid.uuid4()),
            amount=100.50,  # R$ 100,50
            expiration=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            payer_name="João Silva",
            payer_document="12345678901",
            bank_teller_instructions="Pagamento referente à fatura 001"
        )
        
        # Criar boleto padrão (assíncrono)
        result = plugqi.boleto.create_boleto(account_key, requester_profile_key, boleto_data)
        print("Boleto criado:", result)
        
        # 2. Consultar boleto
        bank_slip_key = result.get("bank_slip_key")
        if bank_slip_key:
            boleto_info = plugqi.boleto.get_boleto(account_key, bank_slip_key)
            print("Dados do boleto:", boleto_info)
        
        # 3. Listar carteiras
        carteiras = plugqi.boleto.list_requester_profiles(account_key)
        print("Carteiras disponíveis:", carteiras)
        
    except QiTechError as e:
        print(f"Erro QiTech: {e.status} - {e}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()
