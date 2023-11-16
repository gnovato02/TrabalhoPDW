from flask import Flask, request, jsonify, make_response
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
            resposta = make_response("O cookie foi criado")
            resposta.set_cookie("token", value=token, httponly=True)
    
            return resposta
        else:
            return jsonify({'message': 'Credenciais inválidas'})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/users/<int:user_id>', methods=['PUT'])
def alter_users(user_id):
    try:
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
        usuario = cursor.fetchone()
        
        if usuario is None:
            return jsonify({"message": "Usuário não encontrado"})
        
        data_user = request.get_json()        
        nome = data_user.get("nome")
        email = data_user.get("email")
        tipo_usuario = data_user.get("tipo_usuario")
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
        return jsonify({"error": str(e)})
        
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
    
@app.route('/items', methods=['POST'])
def create_itens():
    try:
        createItem = request.json
        queryItens = "INSERT INTO itens (titulo, autor, preco, itemStatus, idVendedor) VALUES (%s, %s, %s, TRUE, %s)"
        cursor.execute(queryItens, (createItem['titulo'], createItem['autor'], createItem['preco'], createItem['idVendedor']))
        conexao.commit()
        return jsonify({"message": "Registro criado com sucesso"})

    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/items', methods=['GET'])
def get_items():
    try:
        cursor.execute("SELECT * FROM itens WHERE itemStatus = 1")
        registros = cursor.fetchall()
        for itens in registros:
            itens_data = [{"Titulo": itens[1], "Autor": itens[2], "preço": itens[3], "Vendedor": itens[5] } for itens in registros]
        return jsonify(itens_data)
    
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/items/<int:item_id>', methods=['PUT'])
def alter_itens(item_id):
    try:
        cursor.execute("SELECT * FROM itens WHERE itemId = %s", (item_id,))
        item = cursor.fetchone()
        
        if item is None:
            return jsonify({"message": "Item não encontrado"})
        
        data_user = request.get_json()        
        titulo = data_user.get("titulo")
        autor = data_user.get("autor")
        preco = data_user.get("preco")
        
        cursor.execute("UPDATE itens SET titulo = %s, autor = %s, preco = %s WHERE itemId = %s",
                       (titulo, autor, preco, item_id))

        conexao.commit()

        return jsonify({"message": "Item atualizado com sucesso"})
        
    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/items/nome/<string>', methods=['GET'])
def get_items_by_name(string):
    try:
        cursor.execute("SELECT * FROM itens WHERE titulo = %s", (string,))
        registros = cursor.fetchall()
        itens_data = [{"Titulo": item[1], "Autor": item[2], "preço": item[3], "Vendedor": item[5]} for item in registros]
        return jsonify(itens_data)
    
    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/items/id/<int:item_id>', methods=['GET'])
def get_items_by_id(item_id):
    try:
        cursor.execute("SELECT * FROM itens WHERE itemId = %s", (item_id,))
        registros = cursor.fetchone()
        itens_data = [{"Titulo": registros[1], "Autor": registros[2], "preço": registros[3], "Vendedor": registros[5] }]
        return jsonify(itens_data)
    
    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/categories', methods=['POST'])
def create_categories():
    try:
        createData = request.json
        queryCat = "INSERT INTO categorias (nome, statusCategoria) VALUES (%s, TRUE)"
        cursor.execute(queryCat, (createData['nome'],))
        conexao.commit()
        return jsonify({"message": "Registro criado com sucesso"})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/categories', methods=['GET'])
def get_categories():
    try:
        cursor.execute("SELECT * FROM categorias WHERE statusCategoria = 1")
        registros = cursor.fetchall()
        categorie_data = [{"Categoria": categorie[1]} for categorie in registros]
        return jsonify(categorie_data)
    
    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/categories/addItem', methods=['POST'])
def add_item():
    try:
        createData = request.json
        queryCat = "INSERT INTO itens_e_categorias (item_id, item_cat) VALUES (%s, %s)"
        cursor.execute(queryCat, (createData['item_id'],createData['item_cat']))
        conexao.commit()
        return jsonify({"message": "Registro criado com sucesso"})

    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/categories/<string>', methods=['GET'])
def get_categories_and_itens(string):
    try:
        cursor.execute("SELECT itens.titulo, categorias.nome AS categoria_nome, itens_e_categorias.* FROM itens JOIN itens_e_categorias ON itens.itemId = itens_e_categorias.item_id JOIN categorias ON itens_e_categorias.item_cat = categorias.idCategoria WHERE categorias.nome =  %s", (string,))
        registros = cursor.fetchall()
        data = [{"Categoria": item[1], "Titulo": item[0]} for item in registros]
        return jsonify(data)
    
    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/items/<int:item_id>', methods=['DELETE'])
def soft_delete_item(item_id):
    try:
            cursor.execute("SELECT * FROM itens WHERE itemId = %s", (item_id,))
            data = cursor.fetchone()

            if data is None:
                return jsonify({"message": "Item não encontrado"})

            cursor.execute("UPDATE itens SET itemStatus = 0 WHERE itemId = %s", (item_id,))
            conexao.commit()

            return jsonify({"message": "Item desativado com sucesso"})
    
    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/categories/<int:cat_id>', methods=['DELETE'])
def soft_delete_categoria(cat_id):
    try:
            cursor.execute("SELECT * FROM categorias WHERE idCategoria = %s", (cat_id,))
            data = cursor.fetchone()

            if data is None:
                return jsonify({"message": "Categoria não encontrada"})

            cursor.execute("UPDATE categorias SET statusCategoria = 0 WHERE idCategoria = %s", (cat_id,))
            conexao.commit()

            return jsonify({"message": "Categoria desativada com sucesso"})
    
    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/transactions', methods=['POST'])
def add_transaction():
    try:
        data = request.json
        query = "INSERT INTO transactions (idItem, idComprador) VALUES (%s, %s)"
        cursor.execute(query, (data['idItem'],data['idComprador']))
        conexao.commit()
        return jsonify({"message": "Registro criado com sucesso"})

    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/transactions/<string>', methods=['GET'])
def get_transactions(string):
    try:
        cursor.execute("SELECT transactions.idTrans, usuarios.nome, itens.titulo FROM transactions JOIN usuarios ON transactions.idComprador = usuarios.id JOIN itens ON transactions.idItem = itens.itemId WHERE usuarios.id =  %s", (string,))
        registros = cursor.fetchall()
        data = [{"Usuario": user[1], "Compra": user[2]} for user in registros]
        return jsonify(data)
    
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run(host='localhost', port=5000,debug=True)

app.run()
