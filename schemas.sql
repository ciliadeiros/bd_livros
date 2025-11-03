-- DROP TABLE IF EXISTS usuarios;

CREATE TABLE IF NOT EXISTS autores (
  id_autor INT AUTOINCREMENT PRIMARY KEY,
  nome_autor VARCHAR(255) NOT NULL,
  nacionalidade VARCHAR(255),
  data_nascimento DATE,
  biografia TEXT  
);

CREATE TABLE IF NOT EXISTS Generos (
    id_genero INT AUTOINCREMENT PRIMARY KEY,
    nome_genero VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS editoras (
    id_editora INT PRIMARY KEY AUTOINCREMENT,
    nome_editora VARCHAR(255) NOT NULL,
    endereco_editora TEXT,    
);

CREATE TABLE IF NOT EXISTS livros (
    id_livro INTEGER PRIMARY KEY AUTOINCREMENT, 
    autor_id INT NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    isbn VARCHAR(13) NOT NULL,
    ano_publicacao INT,
    genero_id INT,
    editora_id INT,
    quantidade_disponivel INT,
    resumo TEXT,
    FOREIGN KEY (autor_id) REFERENCES autores(id_autor)
    FOREIGN KEY (genero_id) REFERENCES generos(id_genero)
    FOREIGN KEY (editora_id) REFERENCES editoras(id_editora)
);

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTOINCREMENT PRIMARY KEY,
    senha_usuario VARCHAR(8) NOT NULL,
    nome_usuario VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    numero_telefone VARCHAR(15),
    data_inscricao DATE,
    multa_atual DECIMAL(10,2)    
);

--DROP TABLE IF EXISTS livros;

CREATE TABLE IF NOT EXISTS Emprestimos (
    id_emprestimo INT AUTOINCREMENT PRIMARY KEY,
    usuario_id INT,
    livro_id INT,
    data_emprestimo DATE,
    data_devolucao_prevista DATE,
    data_devolucao_real DATE,
    status_emprestimo ENUM('pendente', 'devolvido', 'atrasado'),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (livro_id) REFERENCES livros(ID_livro)
);