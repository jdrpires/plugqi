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


def insert_qi_auth_session(
    chave_api: Optional[str],
    external_id: Optional[str],
    cpf: Optional[str],
    cpf_formatado: Optional[str],
    token: Optional[str],
    original_link: Optional[str],
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
    """Insere um registro na tabela `qi_auth_session`.

    Campos principais:
    - `chave_api`: chave usada na requisição (opcional)
    - `cpf` / `cpf_formatado`
    - `token`: token interno white-label (se gerado)
    - `original_link`: link retornado pelo provedor (antes do redirecionamento)
    - `requisicao` / `resposta`: JSONs brutos
    - `resposta_texto`: versão em texto para pesquisa/log
    - demais metadados
    """
    insert_sql = """
    INSERT INTO qi_auth_session (
        chave_api, external_id, cpf, cpf_formatado, token, original_link,
        requisicao, resposta, resposta_texto, codigo_status, duracao_ms,
        ip_cliente, agente_usuario, mensagem_erro, observacoes
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    RETURNING id;
    """

    with get_conn() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(insert_sql, (
                    chave_api,
                    external_id,
                    cpf,
                    cpf_formatado,
                    token,
                    original_link,
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
            except psycopg2.errors.UndefinedColumn:
                # Fallback for databases without external_id column: run insert without that column
                alt_sql = """
                INSERT INTO qi_auth_session (
                    chave_api, cpf, cpf_formatado, token, original_link,
                    requisicao, resposta, resposta_texto, codigo_status, duracao_ms,
                    ip_cliente, agente_usuario, mensagem_erro, observacoes
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id;
                """
                cur.execute(alt_sql, (
                    chave_api,
                    cpf,
                    cpf_formatado,
                    token,
                    original_link,
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


def insert_qi_document(
    chave_api: Optional[str],
    document_key: Optional[str],
    filename: Optional[str],
    file_type: Optional[str],
    size: Optional[int],
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
    """Insere log da operação de upload/consulta de documentos na tabela `qi_document_upload`.

    Campos: chave_api, document_key, filename, file_type, size, requisicao, resposta,
    resposta_texto, codigo_status, duracao_ms, ip_cliente, agente_usuario, mensagem_erro, observacoes
    """
    insert_sql = """
    INSERT INTO qi_document_upload (
        chave_api, document_key, filename, file_type, size,
        requisicao, resposta, resposta_texto, codigo_status, duracao_ms,
        ip_cliente, agente_usuario, mensagem_erro, observacoes
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    RETURNING id;
    """

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(insert_sql, (
                chave_api,
                document_key,
                filename,
                file_type,
                size,
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
