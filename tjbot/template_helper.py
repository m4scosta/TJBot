# coding: utf-8
from jinja2 import Template
from os import path

SRC_DIR = path.dirname(__file__)
TEMPLATE_DIR = path.join(SRC_DIR, 'templates')


def load_template(template_name):
    with open(path.join(TEMPLATE_DIR, template_name)) as tpl:
        return Template(tpl.read().decode('utf-8'))


def render(template_name, **kwargs):
    template = load_template(template_name)
    return template.render(**kwargs)
