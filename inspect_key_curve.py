from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
import os

pem_path = os.path.join('keys', 'ec_p521_private.pem')
print('Inspecting:', pem_path)

try:
    with open(pem_path, 'rb') as f:
        data = f.read()
    key = serialization.load_pem_private_key(data, password=None, backend=default_backend())

    # EllipticCurvePrivateKey class
    EC_PRIV_CLASS = ec.EllipticCurvePrivateKey
    if isinstance(key, EC_PRIV_CLASS):
        curve = key.curve
        curve_name = type(curve).__name__
        mapped = curve_name
        if curve_name == 'SECP521R1':
            mapped = 'P-521 (SECP521R1)'
        print('Key is EC. Curve:', mapped)
    else:
        print('Loaded key is not an EC key. Type:', type(key))
except Exception:
    print('Error while loading key:')
    import traceback
    traceback.print_exc()
