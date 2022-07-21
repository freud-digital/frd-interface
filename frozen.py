from flask_frozen import Freezer
from run import app

app.config['FREEZER_RELATIVE_URLS'] = True
app.config.from_pyfile('utils.py')
freezer = Freezer(app)

if __name__ == '__main__':
    freezer.freeze()
