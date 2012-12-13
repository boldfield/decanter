from flask.ext.wtf import Form, TextField, PasswordField, BooleanField, Required

class LoginForm(Form):
    username = TextField(label='User Name or Email Address',
                         validators=[Required()],
                         description='Username or Email Address.')
                         #default='Username or Email Address.')
    password = PasswordField('Password', validators=[Required()],
                             description='Your password.')

    remember = BooleanField('Remember Me', validators=[],
                             default=False)

class RegistrationForm(Form):
    username = TextField(label='User Name',
                         validators=[Required()],
                         description='Username or Email Address.')
    password_1 = PasswordField('Password', validators=[Required()],
                             description='Your password.')
    password_2 = PasswordField('Reenter Password', validators=[Required()],
                               description='Your password.')
    email = TextField(label='Email Address',
                      validators=[],
                      description='Email Address (optional).')
