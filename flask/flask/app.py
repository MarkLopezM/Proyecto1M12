import sqlite3, os
from flask import Flask, render_template, g, request, flash, request, redirect, url_for
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from os import remove

#VARIABLES


app = Flask(__name__)

UPLOAD_FOLDER = './static/img/uploads'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

basedir = os.path.abspath(os.path.dirname(__file__)) 

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + basedir + "/database.db"

app.config["SQLALCHEMY_ECHO"] = True

DATABASE='database.db'

db = SQLAlchemy()
db.init_app(app)

#FUNCIONES

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def now():
    return datetime.now()


#BASE DE DATOS

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    photo = db.Column(db.Text)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created = db.Column(db.DATETIME, default=now, nullable=False)
    updated = db.Column(db.DATETIME, default=now(), onupdate=now(), nullable=False)

    category = db.relationship('Category', backref='products')
    seller = db.relationship('User', backref='products')

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    slug = db.Column(db.Text, unique=True, nullable=False)
    
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created = db.Column(db.DATETIME, default=now(), nullable=False)
    updated = db.Column(db.DATETIME, default=now(), onupdate=now(), nullable=False)

#ROUTES

@app.route("/")
def hello_world():
    return render_template('hello.html')

@app.route('/products/list')
def item_list():
    items = db.session.query(Product)
    return render_template('products/list.html', items=items)

@app.route('/products/create', methods=["GET", "POST"])
def item_create():
    if request.method == 'GET':
        cat = db.session.query(Category)
        return render_template('products/create-edit.html', cat = cat)
    elif request.method == 'POST':
        data = request.form
        file = request.files["foto"]
        id = '1'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = Product()
            new.title = data["nombre"]
            new.description = data["descripcion"]
            new.photo = file.filename
            new.price = float(data["precio"])
            new.category_id = int(data["categoria"])
            new.seller_id = int(id)
            new.created = now()
            new.updated = now()
            db.session.add(new)
            db.session.commit()
        return redirect(url_for('item_list'))

@app.route('/products/read/<int:id>', methods=["GET"])
def item_read(id):
    if request.method == 'GET':
        info = db.session.query(Product).filter(Product.id == id).one()
        return render_template('products/read.html', info=info)

@app.route('/products/edit/<int:id>', methods=["GET", "POST"])
def item_edit(id):
    info = db.session.query(Product).filter(Product.id == id).one()
    if request.method == 'GET':
        cat = db.session.query(Category)
        return render_template('products/create-edit.html', cat = cat, info = info)
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
        info.title = data["nombre"]
        info.description = data["descripcion"]
        info.photo = img
        info.price = float(data["precio"])
        info.category_id = int(data["categoria"])
        info.seller_id = int(id)
        info.updated = now()
        db.session.add(info)
        db.session.commit()
        return redirect(url_for('item_list'))

@app.route('/products/delete/<int:id>', methods=["GET", "POST"])
def item_delete(id):
    info = db.session.query(Product).filter(Product.id == id).one()
    if request.method == 'GET':
        return render_template('products/delete.html',info = info)
    elif request.method == 'POST':
        db.session.delete(info)
        db.session.commit()
        data = request.form
        remove(os.path.join(app.config['UPLOAD_FOLDER'], data["foto"]))
        return redirect(url_for('item_list'))