import os
import glob
import shutil
import requests
import json
import xml.etree.ElementTree as ET

from zipfile import ZipFile
from acdh_collatex_utils.acdh_collatex_utils import CxCollate
from acdh_collatex_utils.post_process import (
    merge_tei_fragments,
    make_full_tei_doc,
    define_readings,
    make_positive_app
)


def get_frd_data(url, save_path, path_dir, save):
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
    if save:
        with open('test.json', "w") as f:
            json.dump(dct_man, f)
    return dct_man


def create_html_template(input):
    all_works = '<div id="all_works">'
    for x in input:
        div = f'<div id="w__{x}">'
        w = f'<label>Werksignatur {x}:</label>'
        div += w
        select = f"""<select class="custom-select" id="s__{x}" onchange="get_select(this)">
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
    with open('test.xml', 'wb') as f:
        f.write(tei)
    return tei


def collate_tei(save_path, path_dir, select):
    el = select
    werk = el[1].replace('s__', '')
    manifest = el[0]
    all_manifests = os.path.join(save_path, '*', path_dir, werk, '*.xml')
    os.makedirs('collate-out', exist_ok=True)
    os.makedirs('collate-out/collated', exist_ok=True)
    output_dir = "./collate-out/collated"
    result_file = f'{output_dir}/collated.xml'
    # result_html = './index.html'

    print("starting...")
    CxCollate(
        glob_pattern=all_manifests,
        glob_recursive=False,
        output_dir=output_dir,
        char_limit=False,
        chunk_size=7000,
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
    # files = glob.glob(f"{output_dir}/*.html")
    # full_doc = merge_html_fragments(files)
    # with open(result_html, 'w') as f:
    #     f.write(full_doc.prettify("utf-8").decode('utf-8'))
    # result_html = full_doc.prettify("utf-8").decode('utf-8')
    for x in glob.glob(f"{output_dir}/out__*"):
        print(f"removing {x}")
        os.remove(x)
    return result_tei


def remove_dir(save_path):
    unziped_dir = glob.glob(os.path.join(save_path, '*'))
    for dir in unziped_dir:
        shutil.rmtree(dir)
        print(f'{dir}: dir removed')