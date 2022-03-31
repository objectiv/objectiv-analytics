import glob
import re
from os import path, makedirs
import json
from typing import Dict, List
from lxml import html, etree

"""
Copyright Objectiv B.V. 2021

Used to import Sphinx generated python docs into docusaurus. This script does the following:
- find all html pages in build/html
- extract the "body" from the page
- fix links in the "modules"
- extract toc from the html
- preserve order of left navbar, by extracting/saving that (using sidebar_order)
- write the static html to docusaurus/static/_{module}
- generate .mdx files, and write those to {docs}/{module}

"""

# html build dir / output of sphinx
html_dir = 'build/html/'

# root of docusaurus install
docusaurus_dir = '../../../objectiv.io/docs'
# where are the docs at
docs = 'docs'
# where to put static content
static = 'static'

# base dir of these docs (relative to docusaurus_dir/docs/
module = 'modeling'

docs_target = f'{docusaurus_dir}/{docs}/{module}'
# full path to base for the static files. note the `_` here. This is needed
# so docusaurus doesn't break this in a full build
static_target = f'{docusaurus_dir}/{static}/_{module}'

# the actual index page, as `index.html` should contain the index, that is main navigation/ toctree
index_page = 'intro'

# these categories only get a toplevel entry in the sidebar
# but no submenus for the headers
skip_categories = ['Introduction']

# replacement label to avoid duplicates
category_index = 'Overview'

# whitelist of pages to consider
# subdirs / modules will be auto-added below
patterns = [
    '^intro.html$',
    '^example_notebooks.html$',
    '^models.html$',
    '^modelhub_basics.html$',
    '^open_taxonomy.html$',
    '^modelhub_api_reference.html$',
    '^bach.html$',
    '^feature_engineering.html$',
    '^machine_learning.html$',
    '^product_analytics.html$',
    '^bach_core_concepts.html$',
    '^bach_examples.html$',
    '^bach_reference.html$',
    "^bach_whatisbach.html$"
]

# list of special cases, where we have a subdir, with an introduction at toplevel
# eg /dataframe.html and /dataframe/
for fn in glob.glob(f'{html_dir}/*'):
    dn = fn.replace('.html', '')
    if path.isfile(fn) and path.isdir(dn):
        patterns.extend([f'{path.basename(dn)}.*', f'{path.basename(fn).replace(".html", "")}.*'])


def a_to_toc(a: html.Element, level: int) -> Dict:
    """
    provided an anchor HTML element, return a docusaurus toc item
    :param a: html.Element
    :param level: level of indentation in the toc, should be either 2 or 3
    :return: Dictionary with toc_item
    """
    return {
        'value': a.text.strip(),
        'id': a.get('href')[1:],
        'children': [],
        'level': level
    }


"""
structure of main navigation as in index.html
<div id=bd-docs-nav>
    <div>
        <ul>
            <li>
                <a href=#>
                    DataFrame
                </a>
                <ul>
                    <li>
                        <a href=dataframe/bach.DataFrame.html>
                            bach.DataFrame
                        </a>
                        <ul>
                            <li>
                                <a href=dataframe/bach.DataFrame.agg.html>
                                    bach.DataFrame.agg
                                </a>
                            </li>
                        </ul>
                    </li>
                    <li>
                        <a href=dataframe/bach.DataFrame.from_table.html>
                            bach.DataFrame.from_table
                        </a>
                    </li>
                </ul>
            </li>
        </ul>
    </div>k
</div>

"""


def parse_ul_menu(ul: html.Element) -> List:
    """
    Build tree of menu structure, by recursively traversing all UL/LIs
    :param ul: html.Element - part of an html doc
    :return: List of lists, representing the tree
    """
    menu_items = []
    for element in ul:
        item = {
            'children': []
        }
        if element.tag == 'ul':
            return parse_ul_menu(element)
        if element.tag == 'li':
            for sub_element in element:
                if sub_element.tag == 'a':
                    item['href'] = sub_element.get('href')
                    item['text'] = sub_element.text.strip()
                elif sub_element.tag == 'ul':
                    item['children'] += parse_ul_menu(sub_element)
                else:
                    print(f'unknown tag in sub_element: {sub_element.tag}')
        else:
            print(f'unknown tag in element: {element.tag}')
        menu_items.append(item)
    return menu_items


def menu_list_to_sidebar(menu_items: list, level: int = 0) -> List[Dict[str, str]]:
    """
    Transform menu tree into something docusaurus can interpret as a sidebar
    :param menu_items: List of lists
    :param level: int - internal var, keeping track of how deep we are in the tree
    :return: List[Dict] - can be directly json-dumped into a sidebar
    """
    sb = []
    for menu_item in menu_items:
        items = []
        href = menu_item['href'].replace('.html', '')
        label = menu_item['text']

        # if this is a deeper nested item, and a fully qualified name, let's remove the class/module name
        # for a more compact tree
        parts = label.split('.')
        if level > 0 and len(parts) > 1:
            label = parts[-1]

        if '#' in href:
            if menu_item['href'].startswith(f'{index_page}#'):
                # this is the "index" page, so correct path
                href = menu_item['href'].replace(index_page, '')

            if level > 0 or len(menu_item['children']) == 0 or menu_item['text'] in skip_categories:
                # To avoid duplicates (because Docusaurus doesn't support categories with links),
                # we only add the link, if:
                # - we're not at top level
                # - there are no children (so no category with the same name)
                # - the item is not in the skip_categories list
                items = [{
                    'type': 'link',
                    'label': label,
                    'href': f"/{module}/{href}"
                }]
        else:
            items = [{
                'type': 'doc',
                'label': label,
                'id': f'{module}/{href}'
            }]
        if len(menu_item['children']) > 0 and menu_item['text'] not in skip_categories and menu_item['href']:
            # this is a case where we have a duplicate (both children and an href)
            menu_item_children = []
            if level > -1:
                print(f'moving parent {menu_item["text"]} into children')
                # get parent, and put in here, but only below top level
                menu_item_children = items.copy()
                if len(menu_item_children) > 1:
                    print(f'There should not be more than 1 child in this list! {menu_item_children}')
                    exit(1)
                # change label of parent to introduction
                if len(menu_item_children) > 0:
                    menu_item_children[0]['label'] = category_index
                # reset original list
                items = []
            menu_item_children += menu_list_to_sidebar(menu_item['children'], level=level + 1)

            # get rid of any pre-existing introduction heading
            # logically there wouldn't be more than 1, so we quit
            # after we find one and get rid of it (otherwise the loop breaks)
            for i in range(1, len(menu_item_children)):
                if menu_item_children[i]['label'] == category_index:
                    del menu_item_children[i]
                    break

            items.append({
                'type': 'category',
                'label': label,
                'items': menu_item_children
            })
        if len(items) > 0:
            sb += items
    return sb


# generate docusaurus sidebar
doc = html.parse(f'{html_dir}/index.html')

menu_list = doc.xpath('//div[@class="toctree-wrapper compound"]/ul')

menu = []
for ml in menu_list:
    menu += list(parse_ul_menu(ml))

sidebar = menu_list_to_sidebar(menu)

sidebar_js = f"""
module.exports = {json.dumps(sidebar, indent=4)}
"""

# now write html body
html_path = f'{docs_target}/sidebar.js'
with open(html_path, 'w') as target_handle:
    target_handle.write(sidebar_js)

# sort urls alphabetically, remove .html
urls = glob.glob(f"{html_dir}/**/*.html", recursive=True)

for url in urls:
    # this is the url to the original html fragment
    # it's an absolute url, docusaurus will take care of the rest
    real_url = url.replace(html_dir, "")
    page = path.basename(url).replace('.html', '')

    print(f'{url} -> {real_url} {page}')

    match = False
    for pattern in patterns:
        if re.match(pattern, real_url):
            match = True
    if not match:
        print(f'ignoring {real_url}')
        continue

    # dir where .mdx will be stored
    docs_target_dir = f'{docs_target}/{path.dirname(real_url)}'
    mdx_path = f'{docs_target}/{real_url.replace(".html", ".mdx")}'

    static_target_dir = f'{static_target}/{path.dirname(real_url)}'

    # create dir if needed
    if not path.isdir(docs_target_dir):
        print(f'creating {docs_target_dir}')
        makedirs(docs_target_dir)

    # create dir if needed
    if not path.isdir(static_target_dir):
        print(f'creating {static_target_dir}')
        makedirs(static_target_dir)

    doc = html.parse(url)

    # get title from <title> text </title>
    title = doc.xpath('//title/text()')[0]

    # here we get the body
    # we look for <main role="main"....>
    body_element: html.Element = doc.xpath('//main[@role="main"]/div')[0]
    body = etree.tostring(body_element).decode('utf-8')

    # try to determine description
    description_elements = body_element.xpath('//main[@role="main"]/div/section//p')

    if len(description_elements) > 0:
        description_element = description_elements[0].text
        words = description_element.replace('\n', ' ').split(' ')

        description = ''
        # let's put whole words in the description, with a max length of 500 chars
        for word in words:
            if description == '':
                description = word
            else:
                description += f' {word}'
            if len(description) > 500:
                break
    else:
        # if we cannot find one, use title
        description = title

    toc = []
    # get toc from:
    # <nav id="bd-toc-nav">/ul
    # contains an unordered list (<ul> of toc items)
    # this is typically only 2 layers deep, so no need for recursion here
    toc_containers = doc.xpath('//nav[@id="bd-toc-nav"]/ul')

    if len(toc_containers) > 0:
        toc_container = toc_containers[0]
        toc_item = None
        for l1_item in toc_container:
            children = []
            for l2_item in l1_item:
                if l2_item.tag == 'a':
                    # this is a toplevel menu item
                    toc_item = a_to_toc(l2_item, 2)
                elif l2_item.tag == 'ul':
                    for l3_item in l2_item.findall('li/a'):
                        children.append(a_to_toc(l3_item, 3))
            if toc_item:
                toc_item['children'] = children
                toc.append(toc_item)

    if page == index_page:
        # special case where we map the index to Introduction
        slug = f'/{module}/'
        sidebar_label = 'Introduction'

    else:
        slug = f'/{module}/{real_url.replace(".html", "")}'
        # don't override sidebar_label by default, so we can set it from the sidebar.js
        sidebar_label = None

    # template for the mdx file
    # please leave the whitespace as is (it's part of the markdown)
    mdx = \
        f"""---
id: {real_url.replace('.html', '').split('/')[-1]}
title: {title}
hide_title: true
slug: {slug}
{f"sidebar_label: {sidebar_label}" if sidebar_label else ''}

---
<head>
    <meta name="description" content="{description}" />
    <meta property="og:description" content="{description}" />
</head>

export const toc = {json.dumps(toc, indent=4)};


import SphinxPages from '@site/src/components/sphinx-page'
import useBaseUrl from '@docusaurus/useBaseUrl'


<SphinxPages url={{useBaseUrl('{module}/{real_url}')}} />
"""

    print(f'writing to {mdx_path}')
    with open(mdx_path, 'w') as target_handle:
        target_handle.write(mdx)

    # now write html body to static content directory
    # we load the actual content through the SphinxPages React component, because Docusaurus doesn't
    # like the plain HTML we have, as it tries to interpret it as either MD, or as JSX/TS
    html_path = f'{static_target}/{real_url}'
    with open(html_path, 'w') as target_handle:
        target_handle.write(body)
