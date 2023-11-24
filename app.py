from flask import Flask
from views import views
from waitress import serve

app = Flask(__name__)
app.register_blueprint(views, url_prefix="/")
app.config['TEMPLATES_AUTO_RELOAD'] = True

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=3000, threads=4)
