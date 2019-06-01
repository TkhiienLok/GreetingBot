import os
from flask import Flask, render_template


def create_app(data=default_data):
    """Function to create and return an application"""
    app = Flask(__name__)
    app.config['data'] = data

    return app

# running application on heroku
port = int(os.environ.get("PORT", 5000))
create_app().run(debug=True, host='0.0.0.0', port=port)
