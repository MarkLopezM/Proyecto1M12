import sqlite3, os
from flask import Flask, render_template, g, request, flash, request, redirect, url_for
from datetime import datetime
from werkzeug.utils import secure_filename

#VARIABLES


app = Flask(__name__)

UPLOAD_FOLDER = './static/img/uploads'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

basedir = os.path.abspath(os.path.dirname(__file__)) 


DATABASE='database.db'


#FUNCIONES

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_db_connection():
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    return con

def get_db_select(table):
    with get_db_connection() as con:
        res = con.execute(f"SELECT * from {table}")
        items = res.fetchall()
        return items
#ROUTES

@app.route("/")
def hello_world():
    return render_template('hello.html')

@app.route('/products/list')
def item_list():
    items = get_db_select("products")
    return render_template('products/list.html', items=items)

@app.route('/products/create', methods=["GET", "POST"])
def item_create():
    if request.method == 'GET':
        cat = get_db_select("categories")
        return render_template('products/create-edit.html', cat = cat)
    elif request.method == 'POST':
        data = request.form
        file = request.files["foto"]
        id = '1'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        with get_db_connection() as con:
            cursor = con.cursor()
            sql = 'INSERT INTO products (title, description,photo,price,category_id,seller_id,created,updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
            data=(data["nombre"], data["descripcion"], file.filename, data["precio"], data["categoria"], id, now(),now())
            cursor.execute(sql,data)
            con.commit()
    return redirect(url_for('item_list'))

@app.route('/products/read/<int:id>', methods=["GET"])
def item_read(id):
    if request.method == 'GET':
        with get_db_connection() as con:    
            res = con.execute(f"SELECT * from  products where id =?",(id,))
            info =  res.fetchone()
        return render_template('products/read.html', info=info)

@app.route('/products/edit/<int:id>', methods=["GET", "POST"])
def item_edit(id):
    if request.method == 'GET':
        items = get_db_select('categories')
        with get_db_connection() as con:    
            res = con.execute(f"SELECT * from  products where id =?",(id,))
            info =  res.fetchone()
        return render_template('products/create-edit.html', cat = items, info = info)
    elif request.method == 'POST':
        data = request.form
        id = '1'
        if request.files["foto"]:
            file = request.files["foto"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                img = file.filename
        else:
                img = request.form["photo"]
        with get_db_connection() as con:
            cursor = con.cursor()
            sql = f'UPDATE products SET title = ?, description = ?, photo = ?, price = ?, category_id = ?, seller_id = ?, updated = ? WHERE id = {id}'
            data = (data["nombre"], data["descripcion"], img, data["precio"], data["categoria"],id, now())
            cursor.execute(sql,data)
            con.commit()
    return redirect(url_for('item_list'))

@app.route('/products/delete/<int:id>', methods=["GET", "POST"])
def item_delete(id):
    if request.method == 'GET':
        with get_db_connection() as con:    
            res = con.execute(f"SELECT * from  products where id =?",(id,))
            info =  res.fetchone()
            return render_template('products/delete.html',info = info)
    elif request.method == 'POST':
        with get_db_connection() as con:
            # cursor = con.cursor()
            con.execute(f'DELETE FROM products WHERE id = {id}')
            # data = (id)
            # cursor.execute(sql,data)
            con.commit()
        return redirect(url_for('item_list'))

