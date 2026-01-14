import os
from typing import Any, Dict, Optional
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=False)

DATABASE_URL = os.getenv("DATABASE_URL")


def get_conn():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL não configurado")
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.DictCursor)


def insert_qi_ocr(
    chave_api: Optional[str],
    modelo: Optional[str],
    tipo_arquivo: Optional[str],
    nome_arquivo: Optional[str],
    id_imagem: Optional[str],
    requisicao: Optional[Dict[str, Any]],
    resposta: Optional[Dict[str, Any]],
    resposta_texto: Optional[str],
    codigo_status: Optional[int],
    duracao_ms: Optional[int],
    ip_cliente: Optional[str],
    agente_usuario: Optional[str],
    mensagem_erro: Optional[str],
    observacoes: Optional[str] = None,
):
    """Insere um registro na tabela `qi_ocr` (campos em pt-BR).

    Nota: `requisicao` e `resposta` devem ser dicionários serializáveis para JSON.
    """
    insert_sql = """
    INSERT INTO qi_ocr (
        chave_api, modelo, tipo_arquivo, nome_arquivo, id_imagem,
        requisicao, resposta, resposta_texto, codigo_status, duracao_ms,
        ip_cliente, agente_usuario, mensagem_erro, observacoes
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    RETURNING id;
    """

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(insert_sql, (
                chave_api,
                modelo,
                tipo_arquivo,
                nome_arquivo,
                id_imagem,
                psycopg2.extras.Json(requisicao) if requisicao is not None else None,
                psycopg2.extras.Json(resposta) if resposta is not None else None,
                resposta_texto,
                codigo_status,
                duracao_ms,
                ip_cliente,
                agente_usuario,
                mensagem_erro,
                observacoes,
            ))
            inserted = cur.fetchone()
        conn.commit()

    return str(inserted[0]) if inserted else None


def insert_qi_face_recognition(
    chave_api: Optional[str],
    modelo: Optional[str],
    tipo_arquivo: Optional[str],
    nome_arquivo: Optional[str],
    id_imagem: Optional[str],
    requisicao: Optional[Dict[str, Any]],
    resposta: Optional[Dict[str, Any]],
    resposta_texto: Optional[str],
    codigo_status: Optional[int],
    duracao_ms: Optional[int],
    ip_cliente: Optional[str],
    agente_usuario: Optional[str],
    mensagem_erro: Optional[str],
    observacoes: Optional[str] = None,
):
    """Insere um registro na tabela `qi_face_recognition`.

    Mesma estrutura de campos usada em `qi_ocr` para manter consistência.
    """
    insert_sql = """
    INSERT INTO qi_face_recognition (
        chave_api, modelo, tipo_arquivo, nome_arquivo, id_imagem,
        requisicao, resposta, resposta_texto, codigo_status, duracao_ms,
        ip_cliente, agente_usuario, mensagem_erro, observacoes
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    RETURNING id;
    """

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(insert_sql, (
                chave_api,
                modelo,
                tipo_arquivo,
                nome_arquivo,
                id_imagem,
                psycopg2.extras.Json(requisicao) if requisicao is not None else None,
                psycopg2.extras.Json(resposta) if resposta is not None else None,
                resposta_texto,
                codigo_status,
                duracao_ms,
                ip_cliente,
                agente_usuario,
                mensagem_erro,
                observacoes,
            ))
            inserted = cur.fetchone()
        conn.commit()

    return str(inserted[0]) if inserted else None


def insert_qi_device_scan(
    chave_api: Optional[str],
    evento_tipo: Optional[str],
    session_id: Optional[str],
    requisicao: Optional[Dict[str, Any]],
    resposta: Optional[Dict[str, Any]],
    resposta_texto: Optional[str],
    codigo_status: Optional[int],
    duracao_ms: Optional[int],
    ip_cliente: Optional[str],
    agente_usuario: Optional[str],
    mensagem_erro: Optional[str],
    observacoes: Optional[str] = None,
):
    """Insere um registro na tabela `qi_device_scan`.

    Campos adaptados para device scan; manteremos formato JSON para requisicao/resposta.
    """
    insert_sql = """
    INSERT INTO qi_device_scan (
        chave_api, evento_tipo, session_id,
        requisicao, resposta, resposta_texto, codigo_status, duracao_ms,
        ip_cliente, agente_usuario, mensagem_erro, observacoes
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    RETURNING id;
    """

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(insert_sql, (
                chave_api,
                evento_tipo,
                session_id,
                psycopg2.extras.Json(requisicao) if requisicao is not None else None,
                psycopg2.extras.Json(resposta) if resposta is not None else None,
                resposta_texto,
                codigo_status,
                duracao_ms,
                ip_cliente,
                agente_usuario,
                mensagem_erro,
                observacoes,
            ))
            inserted = cur.fetchone()
        conn.commit()

    return str(inserted[0]) if inserted else None
