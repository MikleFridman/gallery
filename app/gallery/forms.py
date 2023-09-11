from flask_wtf import FlaskForm
from wtforms import (StringField, TelField, DateField, SubmitField, TextAreaField,
                     FileField, IntegerField, SelectField, BooleanField)
from wtforms.validators import Optional, DataRequired, Length, InputRequired


class UploadForm(FlaskForm):
    file = FileField('')
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})


class FeatureForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    type_id = SelectField('Artwork type', choices=[], validators=[InputRequired()])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})


class FeaturesValueForm(FlaskForm):
    value = StringField('Value')
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})


class StatusForm(FlaskForm):
    name = StringField('Name')
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})


class ArtworkTypeForm(FlaskForm):
    name = StringField('Name')
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})


class TagForm(FlaskForm):
    name = StringField('Name')
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})


class ArtworkForm(FlaskForm):
    type_id = SelectField('Type', choices=[], validators=[InputRequired()])
    name = StringField('Name', validators=[DataRequired()])
    author = StringField('Author')
    year = StringField('Year')
    buy_price = IntegerField('Buy price')
    info = TextAreaField('Info', validators=[Length(max=200)])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})


class ClientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone = TelField('Phone', validators=[DataRequired()])
    birthday = DateField('Birthday', validators=[Optional()])
    info = TextAreaField('Info', validators=[Length(max=200)])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})


class AttachmentForm(FlaskForm):
    main_image = BooleanField('Main image')
    info = TextAreaField('Info', validators=[Length(max=200)])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})


class SelectTemplateForm(FlaskForm):
    template = SelectField('Template', choices=[('', '-Select-'), (0, 'Template 1'), (1, 'Template 2')],
                           validators=[InputRequired()])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})


class OfferForm(FlaskForm):
    artwork_id = SelectField('Artwork', choices=[], validators=[InputRequired()])
    client_id = SelectField('Client', choices=[], validators=[InputRequired()])
    price = IntegerField('Buy price')
    status_id = SelectField('Status', choices=[], validators=[InputRequired()])
    info = TextAreaField('Info', validators=[Length(max=200)])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})


class SearchForm(FlaskForm):
    feature_id = SelectField('Feature', choices=[], validators=[InputRequired()])
    value = StringField('Value', validators=[DataRequired()])
    submit = SubmitField('Search')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})
