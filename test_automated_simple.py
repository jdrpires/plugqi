#!/usr/bin/env python3
"""
Testes automatizados simples para validação rápida das funcionalidades
Executa sem chamadas reais à API - apenas validação de estrutura e lógica
"""
import json
import uuid
from datetime import datetime, timedelta
from plugqi import PlugQi
from qitech_client import QiTechError

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name):
        self.passed += 1
        print(f"✅ {test_name}")
    
    def add_fail(self, test_name, error):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ {test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n📊 RESUMO: {self.passed}/{total} testes passaram")
        if self.errors:
            print("\n🔍 ERROS:")
            for error in self.errors:
                print(f"  - {error}")

def test_boleto_functionality():
    """Testa funcionalidades de boleto"""
    results = TestResults()
    plugqi = PlugQi()
    
    try:
        # Teste 1: build_payer_data
        payer = plugqi.boleto.build_payer_data(
            name="João Silva",
            document="12345678901",
            person_type="natural",
            email="joao@teste.com"
        )
        assert payer["name"] == "João Silva"
        assert payer["document_number"] == "12345678901"
        assert payer["contact"]["email"] == "joao@teste.com"
        results.add_pass("Boleto - build_payer_data")
    except Exception as e:
        results.add_fail("Boleto - build_payer_data", str(e))
    
    try:
        # Teste 2: build_simple_boleto
        boleto = plugqi.boleto.build_simple_boleto(
            request_control_key=str(uuid.uuid4()),
            amount=150.75,
            expiration=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            payer_name="Maria Santos",
            payer_document="98765432100"
        )
        assert boleto["amount"] == 150.75
        assert boleto["payer_data"]["name"] == "Maria Santos"
        results.add_pass("Boleto - build_simple_boleto")
    except Exception as e:
        results.add_fail("Boleto - build_simple_boleto", str(e))
    
    try:
        # Teste 3: Métodos existem
        methods = ['create_boleto', 'create_bolepix', 'get_boleto', 'list_boletos']
        for method in methods:
            assert hasattr(plugqi.boleto, method)
        results.add_pass("Boleto - métodos existem")
    except Exception as e:
        results.add_fail("Boleto - métodos existem", str(e))
    
    return results

def test_pix_functionality():
    """Testa funcionalidades PIX"""
    results = TestResults()
    plugqi = PlugQi()
    
    try:
        # Teste 1: Validação de chaves PIX
        assert plugqi.pix.validar_chave_pix("cpf", "12345678901") == True
        assert plugqi.pix.validar_chave_pix("email", "test@email.com") == True
        assert plugqi.pix.validar_chave_pix("cpf", "123") == False
        results.add_pass("PIX - validação de chaves")
    except Exception as e:
        results.add_fail("PIX - validação de chaves", str(e))
    
    try:
        # Teste 2: build_dados_destinatario
        dados = plugqi.pix.build_dados_destinatario(
            nome="João Silva",
            documento="12345678901",
            banco="341",
            agencia="1234",
            conta="12345-6"
        )
        assert dados["owner_name"] == "João Silva"
        assert dados["ispb"] == "341"
        results.add_pass("PIX - build_dados_destinatario")
    except Exception as e:
        results.add_fail("PIX - build_dados_destinatario", str(e))
    
    try:
        # Teste 3: Métodos existem
        methods = ['enviar_pix_chave', 'enviar_pix_automatico', 'consultar_chave_pix', 'listar_transferencias_pix']
        for method in methods:
            assert hasattr(plugqi.pix, method)
        results.add_pass("PIX - métodos existem")
    except Exception as e:
        results.add_fail("PIX - métodos existem", str(e))
    
    return results

def test_account_opening_functionality():
    """Testa funcionalidades de abertura de conta"""
    results = TestResults()
    plugqi = PlugQi()
    
    try:
        # Teste 1: build_empresa_basica
        empresa = plugqi.account_opening.build_empresa_basica(
            cnpj="12345678000100",
            razao_social="Empresa Teste Ltda",
            email="contato@empresa.com",
            data_fundacao="2020-01-01"
        )
        assert empresa["company_document_number"] == "12345678000100"
        assert empresa["name"] == "Empresa Teste Ltda"
        results.add_pass("Account Opening - build_empresa_basica")
    except Exception as e:
        results.add_fail("Account Opening - build_empresa_basica", str(e))
    
    try:
        # Teste 2: Validações
        assert plugqi.account_opening.validar_cnpj("12345678000100") == True
        assert plugqi.account_opening.validar_cpf("12345678901") == True
        assert plugqi.account_opening.validar_cnpj("123") == False
        results.add_pass("Account Opening - validações")
    except Exception as e:
        results.add_fail("Account Opening - validações", str(e))
    
    try:
        # Teste 3: Métodos existem
        methods = ['reservar_conta_pj', 'confirmar_abertura_conta', 'consultar_status_abertura']
        for method in methods:
            assert hasattr(plugqi.account_opening, method)
        results.add_pass("Account Opening - métodos existem")
    except Exception as e:
        results.add_fail("Account Opening - métodos existem", str(e))
    
    return results

def test_health_check():
    """Testa conectividade básica"""
    results = TestResults()
    plugqi = PlugQi()
    
    try:
        # Teste sem credenciais reais - apenas estrutura
        assert hasattr(plugqi, 'health_check')
        assert callable(plugqi.health_check)
        results.add_pass("Health Check - método existe")
    except Exception as e:
        results.add_fail("Health Check - método existe", str(e))
    
    return results

def load_pix_keys():
    """Carrega chaves PIX mockadas"""
    try:
        with open('pix_keys_mock.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def test_pix_keys_loaded():
    """Testa se as chaves PIX foram carregadas"""
    results = TestResults()
    
    try:
        pix_keys = load_pix_keys()
        assert len(pix_keys) > 0
        assert 'caixa' in pix_keys
        assert 'itau' in pix_keys
        results.add_pass("PIX Keys - arquivo carregado")
    except Exception as e:
        results.add_fail("PIX Keys - arquivo carregado", str(e))
    
    return results

def main():
    """Executa todos os testes simples"""
    print("🚀 Executando testes automatizados simples...")
    print("=" * 60)
    
    all_results = TestResults()
    
    # Executa todos os testes
    tests = [
        test_boleto_functionality,
        test_pix_functionality, 
        test_account_opening_functionality,
        test_health_check,
        test_pix_keys_loaded
    ]
    
    for test_func in tests:
        print(f"\n📋 {test_func.__name__.replace('test_', '').replace('_', ' ').title()}")
        print("-" * 40)
        result = test_func()
        all_results.passed += result.passed
        all_results.failed += result.failed
        all_results.errors.extend(result.errors)
    
    print("\n" + "=" * 60)
    all_results.summary()
    
    return all_results.failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
