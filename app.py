from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from database import obter_conexao
from modelos import User
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import sqlite3

login_manager = LoginManager()
login_manager.login_view = 'login'
app = Flask(__name__)
app.secret_key = 'ablublublu'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

app = Flask(__name__)
app.secret_key = "SENHASUPERSECRETAUAAAAU"

# Formato: "mysql://USUARIO:SENHA@HOST:PORTA/NOME_DO_BANCO"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:SUASENHA@localhost:3306/db_trabalho3B'

db = SQLAlchemy(app)

@login_required
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro')
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email'] 
        senha = request.form['senha']

        conexao = obter_conexao()
        sql = "SELECT * FROM usuarios WHERE email = ?"
        resultado = conexao.execute(sql, (email,) ).fetchone()

        if not resultado:
            sql = "INSERT INTO usuarios() VALUES(?,?,?,?)"
            conexao.execute(sql, (email, nome))
            conexao.commit()
            conexao.close()

            # login do usuário
            user = User(email=email, nome=nome, senha=senha)
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

        login_user(usuario)
        flash('Login feito com sucesso!', category='success')
        return redirect(url_for('livros'))
    else:
        flash('Usuário ou senha incorretos. Tente novamente :/', category='error')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout', methods=["POST", "GET"])
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/criar_livros', methods=["GET","POST"])
def criar_livros():
    if request.method == 'POST':
        nome = request.form['nome']
