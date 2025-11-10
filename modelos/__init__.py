from flask_login import UserMixin
from database import obter_conexao

class User(UserMixin):
    def __init__(self, email, nome, senha, numero_telefone, data_inscricao):
        self.id = email  # Flask-Login usa "id" como identificador (nesse caso, será o e-mail)
        self.email = email
        self.nome = nome
        self.senha = senha
        self.numero_telefone = numero_telefone
        self.data_inscricao = data_inscricao


    # procura um usuário no banco pelo e-mail, que é o ID
    @classmethod
    def selecionar_usuario(cls, email):
        conexao = obter_conexao()
        sql = "SELECT * FROM usuarios WHERE email = ?"
        resultado = conexao.execute(sql, (email,)).fetchone()

        if resultado:
            return User(
                email=resultado['email'],
                nome=resultado['nome_usuario'],
                senha=resultado['senha_usuario'],
                numero_telefone=resultado['numero_telefone'],
                data_inscricao=resultado['data_inscricao']
                )
        return None

    @classmethod
    def achar_email(cls, email):
        conexao = obter_conexao()
        sql = "SELECT * FROM usuarios WHERE email = ?"
        resultado = conexao.execute(sql, (email,)).fetchone()

        if resultado:
            return User(
                email=resultado['email'],
                nome=resultado['nome_usuario'],
                senha=resultado['senha_usuario'],
                numero_telefone=resultado['numero_telefone'],
                data_inscricao=resultado['data_inscricao']
            )
        return None

    # salva o usuário no banco de dados
    def add_usuario(self):
        conexao = obter_conexao()
        sql = """
            INSERT INTO usuarios (senha_usuario, nome_usuario, email, numero_telefone, data_inscricao)
            VALUES (?, ?, ?, ?, ?)
        """
        conexao.execute(sql, (self.senha, self.nome, self.email, self.numero_telefone, self.data_inscricao))
        conexao.commit()

    # apaga o usuário do banco de dados
    @classmethod
    def deletar_usuario(cls, email):
        conexao = obter_conexao()
        sql = "DELETE FROM usuarios WHERE email = ?"
        conexao.execute(sql, (email,))
        conexao.commit()
