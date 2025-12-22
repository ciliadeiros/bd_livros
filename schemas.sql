
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
    id_emprestimo INTEGER PRIMARY KEY,
    usuario_id INTEGER,
    livro_id INTEGER,
    data_emprestimo DATE,
    data_devolucao_prevista DATE,
    data_devolucao_real DATE,
    status_emprestimo TEXT CHECK(status_emprestimo IN ('pendente', 'devolvido', 'atrasado')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (livro_id) REFERENCES livros(id_livro) ON DELETE CASCADE
);

-- drop table log_triggers;

CREATE TABLE log_triggers (
    id_log INTEGER PRIMARY KEY AUTOINCREMENT,
    evento TEXT,
    mensagem TEXT,
    data_execucao DATETIME DEFAULT CURRENT_TIMESTAMP,
    lida INTEGER DEFAULT 0
);

---- triggers: Atualização Automática Pós-Evento ----

-- remove mesmos empréstimos duplicados e realizados antes da antiga data de devolução, mantendo o mais recente
create trigger if not exists remover_emprestimo_duplicado
after insert on emprestimos
begin
    delete from emprestimos
    where id_emprestimo != new.id_emprestimo
      and usuario_id = new.usuario_id
      and livro_id = new.livro_id
      and new.data_emprestimo <= data_devolucao_prevista;
end;

-- atualiza quantidade disponível do livro após exclusão do empréstimo
create trigger if not exists atualizar_quantidade_disponivel
after delete on emprestimos
begin
    update livros
    set quantidade_disponivel = quantidade_disponivel + 1
    where id_livro = old.livro_id;
end;

-- atualiza status para devolvido
create trigger if not exists atualizar_status_devolvido
after update on emprestimos
when new.data_devolucao_real IS NOT NULL
    and old.data_devolucao_prevista IS NOT NULL
    and new.data_devolucao_real <= old.data_devolucao_prevista
begin
    update emprestimos
    set status_emprestimo = 'devolvido'
    where id_emprestimo = new.id_emprestimo;
end;

-- atualiza status para atrasado
create trigger if not exists atualizar_status_atrasado
after update on emprestimos
when new.data_devolucao_real != null
 and old.data_devolucao_prevista != null
 and new.data_devolucao_real > old.data_devolucao_prevista
begin
    update emprestimos
    set status_emprestimo = 'atrasado'
    where id_emprestimo = new.id_emprestimo;
end;

-- registra log quando dados do empréstimo são alterados:
--> Obs.: Só começa a cadastrar os logs quando o usuário devolver o livro, já
-- quem não há como comparar enquanto data_devolucao_real for null
create trigger if not exists registrar_log_emprestimo_atualizado
after update on emprestimos
when (new.data_devolucao_real != old.data_devolucao_real or new.data_devolucao_prevista != old.data_devolucao_prevista
or new.data_emprestimo != old.data_emprestimo)
begin
    insert into log_triggers (mensagem)
    values ('Dado(s) do empréstimo atualizado(s)');
end;

-- registra log quando status do empréstimo muda
create trigger if not exists registrar_log_status_emprestimo
after update on emprestimos
when new.status_emprestimo != old.status_emprestimo
begin
    insert into log_triggers (mensagem)
    values ('Status do empréstimo alterado');
end;



