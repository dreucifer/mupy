""" forms for the mupy web admin """
from wtforms import Form, SelectField, TextField, TextAreaField, validators


class AddForm(Form):
    template = SelectField('Template')
    title = TextField('Page Title', [validators.Length(min=5, max=67)])
    youtube = TextField('YouTube URL', [validators.Required()])


class EditForm(Form):
    slug = TextField('New Page URL', [validators.Length(min=15, max=45)])
    title = TextField('Page Title', [validators.Length(min=5, max=67)])
    body = TextAreaField('Page Body', [validators.Required()])
    keywords = TextField('Keywords')
    description = TextAreaField('Description')
