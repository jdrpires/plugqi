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
      id uuid NOT NULL DEFAULT uuid_generate_v4(),
      registration_id character varying(100) NULL,
      person_type character varying(50) NULL,
      person_id character varying(100) NULL,
      analysis_status character varying(50) NULL,
      event_date timestamp without time zone NULL,
      reason text NULL,
      payload jsonb NULL,
      headers jsonb NULL,
      signature character varying(200) NULL,
      signature_ok boolean NULL,
      received_at timestamp without time zone NULL DEFAULT now(),
      attempt_count integer DEFAULT 0,
      processed boolean DEFAULT false,
      processed_at timestamp without time zone NULL
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
        registration_id, person_type, person_id, analysis_status, event_date, reason,
        payload, headers, signature, signature_ok, received_at
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
    return ('OK', 200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '8000')))
