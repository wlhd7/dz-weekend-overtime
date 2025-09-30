from flask import Flask
import os
from .work import init_app
from .db import init_db

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'weekend-overtime.sqlite'),
        )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    init_app(app)

    init_db(app)

    app.add_url_rule('/', endpoint='weekend_overtime')

    return app
