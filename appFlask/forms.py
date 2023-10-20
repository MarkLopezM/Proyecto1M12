from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField,TextAreaField,FloatField, HiddenField
from wtforms.validators import DataRequired, NumberRange, InputRequired
from flask_wtf.file import FileField, FileRequired

class ProductForm(FlaskForm):
    title = StringField('Título', validators = [DataRequired()])
    description = TextAreaField('Descripción', validators = [DataRequired()])
    photo = FileField('Foto',validators = [FileRequired()])
    price = FloatField('Precio',validators = [DataRequired(), NumberRange(min=1)])
    category_id = SelectField('Categoria', validators = [InputRequired()])
    submit = SubmitField()

class DeleteProductForm(FlaskForm):
    submit = SubmitField()