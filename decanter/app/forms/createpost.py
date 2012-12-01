from flask.ext.wtf import (Form,
                           TextField,
                           TextAreaField,
                           BooleanField,
                           Required)

class CreatePostForm(Form):
    title = TextField(label='Post Title',
                      validators=[Required()])
    slug = TextField(label='Post Slug',
                     validators=[Required()])
    content = TextAreaField(label='Post Content',
                            validators=[Required()])
