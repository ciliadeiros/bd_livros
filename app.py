from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from database import obter_conexao
from modelos import User
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import sqlite3
import datetime

login_manager = LoginManager()
login_manager.login_view = 'login'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///livros.db'
app.secret_key = 'ablublublu'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.achar_email(user_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=["GET", "POST"])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email'] 
        senha = request.form['senha']
        numero_telefone = request.form['numero_telefone']
        data_inscricao = datetime.date.today()
        
        conexao = obter_conexao()
        sql = "SELECT * FROM usuarios WHERE email = ?"
        resultado = conexao.execute(sql, (email,) ).fetchone()
        
        if not resultado:
            novo_usuario = User(senha=senha, nome=nome, email=email, numero_telefone=numero_telefone, data_inscricao=data_inscricao)
            novo_usuario.add_usuario()

            # login do usuário
            user = User(senha=senha, nome=nome, email=email, numero_telefone=numero_telefone, data_inscricao=data_inscricao)
            user.id = email
            login_user(user)

            return redirect(url_for('index'))

        else:
            flash('E-mail já cadastrado. Tente outro.', category='error')
            conexao.close()

    return render_template('cadastro.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        usuario = User.selecionar_usuario(email)

        if usuario and usuario.senha==senha:
            login_user(usuario)
            flash('Login feito com sucesso!', category='success')
            return redirect(url_for('livros'))    
        else:
            flash('Opa, você não tem cadastro. Entre na página de cadastro e se registre!', category='error')

    else:
        return render_template('login.html')
    
@app.route('/logout', methods=["POST", "GET"])
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/registrar_autor', methods =["GET","POST"])
def registrar_autor():
    if request.method == "POST":
        nome_au = request.form['nome']
        nacionalidade = request.form['nacionalidade']
        data_nascimento = request.form['data_nascimento']
        biografia = request.form['biografia']
    
        conexao = obter_conexao()
        sql = """INSERT INTO autores (nome_autor, nacionalidade, data_nascimento, biografia) VALUES (?,?,?,?)"""
        conexao.execute(sql,(nome_au,nacionalidade,data_nascimento,biografia))
        conexao.commit()
        conexao.close
        return redirect(url_for('criar_livros'))
    else:
        render_template('criar_livros.html')

@app.route('/autores', methods=["GET","POST"])
def autores():
    conexao = obter_conexao()
    autores = conexao.execute('SELECT * FROM autores').fetchall()
    conexao.close()
    return render_template('autores.html')

@app.route('/editar_autor', methods=["GET","POST"])
def editar_autor():
    if request.method == "POST":
        novo_nome = request.form['nome']
        novo_nacionalidade = request.form['nacionalidade']
        novo_data_nascimento = request.form['data_nascimento']
        nova_biografia = request.form['biografia']
        conexao = obter_conexao()
        sql = """"UPDATE autores (nome,nacionalidade,data_nascimento,biografia), WHERE id_autor = ?
        VALUES(?,?,?,?)"""
        conexao.execute(sql,(novo_nome,novo_nacionalidade,novo_data_nascimento,nova_biografia))
        conexao.close()
    return render_template('editar_autor.html')


@app.route('/livros', methods=["GET", "POST"])
def livros():
    conexao = obter_conexao()

    sql = """
        SELECT 
            livros.id_livro,
            livros.titulo,
            autores.nome_autor AS autor,
            generos.nome_genero AS genero,
            editoras.nome_editora AS editora,
            livros.isbn,
            livros.ano_publicacao,
            livros.quantidade_disponivel,
            livros.resumo
        FROM livros
        LEFT JOIN autores ON livros.autor_id = autores.id_autor
        LEFT JOIN generos ON livros.genero_id = generos.id_genero
        LEFT JOIN editoras ON livros.editora_id = editoras.id_editora
        ORDER BY livros.titulo
    """

    livros = conexao.execute(sql).fetchall()
    conexao.close()

    return render_template('livros.html', livros=livros)

@app.route('/criar_livros', methods=["GET", "POST"])
def criar_livros():
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor_nome = request.form['autor']
        isbn = request.form['isbn']
        ano_publicacao = request.form['ano_publicacao']
        genero = request.form['genero']
        editora = request.form['editora']
        quantidade_disponivel = request.form['quantidade_disponivel']
        resumo = request.form['resumo']

        conexao = obter_conexao()

        # Procura o autor no banco de dados
        sql = """SELECT id_autor FROM autores WHERE nome_autor = ?"""
        autor_resultado = conexao.execute(sql, (autor_nome,)).fetchone()

        if autor_resultado is None: # Caso o autor não seja encontrado
            conexao.close()
            return render_template('criar_livros.html',autor_nao_existe=True,autor_nome=autor_nome,titulo=titulo,isbn=isbn,ano_publicacao=ano_publicacao,genero=genero,editora=editora,quantidade_disponivel=quantidade_disponivel,resumo=resumo)

        autor_id = autor_resultado['id_autor']

        # Insere o livro com SQL puro
        conexao.execute(
            """INSERT INTO livros 
               (titulo, autor_id, isbn, ano_publicacao, genero_id, editora_id, quantidade_disponivel, resumo)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (titulo, autor_id, isbn, ano_publicacao, genero, editora, quantidade_disponivel, resumo)
        )

        conexao.commit()
        conexao.close()
        return redirect(url_for('livros'))

    # Se for GET, só exibe o formulário normal
    return render_template('criar_livros.html')

@app.route('/editar_livros', methods=["GET","POST"])
def editar_livros():
    if request.method == "POST":
        n_titulo = request.form['titulo']
        n_autor = request.form['autor']
        n_isbn = request.form['isbn']
        n_ano_publicacao = request.form['ano_publicacao']
        n_genero = request.form['genero']
        n_editora = request.form['editora']
        n_quantidade_disponivel = request.form['quantidade_disponivel']
        n_resumo = request.form['resumo']
        conexao = obter_conexao()
        sql = """UPDATE livros (titulo, autor, isbn, ano_publicacao, genero, editora, quantidade_disponivel, resumo) WHERE id_livro = ?
        VALUES(?,?,?,?,?,?,?,?)"""
        conexao.execute(sql,(n_titulo,n_autor,n_isbn,n_ano_publicacao,n_genero,n_editora,n_quantidade_disponivel,n_resumo))
        
        sql = """
        SELECT 
            livros.id_livro AS id_livro,
            livros.titulo AS titulo,
            autores.nome_autor AS autor,
            generos.nome_genero AS genero,
            editoras.nome_editora AS editora,
            livros.isbn,
            livros.ano_publicacao,
            livros.quantidade_disponivel,
            livros.resumo
        FROM livros
        LEFT JOIN autores ON livros.autor_id = autores.id_autor
        LEFT JOIN generos ON livros.genero_id = generos.id_genero
        LEFT JOIN editoras ON livros.editora_id = editoras.id_editora
        ORDER BY livros.titulo
        """
        livro_resultado = conexao.execute(sql).fetchone()
        conexao.close()

    else:
        return render_template('editar_livros.html', livro = livro_resultado)

@app.route('/remover_livro', methods=['POST'])
def remover_livro():
    id_livro = request.form['id']
    conexao = obter_conexao()
    conexao.execute('DELETE FROM livros WHERE id_livro = ?', (id_livro,))
    conexao.commit()
    conexao.close()
    return redirect(url_for('livros'))

if __name__ == '__main__':
    app.run(debug=True)