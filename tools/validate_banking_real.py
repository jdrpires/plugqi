import sys
import os
import json

# Add root to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from plugqi import PlugQi

def validate_banking():
    log_file = "validation_log.txt"
    def log(msg):
        print(msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
            
    with open(log_file, "w") as f: f.write("")

    log("🏦 VALIDATING BANKING CONNECTIVITY (JWT/PEM) - REAL CALLS")
    log("="*60)
    
    try:
        plug = PlugQi()
        log(f"✅ PlugQi Initialized with Base URL: {plug.client.base_url}")
    except Exception as e:
        log(f"❌ Failed to init PlugQi: {e}")
        return

    # 1. Test Financial Institutions (Public/Safe List)
    log("\n1️⃣  Testing /financial_institution (List Banks)...")
    try:
        # Pede apenas 2 para ser rápido
        banks = plug.financial_institution.list_institutions(page_size=2)
        
        if 'data' in banks:
            log(f"   🎉 SUCCESS! Found {len(banks['data'])} banks.")
            # Print first one for proof
            if len(banks['data']) > 0:
                log(f"   📝 Example: {banks['data'][0].get('name')}")
        else:
            log(f"   ⚠️ Response structure unexpected: {str(banks)[:100]}...")
            
    except Exception as e:
        log(f"   ❌ FAILED: {e}")

    # 2. Test Account Requests (Connectivity Probe)
    log("\n2️⃣  Testing /account_request/escrow (Connectivity)...")
    try:
        # Tenta um POST mínimo para ver se a rota existe
        try:
            plug.account_opening.reservar_conta_escrow_pf(
                document_number="000.000.000-00", 
                email="test@example.com",
                birthdate="2000-01-01",
                name="Test",
                documents={},
                face_key="test-key"
            )
        except Exception as e:
            msg = str(e)
            log(f"   ℹ️ Request executed. Exception: {msg[:100]}...")
            if hasattr(e, 'payload'):
                 log(f"      Payload: {json.dumps(e.payload, indent=2)}")
                 
    except Exception as e:
        log(f"   ❌ FAILED: {e}")

    # 3. Test Pix Key (Connectivity Probe)
    log("\n3️⃣  Testing /pix_key (Connectivity)...")
    try:
        try:
            plug.pix.consultar_chave_pix("00000000-0000-0000-0000-000000000000")
        except Exception as e:
            log(f"   ℹ️ Request executed. Exception: {e}")
            if hasattr(e, 'payload'):
                 log(f"      Payload: {json.dumps(e.payload, indent=2)}")

    except Exception as e:
        log(f"   ❌ Unexpected: {e}")

    # 4. Test TED (Connectivity Probe)
    log("\n4️⃣  Testing /ted (Connectivity)...")
    try:
        try:
            # Tenta listar com uma conta fake para ver a rota
            plug.ted.list_teds(account_key="00000000-0000-0000-0000-000000000000")
        except Exception as e:
            log(f"   ℹ️ Request executed. Exception: {e}")
            if hasattr(e, 'payload'):
                 log(f"      Payload: {json.dumps(e.payload, indent=2)}")
    except Exception as e:
        log(f"   ❌ Unexpected in TED test: {e}")

    log("\n" + "="*60)
    log("🏁 Validation Complete.")

if __name__ == "__main__":
    validate_banking()
