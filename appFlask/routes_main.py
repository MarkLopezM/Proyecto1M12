import os
from flask import Blueprint, Flask, render_template, g, request, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from os import remove
from datetime import datetime
from .models import Product, Category, User
from . import db_manager as db
from .forms import ProductForm, DeleteProductForm

#VARIABLES

UPLOAD_FOLDER = './appFlask/static/img/uploads'

main_bp = Blueprint(
    "main_bp", __name__, template_folder="templates", static_folder="static"
)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

#FUNCIONES

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def now():
    return datetime.now()

#ROUTES

@main_bp.route("/")
def hello_world():
    return render_template('hello.html')

@main_bp.route('/products/list')
def item_list():
    deleteForm = DeleteProductForm()
    items = db.session.query(Product)
    return render_template('products/list.html', items=items, deleteForm=deleteForm)

@main_bp.route('/products/create', methods=["GET", "POST"])
def item_create():
    cat = db.session.query(Category)
    form = ProductForm()
    form.category_id.choices = [(category.id, category.name) for category in cat]
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        price = form.price.data
        category_id = form.category_id.data
        photo = form.photo.data
        file = form.photo.data
        if photo and allowed_file(photo.filename):
            filename = secure_filename(file.filename)
            photo.save(os.path.join(UPLOAD_FOLDER, filename))
            new_product = Product(title=title, description=description, price=price, category_id=category_id, photo=filename)
            db.session.add(new_product)
            db.session.commit()
            return redirect(url_for('main_bp.item_list'))
    else: 
        return render_template('products/create-edit.html', form = form)

@main_bp.route('/products/read/<int:id>', methods=["GET"])
def item_read(id):
    if request.method == 'GET':
        info = db.session.query(Product).filter(Product.id == id).one()
        return render_template('products/read.html', info=info)

@main_bp.route('/products/edit/<int:id>', methods=["GET", "POST"])
def item_edit(id):
    cat = db.session.query(Category)
    info = db.session.query(Product).filter(Product.id == id).one()
    form = ProductForm(obj = info)
    form.category_id.choices=[(category.name) for category in cat]
        
    if request.method == 'GET' :
        return render_template('products/create-edit.html', info=info, form = form)
    elif request.method == 'POST' and form.validate_on_submit():
        new_product = db.session.query(Product).filter(Product.id == id).one()
        form.populate_obj(new_product)        
        file = form.photo.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            new_product.photo = filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        new_product.updated = datetime.utcnow()

        db.session.commit()

    return redirect(url_for('main_bp.item_list'))

@main_bp.route('/products/delete/<int:id>', methods=["GET", "POST"])
def item_delete(id):
    info = db.session.query(Product).filter(Product.id == id).one()
    form = DeleteProductForm(obj = info)
    if request.method == 'POST' and form.validate_on_submit():
        db.session.delete(info)
        db.session.commit()
        remove(os.path.join(UPLOAD_FOLDER, info.photo))
        return redirect(url_for('main_bp.item_list'))
    
    return redirect(url_for('main_bp.item_list'))