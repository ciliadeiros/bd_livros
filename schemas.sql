
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
    quantidade_disponivel INTEGER NOT NULL,
    resumo TEXT,
    FOREIGN KEY (autor_id) REFERENCES autores(id_autor) ON DELETE RESTRICT,
    FOREIGN KEY (genero_id) REFERENCES generos(id_genero) ON DELETE CASCADE,
    FOREIGN KEY (editora_id) REFERENCES editoras(id_editora)
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

CREATE TABLE IF NOT EXISTS log_emprestimo (
    id_log INTEGER PRIMARY KEY AUTOINCREMENT,
    emprestimo_id INTEGER NOT NULL,
    acao TEXT NOT NULL,
    data_evento DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emprestimo_id) REFERENCES emprestimos(id_emprestimo)
);

-- Após registrar um mesmo empréstimo mais de uma vez,
-- ele é deletado automaticamente e somente o mais atual permanece (por consequência)
create trigger if not exists remover_emprestimo_duplicado
after insert on emprestimos
for each row
begin
    delete from emprestimos
    where id_emprestimo != NEW.id_emprestimo
    and usuario_id = NEW.usuario_id
    and livro_id = NEW.livro_id
    and data_emprestimo = NEW.data_emprestimo;
end;

-- Esse trigger registra log do empréstimo após seus dado(s) serem atualizados
create trigger if not exists registar_log_emprestimo__atualizado
after update on emprestimos
for each row
begin
    insert into log_emprestimo (emprestimo_id, acao)
    values (NEW.id_emprestimo, 'Dados do emprestimo atualizado(s)');
END;



