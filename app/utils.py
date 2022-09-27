import os
import glob
import shutil
import requests
import xml.etree.ElementTree as ET

from zipfile import ZipFile
from acdh_collatex_utils.acdh_collatex_utils import CxCollate, CxReader
from acdh_collatex_utils.post_process import (
    merge_tei_fragments,
    make_full_tei_doc,
    define_readings,
    make_positive_app,
    merge_html_fragments
)
from app.config import XPATH, CHUNK_SIZE


XSLT_FILE = os.path.join(
    os.path.dirname(__file__),
    "fixtures",
    "make_tei.xslt"
)

HTML = os.path.join(
    "index.html"
)


def get_frd_data(url, save_path, path_dir):
    if not os.path.exists(save_path):
        frd_data = requests.get(
            url,
            stream=True
        )
        filename = url.split('/')[-1]
        os.makedirs(save_path, exist_ok=True)
        with open(filename, 'wb') as output_file:
            output_file.write(frd_data.content)
        print('Downloading Completed')
        with ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall(save_path)
        os.remove(filename)
        print(f'{filename}: file removed')
    unziped_dir = glob.glob(os.path.join(save_path, '*'))
    werke = glob.glob(os.path.join(unziped_dir[0], path_dir, '*'))
    dct_man = {}
    for w in werke:
        manifestastions = glob.glob(os.path.join(w, '*.xml'))
        werk = w.split('/')[-1]
        dct_man[werk] = []
        for m in manifestastions:
            dct_man[werk].append(m.split('/')[-1])
    try:
        del dct_man['worklist.csv']
    except KeyError:
        print('worklist.csv not found')
    return dct_man


def create_html_template(input):
    all_works = '<div id="all_works">'
    for x in input:
        div = f'<div id="w__{x}">'
        w = f'<label>Werksignatur {x}:</label>'
        div += w
        select = f"""<select class="custom-select" id="s__{x}"
            onchange="get_select(this)">
            <option selected="selected">Manifestation auswählen</option>"""
        try:
            for w in input[x]:
                select += f'<option value="{w}">{w.split(".")[0]}</option>'
        except TypeError:
            print("error")
        select += '</select>'
        div += select
        div += '</div>'
        all_works += div
    all_works += '</div>'
    return all_works


def copy_xml(save_path, path_dir, select):
    el = select
    werk = el[1].replace('s__', '')
    manifest = el[0]
    # all_manifests = glob.glob(os.path.join(save_path, '*', path_dir, werk))
    # for x in all_manifests:
    #     with open(x, "r", encoding='utf8') as f:
    #         data = f.read()
    base_manifest = glob.glob(os.path.join(save_path, '*', path_dir, werk, manifest))
    print(base_manifest)
    tei = ET.parse(base_manifest[0])
    root = tei.getroot()
    tei = ET.tostring(root, encoding="utf-8")
    return tei


def copy_html():
    h = HTML
    html = ET.parse(h)
    os.remove(h)
    root = html.getroot()
    html = ET.tostring(root, encoding="utf-8")
    return html


def collate_tei(save_path, path_dir, select):
    el = select
    werk = el[1].replace('s__', '')
    manifest = el[0]
    all_manifests_pre = glob.glob(os.path.join(save_path, '*', path_dir, werk, '*.xml'))
    os.makedirs("tmp_to_collate", exist_ok=True)
    for x in all_manifests_pre:
        tei = CxReader(
            xml=x,
            custom_xsl=XSLT_FILE,
            char_limit=False,
            chunk_size=CHUNK_SIZE,
            to_compare_xpath=XPATH
        ).preprocess()
        new_save_path = os.path.join("tmp_to_collate", x.split('/')[-1])
        with open(new_save_path, 'wb') as f:
            f.write(tei)
        print(f"TEI updated ({new_save_path})")
    all_manifests = os.path.join(".", "tmp_to_collate", '*.xml')
    os.makedirs('collate-out', exist_ok=True)
    os.makedirs('collate-out/collated', exist_ok=True)
    output_dir = "./collate-out/collated"
    result_file = f'{output_dir}/collated.xml'
    result_html = './index.html'

    print("starting...")
    CxCollate(
        glob_pattern=all_manifests,
        glob_recursive=False,
        output_dir=output_dir,
        char_limit=False,
        chunk_size=CHUNK_SIZE,
        to_compare_xpath=XPATH
    ).collate()

    files = glob.glob(f"{output_dir}/*.tei")
    print(len(files))
    full_doc = merge_tei_fragments(files)
    with open(result_file, 'w') as f:
        f.write(ET.tostring(full_doc, encoding='UTF-8').decode('utf-8'))
    full_tei = make_full_tei_doc(result_file)
    # root = full_tei.tree
    full_tei.tree_to_file(result_file)
    positive_doc = make_positive_app(result_file)
    positive_doc.tree_to_file(result_file)

    crit_ap_with_rdgs = define_readings(result_file, manifest)
    # with open(result_file, 'w') as f:
    #     f.write(
    #         ET.tostring(
    #             crit_ap_with_rdgs.getroot(),
    #             encoding='UTF-8'
    #         ).decode('utf-8')
    #     )
    result_tei = ET.tostring(crit_ap_with_rdgs.getroot(), encoding='UTF-8')
    files = glob.glob(f"{output_dir}/*.html")
    full_doc = merge_html_fragments(files)
    with open(result_html, 'w') as f:
        f.write(full_doc.prettify("utf-8").decode('utf-8'))
    result_html = full_doc.prettify("utf-8").decode('utf-8')
    shutil.rmtree("tmp_to_collate")
    for x in glob.glob(f"{output_dir}/out__*"):
        print(f"removing {x}")
        os.remove(x)
    return result_tei


def remove_dir(save_path):
    shutil.rmtree(save_path)
