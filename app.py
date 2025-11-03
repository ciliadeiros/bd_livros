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
    return User.get(user_id)

app = Flask(__name__)
app.secret_key = "SENHASUPERSECRETAUAAAAU"

@login_required
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
            User.add_usuario(email=email, senha=senha, numero_telefone=numero_telefone, data_inscricao=data_inscricao)

            # login do usuário
            user = User(email=email, senha=senha, numero_telefone=numero_telefone, data_inscricao=data_inscricao)
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

'''
@app.route('/logout', methods=["POST", "GET"])
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/criar_livros', methods=["GET","POST"])
def criar_livros():
    if request.method == 'POST':
        nome = request.form['nome']
'''


if __name__ == '__main__':
    app.run(debug=True)