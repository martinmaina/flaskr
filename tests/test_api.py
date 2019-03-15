import os
import tempfile
import pytest

from FlaskIt import app

@pytest.fixture 
def client():
    db_df, app.app.config['DATABASE'] = tempfile.mkstemp()
    app.app.config['TESTING'] = True
    client = app.app.test_client()

    with app.app.app_context():
        app.init_db()

    yield client

    os.close(db_df)
    os.unlink(app.app.config['DATABASE'])


def test_empyt_db(client):
    '''Start with an empty database'''
    resp =client.get('/')
    assert b'No Posts' in resp.data

def login(client, username, password):
    return client.post('/login', data=dict(username=username, password=password), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)


def test_login_logout(client):
    '''Login and logout works perfectly well'''

    resp = login(client, app.app.config['USERNAME'], app.app.config['PASSWORD'])
    assert b'You were logged in' in resp.data

    resp = logout(client)
    assert b'You were logged out' in resp.data

    resp = login(client, app.app.config['USERNAME'] + 'x', app.app.config['PASSWORD'])
    assert b'Invalid username' in resp.data

    resp = login(client, app.app.config['USERNAME'], app.app.config['PASSWORD'] + 'x')
    assert b'Invalid password' in resp.data

def test_messages(client):
    '''Test that messages work'''
    login(client, app.app.config['USERNAME'], app.app.config['PASSWORD'])
    resp = client.post('/add', data=dict(
        title='<hello>',
        text='<b>HTML</b> allowed here'
    ), follow_redirects=True)
    assert b'No posts here' not in resp.data
    assert b'&lt;hello&gt;' in resp.data
    assert b'<b>HTML</b> allowed here' in resp.data


