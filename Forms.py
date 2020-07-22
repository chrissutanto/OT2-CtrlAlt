from flask_wtf import FlaskForm
from wtforms import StringField, FormField, FieldList, SelectField
from wtforms.validators import DataRequired

class fieldForm(FlaskForm):
    value = StringField('')

class LabwareForm(FlaskForm):
    choices = [('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', '10 Tube Rack with Falcon 4x50mL, 6x15mL Conical'),
                ('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '24 Tube Rack with Eppendorf 1.5mL Safe-Lock Snapcap'),
                ('opentrons_15_tuberack_falcon_15ml_conical', '15 Tube Rack with Falcon 15mL Conical'),
                ('opentrons_6_tuberack_falcon_50ml_conical', '6 Tube Rack with Falcon 50mL conical')]
    source = SelectField(u'Source', choices=choices)
    destination = SelectField(u'Destination', choices=choices)

class modifyForm(FlaskForm):
    fields = FieldList(FormField(fieldForm))