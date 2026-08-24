import sqlite3
import json
import os

DB_PATH = 'loterias.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela para os sorteios da API
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sorteios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concurso INTEGER NOT NULL,
            modalidade TEXT NOT NULL,
            data TEXT NOT NULL,
            dezenas TEXT NOT NULL,
            trevos TEXT
        )
    ''')
    
    # Tabela para salvar o histórico de gerações do usuário
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_geracao TEXT NOT NULL,
            modalidade TEXT NOT NULL,
            combinacao TEXT NOT NULL,
            trevos TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def concurso_existe(modalidade: str, concurso: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM sorteios WHERE modalidade = ? AND concurso = ?", (modalidade, concurso))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def inserir_sorteio(concurso: int, modalidade: str, data: str, dezenas: list, trevos: list = None):
    if concurso_existe(modalidade, concurso):
        return
        
    conn = get_connection()
    cursor = conn.cursor()
    
    dezenas_json = json.dumps(dezenas)
    trevos_json = json.dumps(trevos) if trevos else None
    
    cursor.execute('''
        INSERT INTO sorteios (concurso, modalidade, data, dezenas, trevos)
        VALUES (?, ?, ?, ?, ?)
    ''', (concurso, modalidade, data, dezenas_json, trevos_json))
    
    conn.commit()
    conn.close()

def buscar_sorteios(modalidade: str) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT concurso, data, dezenas, trevos FROM sorteios WHERE modalidade = ?", (modalidade,))
    rows = cursor.fetchall()
    conn.close()
    
    resultados = []
    for row in rows:
        resultados.append({
            'concurso': row[0],
            'data': row[1],
            'dezenas': json.loads(row[2]),
            'trevos': json.loads(row[3]) if row[3] else []
        })
    return resultados

def salvar_historico_usuario(modalidade: str, data_geracao: str, combinacao: list, trevos: list = None):
    conn = get_connection()
    cursor = conn.cursor()
    
    combinacao_json = json.dumps(combinacao)
    trevos_json = json.dumps(trevos) if trevos else None
    
    cursor.execute('''
        INSERT INTO historico_usuario (data_geracao, modalidade, combinacao, trevos)
        VALUES (?, ?, ?, ?)
    ''', (data_geracao, modalidade, combinacao_json, trevos_json))
    
    conn.commit()
    conn.close()
