import os, sys

from qitech_client import QiTechClient

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


ABS = "/Users/jeanpires/GitHub/plugqi/keys/ec_p521_private.pem"  # ajuste se diferente
c = QiTechClient(private_key_path=ABS)  # força caminho absoluto
print("OK: chave carregada. Cabeçalho:", c.private_key_pem.splitlines()[0])
