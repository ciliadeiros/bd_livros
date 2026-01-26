CREATE TABLE IF NOT EXISTS autores (
    id_autor INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_autor VARCHAR(255) NOT NULL,
    nacionalidade VARCHAR(255),
    data_nascimento DATE,
    biografia TEXT,
    idade_autor INTEGER
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
    dias_emprestimo INTEGER, -- coloquei aqui pra ser calculado automaticamente e faciltar a vida
    status_emprestimo TEXT CHECK(status_emprestimo IN ('pendente', 'devolvido', 'atrasado')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (livro_id) REFERENCES livros(id_livro) ON DELETE CASCADE
);

-- drop table log_triggers;

CREATE TABLE if not exists log_triggers (
    id_log INTEGER PRIMARY KEY AUTOINCREMENT,
    evento TEXT,
    mensagem TEXT,
    data_execucao DATETIME DEFAULT CURRENT_TIMESTAMP,
    lida INTEGER DEFAULT 0
);

---- triggers: Atualização Automática Pós-Evento ----

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
when
    new.data_devolucao_real is not null
    and new.data_devolucao_prevista is not null
    and new.data_devolucao_real <= new.data_devolucao_prevista
begin
    update emprestimos
    set status_emprestimo = 'devolvido'
    where id_emprestimo = new.id_emprestimo;
end;


-- atualiza status para atrasado
create trigger if not exists atualizar_status_atrasado
after update on emprestimos
when
    new.data_devolucao_real is not null
    and new.data_devolucao_prevista is not null
    and new.data_devolucao_real > new.data_devolucao_prevista
begin
    update emprestimos
    set status_emprestimo = 'atrasado'
    where id_emprestimo = new.id_emprestimo;
end;


-- registra log quando dados do empréstimo são alterados:
--> Obs.: Só começa a cadastrar os logs quando o usuário devolver o livro, já
-- que não há como comparar enquanto data_devolucao_real for null
create trigger if not exists registrar_log_emprestimo_atualizado
after update on emprestimos
when (new.data_devolucao_real != old.data_devolucao_real or new.data_devolucao_prevista != old.data_devolucao_prevista
or new.data_emprestimo != old.data_emprestimo)
begin
    insert into log_triggers (mensagem)
    values ('Emprestimo atualizado com sucesso!');
end;

-- registra log quando status do empréstimo muda
create trigger if not exists registrar_log_status_emprestimo
after update on emprestimos
when new.status_emprestimo != old.status_emprestimo
begin
    insert into log_triggers (mensagem)
    values ('Status do emprestimo alterado com sucesso!');
end;


---- triggers: Auditoria ----
create trigger if not exists resgistrar_log_usuario
after insert on usuarios
begin
    insert into log_triggers (mensagem)
    values('Um novo usuário foi inserido');
end;

create trigger if not exists resgistrar_editar_livro
after update on livros
begin
    insert into log_triggers (mensagem)
    values('Um livro foi editado');
end;

create trigger if not exists resgistrar_excluir_livro
after delete on livros
begin
    insert into log_triggers (mensagem)
    values('Um livro foi excluido do catalogo');
end;

create trigger if not exists resgistrar_log_autor
after insert on autores
begin
    insert into log_triggers (mensagem)
    values('Um novo autor foi inserido');
end;

create trigger if not exists resgistrar_editar_autor
after update on autores
begin
    insert into log_triggers (mensagem)
    values('Um autor foi editado');
end;

---- triggers: Geração Automática de Valores ----

-- preenche a data de inscrção do usuário automaticamente
create trigger if not exists preencher_data_inscricao
after insert on usuarios
when new.data_inscricao is null
begin
    update usuarios
    set data_inscricao = date('now')
    where id_usuario = new.id_usuario;
end;

-- calcula a idade dos autores automaticamente
create trigger if not exists calcular_idade_autor
after insert on autores
when new.data_nascimento is not null
begin
    update autores
    set idade_autor = cast((julianday('now') - julianday(new.data_nascimento)) / 365 as integer)
    where id_autor = new.id_autor;
end;
-- o cast serve para transformar o resultado em inteiro
-- o julianday transforma a data em um número de dias

-- calcula dias de empréstimo
create trigger if not exists calcular_ias_emprestimo
after insert on emprestimos
when new.data_devolucao_prevista is not null
begin
    update emprestimos
    set dias_emprestimo = julianday(new.data_devolucao_prevista) - julianday(new.data_emprestimo)
    where id_emprestimo = new.id_emprestimo;
end;

-- define data de empréstimo padrão caso não informada - no caso,  data atual
create trigger if not exists definir_data_emprestimo
after insert on emprestimos
when new.data_emprestimo is null
begin
    update emprestimos
    set data_emprestimo = date('now')
    where id_emprestimo = new.id_emprestimo;
end;


-- Avisa sobre emprestimos atrasados
create trigger if not exists avisar_se_status_emprestimo_atrasado
after update on emprestimos
when new.status_emprestimo = 'atrasado' and old.status_emprestimo != 'atrasado' 
begin
    insert into log_triggers (mensagem)
    values ('Empréstimo atrasado!');
end;

---- triggers: Validação  ----

---- Impede que o usuário se cadastre com campos vazios ----
create trigger if not exists validar_usuario
before insert on usuarios
when
    new.nome_usuario is null or new.nome_usuario = ''
    or new.senha_usuario is null or new.senha_usuario = ''
    or new.email is null or new.email = ''
    or new.numero_telefone is null or new.numero_telefone = ''
begin
    insert into log_triggers (mensagem)
    values ('Preencha todos os campos.');

    select raise(fail, 'Preencha todos os campos.');
end;

---- Impede que o usuário cadastre um autor com campos vazios ----
create trigger if not exists validar_autor
before insert on autores
when
    new.nome_autor is null or new.nome_autor = ''
    or new.nacionalidade is null or new.nacionalidade = ''
    or new.data_nascimento is null or new.data_nascimento = ''
    or new.biografia is null or new.biografia = ''
begin
    insert into log_triggers (mensagem)
    values ('Preencha todos os campos.');

    select raise(fail, 'Preencha todos os campos.');
end;

---- Impede que o usuário cadastre uma editora com campos vazios ----
create trigger if not exists validar_editora
before insert on editoras
when
    new.nome_editora is null or new.nome_editora = ''
    or new.endereco_editora is null or new.endereco_editora = ''
begin
    insert into log_triggers (mensagem)
    values ('Preencha todos os campos.');

    select raise(fail, 'Preencha todos os campos.');
end;

---- Impedir adição de mais de um livro com o mesmo ISBN ----
create trigger if not exists validar_isbn_unico
before insert on livros
when exists (
    select 1
    from livros
    where isbn = new.isbn
)
begin
    insert into log_triggers (mensagem)
    values ('Existe um livro cadastrado com este ISBN.');

    select raise(fail, 'Existe um livro cadastrado com este ISBN.');
end;

---- Impedir email repetido ----
create trigger if not exists validar_email
before insert on usuarios
when exists (
    select 1
    from usuarios
    where email = new.email
)
begin
    insert into log_triggers (mensagem)
    values ('Existe um usuário cadastrado com este email.');

    select raise(fail, 'Existe um usuário cadastrado com este email.');
end;

---- Impedir que o usuário registre um livro com info faltando ----
CREATE TRIGGER IF NOT EXISTS validar_livro_campos
BEFORE UPDATE ON livros
WHEN
    new.autor_id IS NULL
    OR new.titulo IS NULL OR trim(new.titulo) = ''
    OR new.isbn IS NULL OR trim(new.isbn) = ''
    OR new.ano_publicacao IS NULL
    OR new.genero_id IS NULL
    OR new.editora_id IS NULL
    OR new.quantidade_disponivel IS NULL
BEGIN
    INSERT INTO log_triggers (mensagem)
    VALUES ('Preencha todos os campos.');

    SELECT RAISE(fail, 'Preencha todos os campos.');
END;