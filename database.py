import sqlite3

def obter_conexao():
    conexao = sqlite3.connect(
        'livros.db',
        timeout=30,
        isolation_level=None
    )
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.execute("PRAGMA journal_mode = WAL")
    conexao.execute("PRAGMA busy_timeout = 30000")
    conexao.row_factory = sqlite3.Row
    return conexao

