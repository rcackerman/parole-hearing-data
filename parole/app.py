import os

from flask import Flask
from flask import redirect, url_for

from parole import models


app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS'))


if __name__ == '__main__':
    models.connect_db(app.config['DATABASE_URL'])
    app.run()
