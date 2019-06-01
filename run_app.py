import os
from flask import Flask, render_template
from greet_bot import main


def create_app():
    """Function to create and return an application"""
    app = Flask(__name__)

    @app.route("/")
    def run_bot():
        main()

    return app

# running application on heroku
port = int(os.environ.get("PORT", 5000))
create_app().run(debug=True, host='0.0.0.0', port=port)

##local mashine
##if __name__ == "__main__":
##    create_app().run()
