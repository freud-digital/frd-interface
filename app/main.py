
from flask import Flask, render_template

from app.config import FRD_DATA, WERK_PATH
from app.utils import get_frd_data, create_html_template, copy_xml, collate_tei

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data', methods=['POST'])
def get_werke():
    werke = get_frd_data(FRD_DATA, 'tmp', WERK_PATH, save=False)
    html = create_html_template(werke)
    return html


@app.route('/select/<string:selected>', methods=['POST'])
def get_selected(selected):
    sel = selected.split(',')
    copy = copy_xml(save_path='tmp', path_dir=WERK_PATH, select=sel)
    # remove_dir(save_path='tmp')
    return copy


@app.route('/collate/<string:selected>', methods=['POST'])
def get_collated(selected):
    sel = selected.split(',')
    collated = collate_tei(save_path='tmp', path_dir=WERK_PATH, select=sel)
    return collated


# if __name__ == "__main__":
#     app.run()
