#!/usr/bin/env python
# Copyright (c) 2018, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory
# All rights reserved.
# This code is released under an MIT license, see LICENSE.txt for details.
"""Download reveal.js and optionally MathJax.

Also supply four light and four dark highlight.js styles, which have been
modified slightly to be compatible with reveal.js.  The issue is that
reveal.css contains

.reveal span { ... font: inherit; ...}

which defeats any changes in font-style (italic) or font-weight (bold) for
any of the highlight.js styles.  The solution here is to prepend the .reveal
class to all properties which mention font-style or font-weight.

The most readable highlight styles have muted colors, and distinguish elements
both by color and bold or italic styles.  By these standards, github is my
preference for the light styles, and obsidian for the dark styles.  Note that
the zenburn style provided with reveal.js 3.6.0 has not been modified for
compatibility, and fails to produce bold or italic highlights.

This module can be run as a script to download reveal.js and/or MathJax::

    python -m rst2slides.download [path] [-m [mathjax_tag]]

The default path is 'ui' in the current working directory; reveal.js will
be downloaded to the specified path, and the eight highlight.js css styles
will be copied to path/hljs/.  If the -m flag is specified, MathJax will
be downloaded to path/MathJax-master/ or to path/MathJax-tag if the mathjax
tag is specified.

"""

import os
import os.path
import sys
from io import BytesIO
from zipfile import ZipFile
from glob import glob

if sys.version_info < (3,):
    from urllib2 import urlopen
    input = raw_input
else:
    from urllib.request import urlopen


def setup(path='ui', math='master'):
    if not os.path.exists(os.path.join(path, 'js', 'reveal.js')):
        download_reveal(path)
    hljs = os.path.join(path, 'hljs')
    if not os.path.exists(hljs):
        copy_hljs_styles(hljs)
    if math and not glob(os.path.join(path, 'MathJax*')):
        download_mathjax(path, math)


def download_reveal(path, tag='master'):
    url = 'https://github.com/hakimel/reveal.js/archive/{}.zip'.format(tag)
    # rst2slides built at tag 3.6.0
    print('Downloading reveal.js...')
    top = os.path.dirname(path)
    ZipFile(BytesIO(urlopen(url).read())).extractall(top or None)
    if os.path.exists(path):
        old, i = path + '-old', 0
        while os.path.exists(old):
            old, i = path + '-old{}'.format(i), i + 1
        os.rename(path, old)
    os.rename(os.path.join(top, 'reveal.js-{}'.format(tag)), path)
    print('Done')


def download_mathjax(path, tag='master'):
    url = 'https://github.com/mathjax/MathJax/archive/{}.zip'.format(tag)
    # rst2slides built at tag 2.7.4
    print('Downloading MathJax...')
    ZipFile(BytesIO(urlopen(url).read())).extractall(path)
    print('Done')


def copy_hljs_styles(dest):
    """Copy four light and four dark highlight.js styles to `dest`."""
    if not dest.endswith('hljs'):
        dest = os.path.join(dest, 'hljs')
    if not os.path.isdir(dest):
        os.mkdir(dest)
    for style in hljs_styles:
        path = os.path.join(dest, style + '.css')
        if os.path.isfile(path):
            continue
        with open(path, 'w') as f:
            f.write(hljs_styles[style])


hljs_styles = {
    ############################################ Styles with light background

    'github': """/*

github.com style (c) Vasily Polovnyov <vast@whiteants.net>

*/

.hljs {
  display: block;
  overflow-x: auto;
  padding: 0.5em;
  color: #333;
  background: #f8f8f8;
}

.reveal .hljs-comment,
.reveal .hljs-quote {
  color: #998;
  font-style: italic;
}

.reveal .hljs-keyword,
.reveal .hljs-selector-tag,
.reveal .hljs-subst {
  color: #333;
  font-weight: bold;
}

.hljs-number,
.hljs-literal,
.hljs-variable,
.hljs-template-variable,
.hljs-tag .hljs-attr {
  color: #008080;
}

.hljs-string,
.hljs-doctag {
  color: #d14;
}

.reveal .hljs-title,
.reveal .hljs-section,
.reveal .hljs-selector-id {
  color: #900;
  font-weight: bold;
}

.reveal .hljs-subst {
  font-weight: normal;
}

.reveal .hljs-type,
.reveal .hljs-class .hljs-title {
  color: #458;
  font-weight: bold;
}

.reveal .hljs-tag,
.reveal .hljs-name,
.reveal .hljs-attribute {
  color: #000080;
  font-weight: normal;
}

.hljs-regexp,
.hljs-link {
  color: #009926;
}

.hljs-symbol,
.hljs-bullet {
  color: #990073;
}

.hljs-built_in,
.hljs-builtin-name {
  color: #0086b3;
}

.reveal .hljs-meta {
  color: #999;
  font-weight: bold;
}

.hljs-deletion {
  background: #fdd;
}

.hljs-addition {
  background: #dfd;
}

.reveal .hljs-emphasis {
  font-style: italic;
}

.reveal .hljs-strong {
  font-weight: bold;
}
""",

    'solarized-light': """/*

Orginal Style from ethanschoonover.com/solarized (c) Jeremy Hull <sourdrums@gmail.com>

*/

.hljs {
  display: block;
  overflow-x: auto;
  padding: 0.5em;
  background: #fdf6e3;
  color: #657b83;
}

.hljs-comment,
.hljs-quote {
  color: #93a1a1;
}

/* Solarized Green */
.hljs-keyword,
.hljs-selector-tag,
.hljs-addition {
  color: #859900;
}

/* Solarized Cyan */
.hljs-number,
.hljs-string,
.hljs-meta .hljs-meta-string,
.hljs-literal,
.hljs-doctag,
.hljs-regexp {
  color: #2aa198;
}

/* Solarized Blue */
.hljs-title,
.hljs-section,
.hljs-name,
.hljs-selector-id,
.hljs-selector-class {
  color: #268bd2;
}

/* Solarized Yellow */
.hljs-attribute,
.hljs-attr,
.hljs-variable,
.hljs-template-variable,
.hljs-class .hljs-title,
.hljs-type {
  color: #b58900;
}

/* Solarized Orange */
.hljs-symbol,
.hljs-bullet,
.hljs-subst,
.hljs-meta,
.hljs-meta .hljs-keyword,
.hljs-selector-attr,
.hljs-selector-pseudo,
.hljs-link {
  color: #cb4b16;
}

/* Solarized Red */
.hljs-built_in,
.hljs-deletion {
  color: #dc322f;
}

.hljs-formula {
  background: #eee8d5;
}

.reveal .hljs-emphasis {
  font-style: italic;
}

.reveal .hljs-strong {
  font-weight: bold;
}
""",

    'atom-one-light':"""/*

Atom One Light by Daniel Gamage
Original One Light Syntax theme from https://github.com/atom/one-light-syntax

base:    #fafafa
mono-1:  #383a42
mono-2:  #686b77
mono-3:  #a0a1a7
hue-1:   #0184bb
hue-2:   #4078f2
hue-3:   #a626a4
hue-4:   #50a14f
hue-5:   #e45649
hue-5-2: #c91243
hue-6:   #986801
hue-6-2: #c18401

*/

.hljs {
  display: block;
  overflow-x: auto;
  padding: 0.5em;
  color: #383a42;
  background: #fafafa;
}

.reveal .hljs-comment,
.reveal .hljs-quote {
  color: #a0a1a7;
  font-style: italic;
}

.hljs-doctag,
.hljs-keyword,
.hljs-formula {
  color: #a626a4;
}

.hljs-section,
.hljs-name,
.hljs-selector-tag,
.hljs-deletion,
.hljs-subst {
  color: #e45649;
}

.hljs-literal {
  color: #0184bb;
}

.hljs-string,
.hljs-regexp,
.hljs-addition,
.hljs-attribute,
.hljs-meta-string {
  color: #50a14f;
}

.hljs-built_in,
.hljs-class .hljs-title {
  color: #c18401;
}

.hljs-attr,
.hljs-variable,
.hljs-template-variable,
.hljs-type,
.hljs-selector-class,
.hljs-selector-attr,
.hljs-selector-pseudo,
.hljs-number {
  color: #986801;
}

.hljs-symbol,
.hljs-bullet,
.hljs-link,
.hljs-meta,
.hljs-selector-id,
.hljs-title {
  color: #4078f2;
}

.reveal .hljs-emphasis {
  font-style: italic;
}

.reveal .hljs-strong {
  font-weight: bold;
}

.hljs-link {
  text-decoration: underline;
}
""",

    'default': """/*

Original highlight.js style (c) Ivan Sagalaev <maniac@softwaremaniacs.org>

*/

.hljs {
  display: block;
  overflow-x: auto;
  padding: 0.5em;
  background: #F0F0F0;
}


/* Base color: saturation 0; */

.hljs,
.hljs-subst {
  color: #444;
}

.hljs-comment {
  color: #888888;
}

.reveal .hljs-keyword,
.reveal .hljs-attribute,
.reveal .hljs-selector-tag,
.reveal .hljs-meta-keyword,
.reveal .hljs-doctag,
.reveal .hljs-name {
  font-weight: bold;
}


/* User color: hue: 0 */

.hljs-type,
.hljs-string,
.hljs-number,
.hljs-selector-id,
.hljs-selector-class,
.hljs-quote,
.hljs-template-tag,
.hljs-deletion {
  color: #880000;
}

.reveal .hljs-title,
.reveal .hljs-section {
  color: #880000;
  font-weight: bold;
}

.hljs-regexp,
.hljs-symbol,
.hljs-variable,
.hljs-template-variable,
.hljs-link,
.hljs-selector-attr,
.hljs-selector-pseudo {
  color: #BC6060;
}


/* Language color: hue: 90; */

.hljs-literal {
  color: #78A960;
}

.hljs-built_in,
.hljs-bullet,
.hljs-code,
.hljs-addition {
  color: #397300;
}


/* Meta color: hue: 200 */

.hljs-meta {
  color: #1f7199;
}

.hljs-meta-string {
  color: #4d99bf;
}


/* Misc effects */

.reveal .hljs-emphasis {
  font-style: italic;
}

.reveal .hljs-strong {
  font-weight: bold;
}
""",

    ################################################ Styles with dark background

    'obsidian': """/**
 * Obsidian style
 * ported by Alexander Marenin (http://github.com/ioncreature)
 */

.hljs {
  display: block;
  overflow-x: auto;
  padding: 0.5em;
  background: #282b2e;
}

.hljs-keyword,
.hljs-selector-tag,
.hljs-literal,
.hljs-selector-id {
  color: #93c763;
}

.hljs-number {
  color: #ffcd22;
}

.hljs {
  color: #e0e2e4;
}

.hljs-attribute {
  color: #668bb0;
}

.hljs-code,
.hljs-class .hljs-title,
.hljs-section {
  color: white;
}

.hljs-regexp,
.hljs-link {
  color: #d39745;
}

.hljs-meta {
  color: #557182;
}

.hljs-tag,
.hljs-name,
.hljs-bullet,
.hljs-subst,
.hljs-emphasis,
.hljs-type,
.hljs-built_in,
.hljs-selector-attr,
.hljs-selector-pseudo,
.hljs-addition,
.hljs-variable,
.hljs-template-tag,
.hljs-template-variable {
  color: #8cbbad;
}

.hljs-string,
.hljs-symbol {
  color: #ec7600;
}

.hljs-comment,
.hljs-quote,
.hljs-deletion {
  color: #818e96;
}

.hljs-selector-class {
  color: #A082BD
}

.reveal .hljs-keyword,
.reveal .hljs-selector-tag,
.reveal .hljs-literal,
.reveal .hljs-doctag,
.reveal .hljs-title,
.reveal .hljs-section,
.reveal .hljs-type,
.reveal .hljs-name,
.reveal .hljs-strong {
  font-weight: bold;
}
""",

    'zenburn': """/*

Zenburn style from voldmar.ru (c) Vladimir Epifanov <voldmar@voldmar.ru>
based on dark.css by Ivan Sagalaev

*/

.hljs {
  display: block;
  overflow-x: auto;
  padding: 0.5em;
  background: #3f3f3f;
  color: #dcdcdc;
}

.hljs-keyword,
.hljs-selector-tag,
.hljs-tag {
  color: #e3ceab;
}

.hljs-template-tag {
  color: #dcdcdc;
}

.hljs-number {
  color: #8cd0d3;
}

.hljs-variable,
.hljs-template-variable,
.hljs-attribute {
  color: #efdcbc;
}

.hljs-literal {
  color: #efefaf;
}

.hljs-subst {
  color: #8f8f8f;
}

.hljs-title,
.hljs-name,
.hljs-selector-id,
.hljs-selector-class,
.hljs-section,
.hljs-type {
  color: #efef8f;
}

.hljs-symbol,
.hljs-bullet,
.hljs-link {
  color: #dca3a3;
}

.hljs-deletion,
.hljs-string,
.hljs-built_in,
.hljs-builtin-name {
  color: #cc9393;
}

.hljs-addition,
.hljs-comment,
.hljs-quote,
.hljs-meta {
  color: #7f9f7f;
}


.reveal .hljs-emphasis {
  font-style: italic;
}

.reveal .hljs-strong {
  font-weight: bold;
}
""",

    'solarized-dark': """/*

Orginal Style from ethanschoonover.com/solarized (c) Jeremy Hull <sourdrums@gmail.com>

*/

.hljs {
  display: block;
  overflow-x: auto;
  padding: 0.5em;
  background: #002b36;
  color: #839496;
}

.hljs-comment,
.hljs-quote {
  color: #586e75;
}

/* Solarized Green */
.hljs-keyword,
.hljs-selector-tag,
.hljs-addition {
  color: #859900;
}

/* Solarized Cyan */
.hljs-number,
.hljs-string,
.hljs-meta .hljs-meta-string,
.hljs-literal,
.hljs-doctag,
.hljs-regexp {
  color: #2aa198;
}

/* Solarized Blue */
.hljs-title,
.hljs-section,
.hljs-name,
.hljs-selector-id,
.hljs-selector-class {
  color: #268bd2;
}

/* Solarized Yellow */
.hljs-attribute,
.hljs-attr,
.hljs-variable,
.hljs-template-variable,
.hljs-class .hljs-title,
.hljs-type {
  color: #b58900;
}

/* Solarized Orange */
.hljs-symbol,
.hljs-bullet,
.hljs-subst,
.hljs-meta,
.hljs-meta .hljs-keyword,
.hljs-selector-attr,
.hljs-selector-pseudo,
.hljs-link {
  color: #cb4b16;
}

/* Solarized Red */
.hljs-built_in,
.hljs-deletion {
  color: #dc322f;
}

.hljs-formula {
  background: #073642;
}

.reveal .hljs-emphasis {
  font-style: italic;
}

.reveal .hljs-strong {
  font-weight: bold;
}
""",

    'atom-one-dark': """/*

Atom One Dark by Daniel Gamage
Original One Dark Syntax theme from https://github.com/atom/one-dark-syntax

base:    #282c34
mono-1:  #abb2bf
mono-2:  #818896
mono-3:  #5c6370
hue-1:   #56b6c2
hue-2:   #61aeee
hue-3:   #c678dd
hue-4:   #98c379
hue-5:   #e06c75
hue-5-2: #be5046
hue-6:   #d19a66
hue-6-2: #e6c07b

*/

.hljs {
  display: block;
  overflow-x: auto;
  padding: 0.5em;
  color: #abb2bf;
  background: #282c34;
}

.reveal .hljs-comment,
.reveal .hljs-quote {
  color: #5c6370;
  font-style: italic;
}

.hljs-doctag,
.hljs-keyword,
.hljs-formula {
  color: #c678dd;
}

.hljs-section,
.hljs-name,
.hljs-selector-tag,
.hljs-deletion,
.hljs-subst {
  color: #e06c75;
}

.hljs-literal {
  color: #56b6c2;
}

.hljs-string,
.hljs-regexp,
.hljs-addition,
.hljs-attribute,
.hljs-meta-string {
  color: #98c379;
}

.hljs-built_in,
.hljs-class .hljs-title {
  color: #e6c07b;
}

.hljs-attr,
.hljs-variable,
.hljs-template-variable,
.hljs-type,
.hljs-selector-class,
.hljs-selector-attr,
.hljs-selector-pseudo,
.hljs-number {
  color: #d19a66;
}

.hljs-symbol,
.hljs-bullet,
.hljs-link,
.hljs-meta,
.hljs-selector-id,
.hljs-title {
  color: #61aeee;
}

.reveal .hljs-emphasis {
  font-style: italic;
}

.reveal .hljs-strong {
  font-weight: bold;
}

.hljs-link {
  text-decoration: underline;
}
"""}

if __name__ == '__main__':
    args = sys.argv[1:]
    math = False
    if '-h' in args or '--help' in args:
        print('Usage: python -m rst2slides.download [path] [-m [mathjax_tag]]')
        sys.exit(0)
    if '-m' in args:
        i = args.index('-m')
        math = args[i+1] if len(args) > i+1 else 'master'
        del args[i:]
    path = args[0] if args else 'ui'
    setup(path, math)
