""" forms for the mupy web admin """
from wtforms import Form, TextField, TextAreaField, validators

class AddForm(Form):
    slug = TextField('New Page URL', [validators.Length(min=15, max=45)])
    title = TextField('Page Title', [validators.Length(min=5, max=67)])
    youtube = TextField('YouTube URL', [validators.Required()])


class EditForm(Form):
    slug = TextField('New Page URL', [validators.Length(min=15, max=45)])
    title = TextField('Page Title', [validators.Length(min=5, max=67)])
    body = TextAreaField('Page Body', [validators.Required()])