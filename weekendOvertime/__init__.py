from flask import Flask
import os
from .db import init_db
from .routes import init_route, views

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

    init_db(app)

    init_route(app, views)

    app.add_url_rule('/', endpoint='weekend_overtime')

    return app
