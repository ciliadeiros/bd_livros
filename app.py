from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from database import obter_conexao
from modelos import User
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import sqlite3
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

login_manager = LoginManager()
login_manager.loginovo_view = 'login'
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

        if usuario and usuario.senha == senha:
            login_user(usuario)
            flash('Login feito com sucesso!', category='success')
            return redirect(url_for('livros'))
        else:
            flash('Opa, você não tem cadastro. Entre na página de cadastro e se registre!', category='error')
            return render_template('login.html')  

    # para requisições GET
    return render_template('login.html')

@app.route('/logout', methods=["POST", "GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/registrar_autor', methods=["GET", "POST"])
@login_required
def registrar_autor():
    if request.method == "POST":
        nome_au = request.form['nome']
        nacionalidade = request.form['nacionalidade']
        data_nascimento = request.form['data_nascimento']
        biografia = request.form['biografia']
    
        conexao = obter_conexao()
        sql = """INSERT INTO autores (nome_autor, nacionalidade, data_nascimento, biografia)
                 VALUES (?,?,?,?)"""
        conexao.execute(sql, (nome_au, nacionalidade, data_nascimento, biografia))
        conexao.commit()
        conexao.close() 
        return redirect(url_for('autores'))

    return render_template('registrar_autor.html')

@app.route('/autores', methods=["GET","POST"])
def autores():
    conexao = obter_conexao()
    autores = conexao.execute('SELECT * FROM autores').fetchall()
    conexao.close()
    return render_template('autores.html',autores = autores)

@app.route('/editar_autor', methods=["GET", "POST"])
@login_required
def editar_autor():
    conexao = obter_conexao()

    if request.method == "POST":
        id_autor = request.form['id_autor']
        novo_nome = request.form['nome']
        novo_nacionalidade = request.form['nacionalidade']
        novo_data_nascimento = request.form['data_nascimento']
        nova_biografia = request.form['biografia']

        sql = """UPDATE autores
                 SET nome_autor = ?, nacionalidade = ?, data_nascimento = ?, biografia = ?
                 WHERE id_autor = ?"""
        conexao.execute(sql, (novo_nome, novo_nacionalidade, novo_data_nascimento, nova_biografia, id_autor))
        conexao.commit()
        conexao.close()
        flash('Autor atualizado com sucesso!', 'success')
        return redirect(url_for('autores'))

    else:
        id_autor = request.args.get('id') 
        cursor = conexao.execute("SELECT * FROM autores WHERE id_autor = ?", (id_autor,))
        autor = cursor.fetchone()
        conexao.close()

        return render_template('editar_autor.html', autor=autor)

@app.route('/remover_autor/<int:id>', methods=['POST'])
@login_required
def remover_autor(id):
    conexao = obter_conexao()

    sql = """
        DELETE FROM autores
        WHERE id_autor = ?
        AND id_autor NOT IN (SELECT autor_id FROM livros)
    """
    conexao.execute(sql, (id,))

    conexao.commit()
    conexao.close()

    return redirect(url_for('autores'))

@app.route('/livros', methods=["GET", "POST"])
@login_required
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

@app.route('/criar_livro', methods=["GET", "POST"])
@login_required
def criar_livro():
    conexao = obter_conexao()

    if request.method == "POST":
        titulo = request.form['titulo']
        autor = request.form['autor']
        isbn = request.form['isbn']
        ano_publicacao = request.form['ano_publicacao']
        genero = request.form['genero']
        editora = request.form['editora']
        quantidade_disponivel = request.form['quantidade_disponivel']
        resumo = request.form['resumo']

        # AUTOR
        autor_resultado = conexao.execute(
            "SELECT id_autor FROM autores WHERE nome_autor = ?", (autor,)
        ).fetchone()

        if autor_resultado is None and 'nacionalidade' not in request.form:
            conexao.close()
            return render_template('criar_livro.html',livro={'titulo': titulo, 'isbn': isbn, 'ano_publicacao': ano_publicacao,'genero': genero, 'editora': editora,'quantidade_disponivel': quantidade_disponivel, 'resumo': resumo,'autor': autor},autor_nao_existe=True, autor_nome=autor)

        if autor_resultado is None:
            conexao.execute(
                "INSERT INTO autores (nome_autor, nacionalidade, data_nascimento, biografia) VALUES (?, ?, ?, ?)",
                (autor, request.form['nacionalidade'], request.form['data_nascimento'], request.form['biografia'])
            )
            conexao.commit()
            autor_resultado = conexao.execute(
                "SELECT id_autor FROM autores WHERE nome_autor = ?", (autor,)
            ).fetchone()

        autor_id = autor_resultado['id_autor']

        # GÊNERO
        genero_resultado = conexao.execute(
            "SELECT id_genero FROM generos WHERE nome_genero = ?", (genero,)
        ).fetchone()
        if genero_resultado is None:
            conexao.execute("INSERT INTO generos (nome_genero) VALUES (?)", (genero,))
            conexao.commit()
            genero_resultado = conexao.execute(
                "SELECT id_genero FROM generos WHERE nome_genero = ?", (genero,)
            ).fetchone()
        genero_id = genero_resultado['id_genero']

        # EDITORA
        editora_resultado = conexao.execute(
            "SELECT id_editora FROM editoras WHERE nome_editora = ?", (editora,)
        ).fetchone()
        if editora_resultado is None:
            conexao.execute("INSERT INTO editoras (nome_editora) VALUES (?)", (editora,))
            conexao.commit()
            editora_resultado = conexao.execute(
                "SELECT id_editora FROM editoras WHERE nome_editora = ?", (editora,)
            ).fetchone()
        editora_id = editora_resultado['id_editora']

        conexao.execute("""
            INSERT INTO livros (titulo, autor_id, isbn, ano_publicacao, genero_id, editora_id, quantidade_disponivel, resumo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (titulo, autor_id, isbn, ano_publicacao, genero_id, editora_id, quantidade_disponivel, resumo))
        conexao.commit()
        conexao.close()
        return redirect(url_for("livros"))

    conexao.close()
    return render_template('criar_livro.html', livro=None)

@app.route('/editar_livro/<id>', methods=["GET", "POST"])
@login_required
def editar_livro(id):
    conexao = obter_conexao()

    if request.method == "POST":
        titulo = request.form['titulo']
        autor = request.form['autor']
        isbn = request.form['isbn']
        ano_publicacao = request.form['ano_publicacao']
        genero = request.form['genero']
        editora = request.form['editora']
        quantidade_disponivel = request.form['quantidade_disponivel']
        resumo = request.form['resumo']

        # AUTOR
        autor_resultado = conexao.execute("SELECT id_autor FROM autores WHERE nome_autor = ?", (autor,)).fetchone()

        if autor_resultado is None and 'nacionalidade' not in request.form:
            conexao.close()
            return render_template('editar_livro.html', livro={'id_livro': id, 'titulo': titulo, 'isbn': isbn,
                'ano_publicacao': ano_publicacao, 'genero': genero, 'editora': editora,
                'quantidade_disponivel': quantidade_disponivel, 'resumo': resumo, 'autor': autor},
                autor_nao_existe=True, autor_nome=autor)

        if autor_resultado is None:
            conexao.execute(
                "INSERT INTO autores (nome_autor, nacionalidade, data_nascimento, biografia) VALUES (?, ?, ?, ?)",
                (autor, request.form['nacionalidade'], request.form['data_nascimento'], request.form['biografia'])
            )
            conexao.commit()
            autor_resultado = conexao.execute("SELECT id_autor FROM autores WHERE nome_autor = ?", (autor,)).fetchone()

        autor_id = autor_resultado['id_autor']

        # GÊNERO
        genero_resultado = conexao.execute("SELECT id_genero FROM generos WHERE nome_genero = ?", (genero,)).fetchone()
        if genero_resultado is None:
            conexao.execute("INSERT INTO generos (nome_genero) VALUES (?)", (genero,))
            conexao.commit()
            genero_resultado = conexao.execute("SELECT id_genero FROM generos WHERE nome_genero = ?", (genero,)).fetchone()
        genero_id = genero_resultado['id_genero']

        # EDITORA
        editora_resultado = conexao.execute("SELECT id_editora FROM editoras WHERE nome_editora = ?", (editora,)).fetchone()
        if editora_resultado is None:
            conexao.execute("INSERT INTO editoras (nome_editora) VALUES (?)", (editora,))
            conexao.commit()
            editora_resultado = conexao.execute("SELECT id_editora FROM editoras WHERE nome_editora = ?", (editora,)).fetchone()
        editora_id = editora_resultado['id_editora']

        conexao.execute("""
            UPDATE livros 
            SET titulo=?, autor_id=?, isbn=?, ano_publicacao=?, genero_id=?, editora_id=?, quantidade_disponivel=?, resumo=?
            WHERE id_livro=?
        """, (titulo, autor_id, isbn, ano_publicacao, genero_id, editora_id, quantidade_disponivel, resumo, id))
        conexao.commit()
        conexao.close()
        return redirect(url_for("livros"))

    livro = conexao.execute("SELECT * FROM livros WHERE id_livro = ?", (id,)).fetchone()
    conexao.close()
    if not livro:
        flash("Livro não encontrado.", "error")
        return redirect(url_for("livros"))
    return render_template("editar_livro.html", livro=livro)
             
@app.route('/remover_livro', methods=['POST'])
@login_required
def remover_livro():
    id_livro = request.form['id']
    conexao = obter_conexao()
    conexao.execute('DELETE FROM livros WHERE id_livro = ?', (id_livro,))
    conexao.commit()
    conexao.close()
    return redirect(url_for('livros'))

@app.route('/emprestimo', methods=["GET", "POST"])
@login_required
def emprestimo():
    conexao = obter_conexao()
    usuarios = conexao.execute('SELECT id_usuario, nome_usuario FROM usuarios').fetchall()
    livros = conexao.execute('SELECT id_livro, titulo FROM livros WHERE quantidade_disponivel > 0').fetchall()

    if request.method == "POST":
        usuario = request.form['usuario_id']
        livro = request.form['livro_id']
        data_emprestimo = datetime.date.today()
        data_devolucao_prevista = data_emprestimo + relativedelta(months=1)
        data_devolucao_real = None
        status_emprestimo = 'pendente'

        conexao.execute('''
            INSERT INTO emprestimos (usuario_id, livro_id, data_emprestimo, data_devolucao_prevista, data_devolucao_real, status_emprestimo)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (usuario, livro, data_emprestimo, data_devolucao_prevista, data_devolucao_real, status_emprestimo))

        conexao.execute('''
            UPDATE livros
            SET quantidade_disponivel = quantidade_disponivel - 1
            WHERE id_livro = ?
        ''', (livro,))

        conexao.commit()
        conexao.close()
        return redirect(url_for('emprestimo'))

    conexao.close()
    return render_template('emprestimo.html', usuarios=usuarios, livros=livros)

@app.route('/ver_emprestimos')
@login_required
def ver_emprestimos():
    conexao = obter_conexao()

    consulta = '''
        SELECT 
            emprestimos.id_emprestimo,
            usuarios.nome_usuario,
            livros.titulo,
            emprestimos.data_emprestimo,
            emprestimos.data_devolucao_prevista,
            emprestimos.data_devolucao_real,
            emprestimos.status_emprestimo
        FROM emprestimos
        JOIN usuarios ON emprestimos.usuario_id = usuarios.id_usuario
        JOIN livros ON emprestimos.livro_id = livros.id_livro
        ORDER BY emprestimos.data_emprestimo DESC
    '''

    lista_emprestimos = conexao.execute(consulta).fetchall()
    conexao.close()
    return render_template('ver_emprestimos.html', lista_emprestimos=lista_emprestimos)

if __name__ == '__main__':
    app.run(debug=True)