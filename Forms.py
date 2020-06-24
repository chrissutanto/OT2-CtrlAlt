from flask_wtf import FlaskForm
from wtforms import StringField, FormField, FieldList
from wtforms.validators import DataRequired

class fieldForm(FlaskForm):
    value = StringField('')

class modifyForm(FlaskForm):
    fields = FieldList(FormField(fieldForm))