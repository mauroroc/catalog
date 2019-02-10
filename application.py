from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categoria, Item
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Udacity"

engine = create_engine('sqlite:///catalogo.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Codigo de autenticacao do Google
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps("User already connected."), 200)
        print("Current user is already connected.")
        print("Email: " + login_session['email'])
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['email'] = data['email']

    return login_session['email']


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['email']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        print(response)
    else:
        response = make_response(json.dumps('Failed to revoke token', 400))
        response.headers['Content-Type'] = 'application/json'
        print(response)
    return redirect(url_for('showCategorias'))


# Lista todas as categorias / pagina inicial
@app.route('/')
@app.route('/catalog/')
def showCategorias():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    if 'email' not in login_session:
        login = {'nome': False}
    else:
        login = {'nome': login_session['email']}
    categorias = session.query(Categoria).all()
    itens = session.query(Item).order_by(Item.id.desc()).all()
    return render_template('index.html', login=login,
                           categorias=categorias,
                           itens=itens,
                           STATE=state)


# Adicionar uma nova categoria
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCategoria():
    if 'email' not in login_session:
        return redirect('/catalog')
    else:
        login = {'nome': login_session['email']}
    if request.method == 'POST':
        newCategoria = Categoria(nome=request.form['nome'],
                                 user=login_session['email'])
        session.add(newCategoria)
        session.commit()
        return redirect(url_for('showCategorias'))
    else:
        return render_template('addCategoria.html', login=login)


# Editar uma categoria
@app.route('/catalog/<int:categoria_id>/edit/', methods=['GET', 'POST'])
def editCategoria(categoria_id):
    if 'email' not in login_session:
        return redirect('/catalog')
    else:
        login = {'nome': login_session['email']}
    editedCategoria = session.query(
        Categoria).filter_by(id=categoria_id).one()
    if request.method == 'POST':
        if request.form['nome']:
            editedCategoria.nome = request.form['nome']
            return redirect(url_for('showCategorias'))
    else:
        return render_template('editCategoria.html', login=login,
                               categoria=editedCategoria)


# Deletar uma categoria
@app.route('/catalog/<int:categoria_id>/delete/', methods=['GET', 'POST'])
def deleteCategoria(categoria_id):
    if 'email' not in login_session:
        return redirect('/catalog')
    else:
        login = {'nome': login_session['email']}
    categoriaToDelete = session.query(
        Categoria).filter_by(id=categoria_id).one()
    if request.method == 'POST':
        session.delete(categoriaToDelete)
        session.commit()
        return redirect(url_for('showCategorias'))
    else:
        return render_template('deleteCategoria.html', login=login,
                               categoria=categoriaToDelete)


# Apresenta os itens de uma categoria
@app.route('/catalog/<categoria_nome>/')
@app.route('/catalog/<categoria_nome>/itens/')
def showItens(categoria_nome):
    categoria = session.query(Categoria).filter_by(nome=categoria_nome).one()
    itens = session.query(Item).filter_by(
        categoria_id=categoria.id).all()
    categorias = session.query(Categoria).all()
    if 'email' not in login_session:
        login = {'nome': False}
    else:
        login = {'nome': login_session['email']}
    return render_template('itens.html', login=login,
                           itens=itens,
                           categorias=categorias,
                           categoria=categoria)


# Adicionar um novo item
@app.route('/catalog/itens/new/', methods=['GET', 'POST'])
def newItem():
    if 'email' not in login_session:
        return redirect('/catalog')
    else:
        login = {'nome': login_session['email']}
    categorias = session.query(Categoria).all()
    if request.method == 'POST':
        newItem = Item(nome=request.form['nome'],
                       descricao=request.form['descricao'],
                       categoria_id=request.form['sel_categoria'],
                       user=login_session['email'])
        session.add(newItem)
        session.commit()
        return render_template('itens.html',
                               login=login,
                               categorias=categorias,
                               categoria_id=request.form['sel_categoria'])
    else:
        return render_template('addItem.html', login=login,
                               categorias=categorias)


# Editar um item
@app.route('/catalog/itens/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(item_id):
    if 'email' not in login_session:
        return redirect('/catalog')
    else:
        login = {'nome': login_session['email']}
    editedItem = session.query(Item).filter_by(id=item_id).one()
    categoria_id = editedItem.categoria_id
    if request.method == 'POST':
        if request.form['nome']:
            editedItem.nome = request.form['nome']
        if request.form['descricao']:
            editedItem.descricao = request.form['descricao']
        if request.form['sel_categoria']:
            editedItem.categoria_id = request.form['sel_categoria']
        session.add(editedItem)
        session.commit()
        categoria = session.query(Categoria).filter_by(id=categoria_id).one()
        return redirect(url_for('showItens', categoria_nome=categoria.nome))
    else:
        categorias = session.query(Categoria).all()
        return render_template('edititem.html', login=login,
                               item=editedItem, categorias=categorias)


# Deletar um item
@app.route('/catalog/itens/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(item_id):
    if 'email' not in login_session:
        return redirect('/catalog')
    else:
        login = {'nome': login_session['email']}
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    categoria_id = itemToDelete.categoria_id
    categoria = session.query(Categoria).filter_by(id=categoria_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showItens', login=login,
                        categoria_nome=categoria.nome))
    else:
        return render_template('deleteItem.html', login=login,
                               item=itemToDelete, categoria=categoria)


# Apresenta um determinado item
@app.route('/catalog/<categoria_nome>/<item_nome>')
def showItem(item_nome, categoria_nome):
    item = session.query(Item).filter_by(nome=item_nome).one()
    if item:
        if 'email' not in login_session:
            login = {'nome': False}
        else:
            login = {'nome': login_session['email']}
        return render_template('item.html', login=login,
                               item=item,
                               categoria_nome=categoria_nome)
    else:
        return redirect(url_for('showCategorias'))


# Gera JSON de todas as categorias existentes
@app.route('/catalog/jsonCategorias')
def jsonCategorias():
    categorias = session.query(Categoria).all()
    return jsonify(Categoria=[i.serialize for i in categorias])


# Gera JSON de todos os itens existentes
@app.route('/catalog/jsonItens')
def jsonItens():
    itens = session.query(Item).all()
    return jsonify(Item=[i.serialize for i in itens])

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
