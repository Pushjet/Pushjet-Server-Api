from flask import Blueprint, render_template, current_app
from json import load, dumps
from string import ascii_letters
from uuid import uuid4
import re

docs = Blueprint('docs', __name__)
json_doc = None
mdRegex = [
    (re.compile(r'\[([^\]]+)\]\(([^\)]+)\)'), r'<a href="\2">\1</a>'),  # Link
    (re.compile(r'\*([^\*]+)\*'), r'<b>\1</b>'),  # Bold
]


def get_json():
    global json_doc
    if not json_doc:
        json_doc = load(open(current_app.static_folder + '/js/docs.json'))
    return json_doc


@docs.route('/docs/')
def docs_index():
    return render_template('index.html', docs=get_json(), uuid=uuid4())


@docs.app_template_filter('quickmd')
def filter_quickmd(s):
    for r in mdRegex:
        s = r[0].sub(r[1], s)
    return s


@docs.app_template_filter('typeref')
def filter_typeref(s):
    primitives = ['string', 'int']
    if s.lower() not in primitives:
        return '<a href="#type-%s">%s</a>' % (s, s)
    return s


@docs.app_template_filter('objref')
def filter_objref(s):
    return '<a href="#object-%s">%s<sup>[o]</sup></a>' % (s, s)


@docs.app_template_filter('yesno')
def filter_yesno(b):
    return 'yes' if b else 'no'


@docs.app_template_filter('objectbuilder')
def filter_build_object(s, dump=True):
    resp = {}
    data = get_json()['objects'][s]['variables']
    for v in data:
        resp[v] = data[v]['example'] if 'type' in data[v] else filter_build_object(data[v]['object'], False)
    return dumps(resp, indent=4, separators=(',', ': '), sort_keys=True) if dump else resp


@docs.app_template_filter('az')
def filter_letters(s):
    return ''.join(x for x in s if x in ascii_letters)
