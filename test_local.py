#!/usr/bin/env python3
from plugqi import PlugQi

def main():
    print("🔌 Testando PlugQi localmente...")
    
    try:
        # Inicializar
        plugqi = PlugQi()
        print("✅ PlugQi inicializado")
        
        # Testar conectividade
        if plugqi.health_check():
            print("✅ Conectado à QiTech API")
            print("🚀 Projeto rodando localmente!")
        else:
            print("❌ Falha na conectividade")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
