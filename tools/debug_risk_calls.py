import sys
import os
import requests
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from qitech_client import QiTechClient

def probe_paths():
    log_file = "debug_log.txt"
    def log(msg):
        print(msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
            
    # Limpa log anterior
    with open(log_file, "w") as f: f.write("")
            
    log("🕵️‍♂️ PROBING RISK HOST: api.sandbox.caas.qitech.app")
    log("="*60)
    
    # Força a URL de Risco (CAAS)
    risk_host = "https://api.sandbox.caas.qitech.app"
    
    try:
        # Inicializa com a URL correta e chaves do ambiente
        client = QiTechClient(base_url=risk_host)
        log(f"✅ Client Base URL (Variable): {risk_host}")
        log(f"✅ Client Base URL (Instance): {client.base_url}")
    except Exception as e:
        log(f"❌ Init failed: {e}")
        return

    log("\n2️⃣ Probing Risk Paths...")
    
    # Paths baseados na confirmação do user
    candidate_paths = [
        "/onboarding/natural_person",  # Base api.sandbox.caas... + /onboarding...
        "/natural_person",             # Caso a base já tivesse /onboarding (não tem, mas testamos)
        "/onboarding/legal_person",
        "/legal_person"
    ]
    
    # Payload válido para PJ/PF
    payload = {
        "document_number": "59.541.264/0001-03", 
        "name": "Probe Test"
    }
    
    for path in candidate_paths:
        log(f"\n👉 Trying: {path}")
        try:
            # Captura exception para ver status code
            try:
                resp = client.post(path, json_body=payload)
                log(f"   🎉 FOUND! Status: Success (2xx)")
                # Se der sucesso, mostra resposta
                log(f"   Response: {str(resp)[:100]}")
            except Exception as e:
                log(f"   ❌ Error: {e}")
                if hasattr(e, 'status'):
                     log(f"      Status Code: {e.status}")
                
        except Exception as e:
            log(f"   ⚠️ Exception: {e}")

    log("\n" + "="*50)
    log("📋 Check Status Codes:")
    log("   401/403 -> Auth Inválida (Chave errada para este host)")
    log("   404 -> Rota errada (mas Auth talvez válida?)")
    log("   200/201 -> SUCESSO!")

if __name__ == "__main__":
    probe_paths()
