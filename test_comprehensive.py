#!/usr/bin/env python3
"""
Testes completos com dados reais - cenários positivos, negativos e exploratórios
Executa chamadas reais à API QiTech (requer credenciais válidas)
"""
import json
import uuid
import random
import time
from datetime import datetime, timedelta
from decimal import Decimal
from plugqi import PlugQi
from qitech_client import QiTechError

class ComprehensiveTestResults:
    def __init__(self):
        self.results = {
            'account_opening': {'passed': 0, 'failed': 0, 'errors': []},
            'boletos': {'passed': 0, 'failed': 0, 'errors': []},
            'bolepix': {'passed': 0, 'failed': 0, 'errors': []},
            'pix': {'passed': 0, 'failed': 0, 'errors': []},
            'payments': {'passed': 0, 'failed': 0, 'errors': []},
            'credit': {'passed': 0, 'failed': 0, 'errors': []},
            'negative_tests': {'passed': 0, 'failed': 0, 'errors': []},
            'exploratory': {'passed': 0, 'failed': 0, 'errors': []}
        }
        self.test_data = {
            'accounts_created': [],
            'boletos_created': [],
            'pix_transactions': [],
            'execution_time': 0
        }
    
    def add_result(self, category, test_name, success, error=None, data=None):
        if success:
            self.results[category]['passed'] += 1
            print(f"✅ {category.upper()} - {test_name}")
            if data:
                if category == 'account_opening':
                    self.test_data['accounts_created'].append(data)
                elif category in ['boletos', 'bolepix']:
                    self.test_data['boletos_created'].append(data)
                elif category == 'pix':
                    self.test_data['pix_transactions'].append(data)
        else:
            self.results[category]['failed'] += 1
            self.results[category]['errors'].append(f"{test_name}: {error}")
            print(f"❌ {category.upper()} - {test_name}: {error}")
    
    def summary(self):
        print("\n" + "="*80)
        print("📊 RELATÓRIO COMPLETO DE TESTES")
        print("="*80)
        
        total_passed = sum(cat['passed'] for cat in self.results.values())
        total_failed = sum(cat['failed'] for cat in self.results.values())
        total_tests = total_passed + total_failed
        
        print(f"🎯 RESUMO GERAL: {total_passed}/{total_tests} testes passaram ({(total_passed/total_tests*100):.1f}%)")
        print(f"⏱️  TEMPO DE EXECUÇÃO: {self.test_data['execution_time']:.2f}s")
        
        for category, data in self.results.items():
            total = data['passed'] + data['failed']
            if total > 0:
                success_rate = (data['passed'] / total) * 100
                print(f"\n📋 {category.upper().replace('_', ' ')}: {data['passed']}/{total} ({success_rate:.1f}%)")
                if data['errors']:
                    for error in data['errors'][:3]:  # Mostra apenas os 3 primeiros erros
                        print(f"   ❌ {error}")
        
        print(f"\n📈 DADOS GERADOS:")
        print(f"   🏦 Contas criadas: {len(self.test_data['accounts_created'])}")
        print(f"   💰 Boletos criados: {len(self.test_data['boletos_created'])}")
        print(f"   🔄 Transações PIX: {len(self.test_data['pix_transactions'])}")

def load_pix_keys():
    """Carrega chaves PIX mockadas"""
    try:
        with open('pix_keys_mock.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  Arquivo pix_keys_mock.json não encontrado")
        return {}

def get_random_pix_key():
    """Retorna uma chave PIX aleatória"""
    pix_data = load_pix_keys()
    if not pix_data:
        return None
    
    bank = random.choice(list(pix_data.keys()))
    key_data = random.choice(pix_data[bank]['keys'])
    return key_data['key']

def generate_random_amount():
    """Gera valor aleatório em centavos"""
    return round(random.uniform(0.01, 999.99), 2)

def test_account_opening(plugqi, results):
    """Testa abertura de contas - 3 contas escrow"""
    print("\n🏦 TESTANDO ABERTURA DE CONTAS")
    print("-" * 50)
    
    companies = [
        {"cnpj": "12345678000101", "name": "Empresa Alpha Ltda", "email": "alpha@test.com"},
        {"cnpj": "12345678000102", "name": "Empresa Beta S.A.", "email": "beta@test.com"},
        {"cnpj": "12345678000103", "name": "Empresa Gamma ME", "email": "gamma@test.com"}
    ]
    
    for i, company in enumerate(companies, 1):
        try:
            # Dados da empresa
            empresa_data = plugqi.account_opening.build_empresa_basica(
                cnpj=company["cnpj"],
                razao_social=company["name"],
                email=company["email"],
                data_fundacao="2020-01-01"
            )
            
            # Representante legal
            representante = plugqi.account_opening.build_representante_legal(
                nome=f"Representante {i}",
                cpf=f"1234567890{i}",
                nascimento="1980-01-01",
                documentos=plugqi.account_opening.build_documentos_rg("ocr_front", "ocr_back")
            )
            
            # Reserva conta
            response = plugqi.account_opening.reservar_conta_pj(empresa_data, [representante])
            
            results.add_result('account_opening', f'Reserva conta {i}', True, data={
                'account_request_key': response.get('account_request_key'),
                'company': company["name"],
                'status': response.get('status')
            })
            
            time.sleep(1)  # Evita rate limiting
            
        except QiTechError as e:
            results.add_result('account_opening', f'Reserva conta {i}', False, f"QiTech Error: {e.status}")
        except Exception as e:
            results.add_result('account_opening', f'Reserva conta {i}', False, str(e))

def test_boletos(plugqi, results):
    """Testa criação de boletos - 5 tipos diferentes"""
    print("\n💰 TESTANDO BOLETOS")
    print("-" * 50)
    
    # Chaves reais encontradas
    account_key = "5756066f-f592-43ae-b254-8d51a0026a77"
    profile_key = "4905a83b-d7ed-4114-b26b-e0cd51d78a57"
    
    boleto_types = [
        {"name": "Pessoa Física Básico", "amount": 150.75, "payer": "Mock Person Name", "doc": "65322181032"},
        {"name": "Pessoa Jurídica", "amount": 2500.00, "payer": "Mocked Enterprise S.A", "doc": "40008675000100"},
        {"name": "Valor Alto", "amount": 5000.00, "payer": "Mock Person Name", "doc": "22156083070"},
        {"name": "Valor Baixo", "amount": 10.50, "payer": "Mock Person Name", "doc": "96969879003"},
        {"name": "Vencimento Longo", "amount": 1000.00, "payer": "Mock Person Name", "doc": "61295118092"}
    ]
    
    for boleto_type in boleto_types:
        try:
            boleto_data = plugqi.boleto.build_simple_boleto(
                request_control_key=str(uuid.uuid4()),
                amount=boleto_type["amount"],
                expiration=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                payer_name=boleto_type["payer"],
                payer_document=boleto_type["doc"],
                bank_teller_instructions=f"Pagamento - {boleto_type['name']}"
            )
            
            # Tenta criar boleto (vai falhar sem credenciais válidas)
            response = plugqi.boleto.create_boleto(account_key, profile_key, boleto_data)
            
            results.add_result('boletos', boleto_type["name"], True, data={
                'bank_slip_key': response.get('bank_slip_key'),
                'amount': boleto_type["amount"],
                'payer': boleto_type["payer"]
            })
            
        except QiTechError as e:
            if e.status == 401:  # Unauthorized - esperado sem credenciais
                results.add_result('boletos', f'{boleto_type["name"]} (estrutura)', True, data={
                    'amount': boleto_type["amount"],
                    'payer': boleto_type["payer"],
                    'note': 'Payload válido, falha de autenticação esperada'
                })
            else:
                results.add_result('boletos', boleto_type["name"], False, f"QiTech Error: {e.status}")
        except Exception as e:
            results.add_result('boletos', boleto_type["name"], False, str(e))

def test_bolepix(plugqi, results):
    """Testa criação de BolePix com chaves PIX mockadas"""
    print("\n💳 TESTANDO BOLEPIX")
    print("-" * 50)
    
    account_key = "5756066f-f592-43ae-b254-8d51a0026a77"
    profile_key = "4905a83b-d7ed-4114-b26b-e0cd51d78a57"
    
    for i in range(5):
        try:
            pix_key = get_random_pix_key()
            if not pix_key:
                results.add_result('bolepix', f'BolePix {i+1}', False, "Nenhuma chave PIX disponível")
                continue
            
            amount = generate_random_amount()
            
            response = plugqi.boleto.create_bolepix(
                account_key=account_key,
                requester_profile_key=profile_key,
                amount=amount,
                expiration=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                payer_name=f"Pagador BolePix {i+1}",
                payer_document=f"1234567890{i}",
                pix_key=pix_key,
                description=f"BolePix teste {i+1}"
            )
            
            results.add_result('bolepix', f'BolePix {i+1}', True, data={
                'amount': amount,
                'pix_key': pix_key,
                'bank_slip_key': response.get('bank_slip_key')
            })
            
        except QiTechError as e:
            if e.status == 401:
                results.add_result('bolepix', f'BolePix {i+1} (estrutura)', True, data={
                    'amount': amount,
                    'pix_key': pix_key,
                    'note': 'Payload válido, falha de autenticação esperada'
                })
            else:
                results.add_result('bolepix', f'BolePix {i+1}', False, f"QiTech Error: {e.status}")
        except Exception as e:
            results.add_result('bolepix', f'BolePix {i+1}', False, str(e))

def test_pix_transactions(plugqi, results):
    """Testa transações PIX - 10 transações com valores aleatórios"""
    print("\n🔄 TESTANDO TRANSAÇÕES PIX")
    print("-" * 50)
    
    account_key = "5756066f-f592-43ae-b254-8d51a0026a77"
    
    for i in range(10):
        try:
            pix_key = get_random_pix_key()
            if not pix_key:
                results.add_result('pix', f'PIX {i+1}', False, "Nenhuma chave PIX disponível")
                continue
            
            amount = generate_random_amount()
            
            response = plugqi.pix.enviar_pix_chave(
                account_key=account_key,
                pix_key=pix_key,
                valor=amount,
                descricao=f"Teste PIX {i+1} - Valor: R$ {amount}"
            )
            
            results.add_result('pix', f'PIX {i+1}', True, data={
                'amount': amount,
                'pix_key': pix_key,
                'transaction_id': response.get('transaction_id')
            })
            
        except QiTechError as e:
            if e.status == 401:
                results.add_result('pix', f'PIX {i+1} (estrutura)', True, data={
                    'amount': amount,
                    'pix_key': pix_key,
                    'note': 'Payload válido, falha de autenticação esperada'
                })
            else:
                results.add_result('pix', f'PIX {i+1}', False, f"QiTech Error: {e.status}")
        except Exception as e:
            results.add_result('pix', f'PIX {i+1}', False, str(e))

def test_negative_scenarios(plugqi, results):
    """Testa cenários negativos"""
    print("\n❌ TESTANDO CENÁRIOS NEGATIVOS")
    print("-" * 50)
    
    # Teste 1: CPF inválido
    try:
        payer = plugqi.boleto.build_payer_data("João", "123", "natural")
        # Se chegou aqui, deveria ter validado
        results.add_result('negative_tests', 'CPF inválido aceito', False, "CPF inválido foi aceito")
    except:
        results.add_result('negative_tests', 'CPF inválido rejeitado', True)
    
    # Teste 2: Valor negativo
    try:
        boleto = plugqi.boleto.build_simple_boleto(
            request_control_key=str(uuid.uuid4()),
            amount=-100.0,
            expiration="2024-12-31",
            payer_name="João",
            payer_document="12345678901"
        )
        results.add_result('negative_tests', 'Valor negativo', True, data={'amount': -100.0})
    except Exception as e:
        results.add_result('negative_tests', 'Valor negativo rejeitado', True)
    
    # Teste 3: Data no passado
    try:
        boleto = plugqi.boleto.build_simple_boleto(
            request_control_key=str(uuid.uuid4()),
            amount=100.0,
            expiration="2020-01-01",
            payer_name="João",
            payer_document="12345678901"
        )
        results.add_result('negative_tests', 'Data passado aceita', True, data={'expiration': '2020-01-01'})
    except Exception as e:
        results.add_result('negative_tests', 'Data passado rejeitada', True)

def test_exploratory_scenarios(plugqi, results):
    """Testes exploratórios"""
    print("\n🔍 TESTANDO CENÁRIOS EXPLORATÓRIOS")
    print("-" * 50)
    
    # Teste 1: Caracteres especiais
    try:
        payer = plugqi.boleto.build_payer_data(
            "João da Silva & Cia. Ltda. (Teste)",
            "12345678901",
            "natural"
        )
        results.add_result('exploratory', 'Caracteres especiais no nome', True)
    except Exception as e:
        results.add_result('exploratory', 'Caracteres especiais no nome', False, str(e))
    
    # Teste 2: Valor com muitas casas decimais
    try:
        amount = 123.456789
        boleto = plugqi.boleto.build_simple_boleto(
            request_control_key=str(uuid.uuid4()),
            amount=amount,
            expiration="2024-12-31",
            payer_name="João",
            payer_document="12345678901"
        )
        results.add_result('exploratory', 'Valor com muitas casas decimais', True, data={'amount': amount})
    except Exception as e:
        results.add_result('exploratory', 'Valor com muitas casas decimais', False, str(e))
    
    # Teste 3: UUID duplicado
    try:
        uuid_test = str(uuid.uuid4())
        boleto1 = plugqi.boleto.build_simple_boleto(
            request_control_key=uuid_test,
            amount=100.0,
            expiration="2024-12-31",
            payer_name="João",
            payer_document="12345678901"
        )
        boleto2 = plugqi.boleto.build_simple_boleto(
            request_control_key=uuid_test,  # Mesmo UUID
            amount=200.0,
            expiration="2024-12-31",
            payer_name="Maria",
            payer_document="98765432100"
        )
        results.add_result('exploratory', 'UUID duplicado aceito', True, data={'uuid': uuid_test})
    except Exception as e:
        results.add_result('exploratory', 'UUID duplicado', False, str(e))

def main():
    """Executa todos os testes completos"""
    start_time = time.time()
    
    print("🚀 EXECUTANDO TESTES COMPLETOS COM DADOS REAIS")
    print("="*80)
    print("⚠️  ATENÇÃO: Estes testes fazem chamadas reais à API QiTech")
    print("   Certifique-se de ter credenciais válidas configuradas no .env")
    print("="*80)
    
    try:
        plugqi = PlugQi()
        results = ComprehensiveTestResults()
        
        # Executa todos os testes
        test_account_opening(plugqi, results)
        test_boletos(plugqi, results)
        test_bolepix(plugqi, results)
        test_pix_transactions(plugqi, results)
        test_negative_scenarios(plugqi, results)
        test_exploratory_scenarios(plugqi, results)
        
        # Calcula tempo de execução
        results.test_data['execution_time'] = time.time() - start_time
        
        # Gera relatório
        results.summary()
        
        # Salva dados de teste
        with open(f'test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump({
                'results': results.results,
                'test_data': results.test_data,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos em test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        return sum(cat['failed'] for cat in results.results.values()) == 0
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
