
-- DROP TABLE IF EXISTS usuarios;

CREATE TABLE IF NOT EXISTS autores (
    id_autor INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_autor VARCHAR(255) NOT NULL,
    nacionalidade VARCHAR(255),
    data_nascimento DATE,
    biografia TEXT
);

CREATE TABLE IF NOT EXISTS generos (
    id_genero INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_genero VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS editoras (
    id_editora INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_editora VARCHAR(255) NOT NULL,
    endereco_editora TEXT
);

CREATE TABLE IF NOT EXISTS livros (
    id_livro INTEGER PRIMARY KEY AUTOINCREMENT,
    autor_id INTEGER NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    isbn VARCHAR(13) NOT NULL,
    ano_publicacao INTEGER NOT NULL,
    genero_id INTEGER NOT NULL,
    editora_id INTEGER NOT NULL,
    quantidade_disponivel INTEGER NOT NULl,
    resumo TEXT,
    FOREIGN KEY (autor_id) REFERENCES autores(id_autor) ON DELETE RESTRICT,
    FOREIGN KEY (genero_id) REFERENCES generos(id_genero) ON DELETE CASCADE,
);

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    senha_usuario VARCHAR(8) NOT NULL,
    nome_usuario VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    numero_telefone VARCHAR(15),
    data_inscricao DATE,
    multa_atual DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS emprestimos (
    id_emprestimo INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    livro_id INTEGER,
    data_emprestimo DATE,
    data_devolucao_prevista DATE,
    data_devolucao_real DATE,
    status_emprestimo TEXT CHECK(status_emprestimo IN ('pendente', 'devolvido', 'atrasado')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (livro_id) REFERENCES livros(id_livro) ON DELETE CASCADE
);

conn = obter_conexao()
cursor = conn.cursor()

create_trigger_sql = '''
create trigger imperdir_quatidade_negativa before insert
on livros
for each row
begin
	SELECT RAISE(ABORT)
    WHERE NEW.quantidade_disponivel < 0;
end;'''

cursor.execute(create_trigger_sql)
conn.commit()

-- create trigger nome momento evento
-- on tabela
-- for each row
-- begin
-- #corpo do codigo
-- end