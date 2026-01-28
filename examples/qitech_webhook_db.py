from flask import Flask, request
import os
import json
import hmac
import hashlib
import datetime
import psycopg2
import psycopg2.extras
from risk_solution import RiskSolutionClient

app = Flask(__name__)

# Database connection string - use provided connection if not in env
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://plugz_dev_user:dev_password_123@207.180.209.127:5433/plugz_dev')
WEBHOOK_SECRET = os.environ.get('QITECH_WEBHOOK_SECRET', 'change-me')


def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.DictCursor)


def ensure_tables():
    sql_ext = "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
    sql_table = '''
    CREATE TABLE IF NOT EXISTS public.webhook_qitech (
      id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
      id_registro varchar(100),
      tipo_pessoa varchar(50),
      id_pessoa varchar(100),
      status_analise varchar(50),
      data_evento timestamptz,
      motivo text,
      conteudo jsonb,
      cabecalhos jsonb,
      assinatura varchar(200),
      assinatura_ok boolean,
      recebido_em timestamptz DEFAULT now(),
      tentativas integer DEFAULT 0,
      processado boolean DEFAULT false,
      processado_em timestamptz
    );
    '''
    with get_conn() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(sql_ext)
            except Exception:
                # extension may need superuser; ignore if fails
                pass
            cur.execute(sql_table)
        conn.commit()


def compute_signature(path: str, method: str, payload_text: str, secret: str) -> str:
    # Use same algorithm as risk_solution
    return RiskSolutionClient.compute_webhook_signature(path, method, payload_text, secret)


def insert_webhook(record: dict):
    insert_sql = '''
    INSERT INTO public.webhook_qitech (
        id_registro, tipo_pessoa, id_pessoa, status_analise, data_evento, motivo,
        conteudo, cabecalhos, assinatura, assinatura_ok, recebido_em
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    RETURNING id;
    '''
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(insert_sql, (
                record.get('registration_id'),
                record.get('person_type'),
                record.get('person_id'),
                record.get('analysis_status'),
                record.get('event_date'),
                record.get('reason'),
                psycopg2.extras.Json(record.get('payload')),
                psycopg2.extras.Json(record.get('headers')),
                record.get('signature'),
                record.get('signature_ok'),
                record.get('received_at')
            ))
            inserted = cur.fetchone()
        conn.commit()
    return inserted[0] if inserted else None


def insert_log(nivel: str, mensagem: str, detalhes: dict, endereco_ip: str, user_agent: str):
    # Insert into existing logs table if available
    insert_sql = '''
    INSERT INTO public.logs (nivel, mensagem, detalhes, endereco_ip, user_agent, criado_em)
    VALUES (%s, %s, %s, %s, %s, now())
    RETURNING id;
    '''
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(insert_sql, (nivel, mensagem, psycopg2.extras.Json(detalhes), endereco_ip, user_agent))
                inserted = cur.fetchone()
            conn.commit()
            return inserted[0] if inserted else None
    except Exception:
        return None


@app.route('/webhooks/qitech/onboarding', methods=['POST'])
def onboarding_webhook():
    ensure_tables()
    payload_text = request.get_data(as_text=True)
    received_sig = request.headers.get('Signature', '')
    expected = compute_signature(request.path, request.method, payload_text, WEBHOOK_SECRET)
    signature_ok = False
    try:
        signature_ok = hmac.compare_digest(expected, received_sig)
    except Exception:
        signature_ok = False

    record = {
        'received_at': datetime.datetime.utcnow(),
        'headers': dict(request.headers),
        'payload': None,
        'registration_id': None,
        'person_type': None,
        'person_id': None,
        'analysis_status': None,
        'event_date': None,
        'reason': None,
        'signature': received_sig,
        'signature_ok': signature_ok
    }

    try:
        parsed = json.loads(payload_text)
        record['payload'] = parsed
        # try common fields
        for k in ('registration_id', 'natural_person_id', 'legal_person_id', 'id'):
            if k in parsed:
                if k == 'natural_person_id':
                    record['person_type'] = 'natural_person'
                    record['person_id'] = parsed[k]
                elif k == 'legal_person_id':
                    record['person_type'] = 'legal_person'
                    record['person_id'] = parsed[k]
                else:
                    record['registration_id'] = parsed.get(k)
        record['analysis_status'] = parsed.get('analysis_status') or parsed.get('status')
        ev = parsed.get('event_date')
        if ev:
            try:
                record['event_date'] = datetime.datetime.fromisoformat(ev.replace('Z', '+00:00'))
            except Exception:
                record['event_date'] = None
        record['reason'] = parsed.get('reason')
    except Exception:
        record['payload'] = payload_text

    # persist webhook
    try:
        inserted_id = insert_webhook(record)
        insert_log('info', 'webhook_received', {'inserted_id': str(inserted_id)}, request.remote_addr, request.headers.get('User-Agent'))
    except Exception as e:
        insert_log('error', 'webhook_store_failed', {'error': str(e)}, request.remote_addr, request.headers.get('User-Agent'))

    if not signature_ok:
        return ('Forbidden', 403)
    # If signature ok and status indicates approval, attempt to create escrow reservation
    try:
        approved_values = {'APPROVED', 'approved', 'OK', 'ok'}
        if signature_ok and record.get('analysis_status') in approved_values:
            try:
                created = create_escrow_reservation_from_payload(record.get('payload'))
                insert_log('info', 'escrow_reservation_attempt', {'created': created}, request.remote_addr, request.headers.get('User-Agent'))
            except Exception as e:
                insert_log('error', 'escrow_reservation_failed', {'error': str(e)}, request.remote_addr, request.headers.get('User-Agent'))
    except Exception:
        pass

    return ('OK', 200)


@app.route('/webhooks/qitech/status', methods=['GET'])
def webhook_status():
    """GET endpoint to retrieve latest status by registration_id or person_id.

    Query params:
      - id_registro (registration id)
      - id_pessoa (person id)
      - tipo_pessoa (optional: 'natural_person' or 'legal_person')
    """
    id_registro = request.args.get('id_registro') or request.args.get('registration_id')
    id_pessoa = request.args.get('id_pessoa') or request.args.get('person_id')
    tipo_pessoa = request.args.get('tipo_pessoa') or request.args.get('person_type')

    if not id_registro and not id_pessoa:
        return ({'error': 'Informe id_registro ou id_pessoa como parâmetro de consulta'}, 400)

    # Build SQL to fetch latest record
    sql = "SELECT * FROM public.webhook_qitech WHERE 1=1"
    params = []
    if id_registro:
        sql += " AND id_registro = %s"
        params.append(id_registro)
    if id_pessoa:
        sql += " AND id_pessoa = %s"
        params.append(id_pessoa)
    if tipo_pessoa:
        sql += " AND tipo_pessoa = %s"
        params.append(tipo_pessoa)
    sql += " ORDER BY COALESCE(data_evento, recebido_em) DESC LIMIT 1"

    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
    except Exception as e:
        return ({'error': 'Erro ao consultar banco: ' + str(e)}, 500)

    if not row:
        return ({'status': 'not_found'}, 404)

    # Return a compact status summary
    result = {
        'id': str(row.get('id')),
        'id_registro': row.get('id_registro'),
        'tipo_pessoa': row.get('tipo_pessoa'),
        'id_pessoa': row.get('id_pessoa'),
        'status_analise': row.get('status_analise') or row.get('analysis_status'),
        'data_evento': row.get('data_evento') and row.get('data_evento').isoformat(),
        'motivo': row.get('motivo') or row.get('reason'),
        'recebido_em': row.get('recebido_em') and row.get('recebido_em').isoformat(),
        'conteudo': row.get('conteudo')
    }
    return (result, 200)


def create_escrow_reservation_from_payload(payload: dict) -> dict:
    """Cria uma reserva de conta Escrow usando dados mínimos do payload.

    Retorna o response do endpoint PlugQi ou lança exceção.
    """
    from plugqi import PlugQi

    plugqi = PlugQi()

    if not payload or not isinstance(payload, dict):
        raise ValueError('Payload inválido para criação de Escrow')

    # Infer person type
    person_type = None
    if 'natural_person_id' in payload or payload.get('person_type') in ('natural_person', 'natural'):
        person_type = 'natural'
    elif 'legal_person_id' in payload or payload.get('person_type') in ('legal_person', 'legal'):
        person_type = 'legal'

    if person_type == 'natural':
        owner = {
            'document_number': payload.get('cpf') or payload.get('document_number') or payload.get('natural_person_id'),
            'email': payload.get('email') or payload.get('contact_email'),
            'birthdate': payload.get('birthdate') or payload.get('birth_date'),
            'name': payload.get('name') or payload.get('full_name') or 'Nome Não Informado'
        }
        pf_payload = {'account_owner': owner}
        return plugqi.client.post('/account_request/escrow', pf_payload)

    if person_type == 'legal':
        owner = {
            'company_document_number': payload.get('cnpj') or payload.get('document_number') or payload.get('legal_person_id'),
            'email': payload.get('email') or payload.get('contact_email'),
            'name': payload.get('company_name') or payload.get('name') or 'Empresa'
        }
        pj_payload = {'account_owner': owner}
        return plugqi.client.post('/account_request/escrow/legal', pj_payload)

    raise ValueError('Não foi possível inferir tipo de pessoa para criação de Escrow')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '8000')))
