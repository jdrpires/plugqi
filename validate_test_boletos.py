#!/usr/bin/env python3
"""
Validador de Boletos de Teste
Verifica se os payloads estão corretos para envio ao QA
"""
import json
from datetime import datetime

def validate_boleto(name, boleto):
    """Valida um boleto específico"""
    errors = []
    warnings = []
    
    # Campos obrigatórios
    required_fields = ["request_control_key", "amount", "expiration", "payer_data"]
    for field in required_fields:
        if field not in boleto:
            errors.append(f"Campo obrigatório ausente: {field}")
    
    # Validações específicas
    if "amount" in boleto:
        amount = boleto["amount"]
        if not isinstance(amount, (int, float)):
            errors.append("Amount deve ser numérico")
        elif amount < 0:
            errors.append("Amount não pode ser negativo")
        elif amount > 100000:
            warnings.append(f"Valor alto: R$ {amount:.2f}")
    
    # Validar data
    if "expiration" in boleto:
        try:
            exp_date = datetime.strptime(boleto["expiration"], "%Y-%m-%d")
            if exp_date <= datetime.now():
                warnings.append("Data de vencimento no passado ou hoje")
        except ValueError:
            errors.append("Formato de data inválido (use YYYY-MM-DD)")
    
    # Validar pagador
    if "payer_data" in boleto:
        payer = boleto["payer_data"]
        if "name" not in payer:
            errors.append("Nome do pagador obrigatório")
        if "document_number" not in payer:
            errors.append("Documento do pagador obrigatório")
        elif len(payer["document_number"]) not in [11, 14]:
            errors.append("Documento deve ter 11 (CPF) ou 14 (CNPJ) dígitos")
    
    # Validar multa
    if "fine_data" in boleto:
        fine = boleto["fine_data"]
        if fine.get("fine_type") == "percentage":
            if "fine_percentage" not in fine:
                errors.append("fine_percentage obrigatório para multa percentual")
            elif fine["fine_percentage"] > 100:
                warnings.append("Multa muito alta (>100%)")
    
    # Validar desconto
    if "discounts_data" in boleto:
        for i, discount in enumerate(boleto["discounts_data"]):
            if "discount_number" not in discount:
                errors.append(f"Desconto {i+1}: discount_number obrigatório")
            if discount.get("discount_type") == "percentage":
                if discount.get("discount_percentage", 0) > 100:
                    warnings.append(f"Desconto {i+1}: percentual muito alto")
    
    return errors, warnings

def main():
    """Valida todos os boletos de teste"""
    print("🔍 Validando Boletos de Teste para QA\n")
    
    try:
        with open("boletos_teste_qa.json", "r", encoding="utf-8") as f:
            boletos = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo boletos_teste_qa.json não encontrado")
        print("Execute: python3 generate_test_boletos.py")
        return 1
    
    total_errors = 0
    total_warnings = 0
    
    for name, boleto in boletos.items():
        print(f"🎫 Validando: {name}")
        
        errors, warnings = validate_boleto(name, boleto)
        
        if errors:
            print(f"  ❌ {len(errors)} erro(s):")
            for error in errors:
                print(f"     • {error}")
            total_errors += len(errors)
        
        if warnings:
            print(f"  ⚠️  {len(warnings)} aviso(s):")
            for warning in warnings:
                print(f"     • {warning}")
            total_warnings += len(warnings)
        
        if not errors and not warnings:
            print("  ✅ Válido")
        
        print()
    
    # Resumo
    print("="*50)
    print("📊 RESUMO DA VALIDAÇÃO")
    print("="*50)
    print(f"Total de boletos: {len(boletos)}")
    print(f"Erros encontrados: {total_errors}")
    print(f"Avisos: {total_warnings}")
    
    if total_errors == 0:
        print("\n🎉 Todos os boletos estão válidos para QA!")
        
        # Estatísticas
        print("\n📈 Estatísticas:")
        pessoa_fisica = sum(1 for b in boletos.values() if b.get("payer_data", {}).get("person_type") == "natural")
        pessoa_juridica = sum(1 for b in boletos.values() if b.get("payer_data", {}).get("person_type") == "legal")
        com_multa = sum(1 for b in boletos.values() if "fine_data" in b)
        com_desconto = sum(1 for b in boletos.values() if "discounts_data" in b)
        
        print(f"• Pessoa Física: {pessoa_fisica}")
        print(f"• Pessoa Jurídica: {pessoa_juridica}")
        print(f"• Com multa/juros: {com_multa}")
        print(f"• Com desconto: {com_desconto}")
        
        return 0
    else:
        print(f"\n⚠️  {total_errors} erro(s) encontrado(s)")
        print("Corrija os erros antes de enviar para QA")
        return 1

if __name__ == "__main__":
    exit(main())
