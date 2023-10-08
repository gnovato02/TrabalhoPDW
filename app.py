from flask import Flask, request, jsonify
import mysql.connector
import bcrypt
import jwt
from datetime import datetime, timedelta

conexao = mysql.connector.connect(host='localhost',user='root',password='SEBO',database='sebo',)
cursor = conexao.cursor()

app = Flask(__name__)
app.config['chaveSenha'] = 'SenhaInquebravel'

@app.route('/teste')
def helloWorld():
    return 'Hello World!'

@app.route('/users/signup',methods=['POST'])
def create_user():
    try:
        createuser = request.get_json()
        query = "INSERT INTO usuarios (nome, email, senha, status_usuario, tipo_usuario) VALUES (%s, %s, %s, %s, %s)"
        newSenha = bcrypt.hashpw(createuser['senha'].encode('utf-8'), bcrypt.gensalt(10))
        cursor.execute(query, (createuser['nome'],createuser['email'],newSenha,createuser['status_usuario'],createuser['tipo_usuario']))
        conexao.commit()
        return jsonify({"message": "Registro criado com sucesso"})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/users/getusers', methods=['GET'])
def return_users():
    try:
        cursor.execute("SELECT * FROM usuarios WHERE status_usuario = 1")
        registros = cursor.fetchall()
        for usuario in registros:
            users_data = [{"Id": usuario[0], "Username": usuario[1], "Email": usuario[2], "Tipo de usuario": usuario[5] } for usuario in registros]
        return jsonify(users_data)
    
    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/users/login', methods=['POST'])
def login_users():
    try:
        loginData = request.get_json()
        email = loginData.get("email")
        senha = loginData.get("senha")

        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(senha.encode('utf-8'), user[3].encode('utf-8')):
            expiration = datetime.utcnow() + timedelta(hours=4)
            payload = {'email': email, 'exp': expiration}
            token = jwt.encode(payload, app.config['chaveSenha'], algorithm='HS256')
    
            return jsonify({'token': token})
        else:
            return jsonify({'message': 'Credenciais inválidas'})

    except Exception as e:
        return jsonify({"error": str(e)})

'''@app.route('/users/<int:user_id>', methods=['PUT'])
def alter_users(user_id):
    try:
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
        usuario = cursor.fetchone()
        
        if usuario is None:
            return jsonify({"message": "Usuário não encontrado"})
        
        data_user = request.get_json()        
        nome = data_user.get("nome", usuario["nome"])
        email = data_user.get("email", usuario["email"])
        tipo_usuario = data_user.get("tipo_usuario", usuario["tipo_usuario"])
        senha = data_user.get("senha")
        if senha:
            hashed_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        else:
            hashed_senha = usuario["senha"]
        
        cursor.execute("UPDATE usuarios SET nome = %s, email = %s, senha = %s, tipo_usuario = %s WHERE id = %s",
                       (nome, email, hashed_senha, tipo_usuario, user_id))

        conexao.commit()

        return jsonify({"message": "Usuário atualizado com sucesso"})
        
    except Exception as e:
        return jsonify({"error": str(e)})'''
        
@app.route('/users/<int:user_id>', methods=['DELETE'])
def soft_delete_usuario(user_id):
    try:
            cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
            usuario = cursor.fetchone()

            if usuario is None:
                return jsonify({"message": "Usuário não encontrado"})

            cursor.execute("UPDATE usuarios SET status_usuario = 0 WHERE id = %s", (user_id,))
            conexao.commit()

            return jsonify({"message": "Usuário desativado com sucesso"})
    
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run(port=5000,host='localhost',debug=True)

app.run()