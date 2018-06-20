#!/usr/bin/env python
# Copyright (c) 2018, Lawrence Livermore National Security, LLC
# All rights reserved.
# This code is released under an MIT license, see LICENSE.txt for details.
"""A docutils writer to convert rst files to reveal-js.

Based on public domain or open source code by Ezio Melotti, Julien Vitay,
and the rst2s5 HTML writer from docutils:

* http://bitbucket.org/ezio_melotti/rst2reveal
* http://bitbucket.org/vitay/rst2reveal (or http://github.com/vitay/rst2reveal)
* git://repo.or.cz/docutils.git

Presentation rst begins like this:

==================
Presentation Title
==================
Optional presentation subtitle
++++++++++++++++++++++++++++++

.. titlepage::
    :authors: My Name, Another Name
    :date: April 1, 2018
    :organization: My Company

.. background:: image/titlepage.png

First slide
===========

Contents of first slide.  Slides with same underlining as First Slide
progress left-to-right.

Subslide one
------------

Slides with same underlining as Subslide one progress top-to-bottom.
Subslides should continue discussion of same topic as their top-level
parent.

Subslide two
------------

The background directive may appear in any slide or subslide to set the
background for that slide only.  Reveal.js also will set CSS classes for
individual slides which contain a reveal-state directive:

.. reveal-state:: fancy-format specialty
   :timing: 120

The timing option, if present, sets the speaker view timer for the
individual slide.

Second slide
============

The video directive is similar to the standard rst image directive:

.. video:: http://techslides.com/demos/sample-videos/small.mp4
   :width: 50%
   :align: right

It also accepts controls, loop, and autoplay field options.

.. aside:: notes

    Body is speaker note (in <aside class="notes"> element)

You can change the transition to the next slide only with any of the reveal.js
choices none/fade/slide/convex/concave/zoom:

.. transition:: fade

Third slide
===========

Add :trim: option to code:: directive to add data-trim?

Last slide
==========

You can apply most reveal.js initialization options using the reveal directive
(which may appear anywhere in the document).  For an exhaustive list, see
https://github.com/hakimel/reveal.js#configuration .  The default reveal.js
screen is near 4:3 (960x700 pixels) and uses slide transitions.  To make the
presentation fit a 16:9 screen and use fade transitions, use:

.. reveal::
  :width: 1280
  :height: 720
  :transition: fade

You can also supply many of the standard rst configuration options in the
rst source itself using the configure directive.  An exhaustive list is at
http://docutils.sourceforge.net/docs/user/config.html .  Many default
options have been changed to be more consistent with reveal.js.  The
stylesheet options are particularly useful (stylesheet_path, stylesheet_dirs,
and embed_stylesheet in addition to plain stylesheet:

.. configure::
  :stylesheet: css/custom.css


Layout of your presentation repo::

    your_presentation.rst
    <supporting code and figures>
    css/
        custom.css
        localfonts.css
    font/
    image/

    ui/    reveal.js, highlight.js, and, optionally, MathJax
        js/    reveal.js and highlight.js javascript
        css/
            reveal.css
            print/  reveal.js paper and pdf themes
                paper.css, pdf.css
            theme/  reveal.js themes
                beige, black, blood, league, moon, night, serif, simple,
                sky, solarized, white
            hljs/   highlight.js styles (modified for reveal.js compatibility)
                atom-one-dark, atom-one-light, default, github, obsidian,
                solarized-dark, solarized-light, zenburn
        lib/        some fonts used in reveal.js themes
        MathJax*/
            ...

"""

import sys
import os.path
from glob import glob

from docutils import nodes
from docutils.writers import html5_polyglot
from docutils.core import publish_cmdline, default_description
from docutils.parsers.rst import directives

from . import directives as local_directives
from .directives import (VideoDirective, ConfigureDirective, RevealDirective,
                         BackgroundDirective, TransitionDirective,
                         TitlepageDirective, RevealStateDirective,
                         AsideDirective, mathjax_default, HLjsCodeBlock)
from .download import setup

if sys.version_info >= (3,):
    basestring = str

directives.register_directive('video', VideoDirective)
directives.register_directive('configure', ConfigureDirective)
directives.register_directive('reveal', RevealDirective)
directives.register_directive('background', BackgroundDirective)
directives.register_directive('transition', TransitionDirective)
directives.register_directive('titlepage', TitlepageDirective)
directives.register_directive('reveal-state', RevealStateDirective)
directives.register_directive('aside', AsideDirective)
directives.register_directive('code', HLjsCodeBlock)

# Unfortunately, Writer and HTMLTranslator are old-style classes in python2,
# which means that super() does not work.
writer_baseclass = html5_polyglot.Writer
html_baseclass = html5_polyglot.HTMLTranslator


class Writer(writer_baseclass):
    default_stylesheet = None

    def __init__(self):
        # Base class is old style in python2, super does not work.
        writer_baseclass.__init__(self)
        self.translator_class = HTMLTranslator


REVEAL_DIR = local_directives.REVEAL_DIR = 'ui'
REVEAL_THEME = 'beige'
HLJS_STYLE = 'github'

# highlight.js wants simply
# <pre><code class="python"> ... </code></pre>   "nohighlight" to disable
# notable styles, github is best light, zenburn or obsidian best dark:
# default (L), atom-one-dark, atom-one-light, github (L), solarized-dark,
# solarized-light, obsidian (D), zenburn (D), docco (L), dracula (D)

# pygments/external/rst-directive.py  is a code-blocks Directive subclass


class HTMLTranslator(html_baseclass):
    doctype = '<!doctype html>\n'
    content_type = '<meta charset="%s">\n'
    head_prefix_template = '<html lang="%(lang)s">\n<head>\n'
    reveal_stylesheet_template = """
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />

<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

<link rel="stylesheet" href="%(reveal_dir)s/css/reveal.css">
<style>
  .reveal .slides {text-align:left;}
  .reveal h1, .reveal h2, .reveal .subtitle {text-align:center;}
  .reveal .align-center {display:block; margin-left:auto; margin-right:auto;}
  .reveal .align-left {float:left;}
  .reveal .align-right {float:right;}
</style>
<link rel="stylesheet" href="%(reveal_dir)s/css/theme/%(theme)s.css" id="theme">

<!-- Code syntax highlighting -->
<link rel="stylesheet" href="%(reveal_dir)s/hljs/%(hljs_style)s.css">

<!-- Printing and PDF exports -->
<script>
        var link = document.createElement( 'link' );
        link.rel = 'stylesheet';
        link.type = 'text/css';
        link.href = window.location.search.match( /print-pdf/gi ) ? '%(reveal_dir)s/css/print/pdf.css' : '%(reveal_dir)s/css/print/paper.css';
        document.getElementsByTagName( 'head' )[0].appendChild( link );
</script>

<!--[if lt IE 9]>
<script src="%(reveal_dir)s/lib/js/html5shiv.js"></script>
<![endif]-->
"""  # noqa
    reveal_ending_scripts = """
<script src="%(reveal_dir)s/lib/js/head.min.js"></script>
<script src="%(reveal_dir)s/js/reveal.js"></script>

<script>

    // Full list of configuration options available at:
    // https://github.com/hakimel/reveal.js#configuration
    Reveal.initialize({
%(reveal_init)s
%(reveal_math)s
        // Optional reveal.js plugins
        dependencies: [
            { src: '%(reveal_dir)s/lib/js/classList.js', condition: function() { return !document.body.classList; } },%(reveal_math_dep)s
            { src: '%(reveal_dir)s/plugin/markdown/marked.js', condition: function() { return !!document.querySelector( '[data-markdown]' ); } },
            { src: '%(reveal_dir)s/plugin/markdown/markdown.js', condition: function() { return !!document.querySelector( '[data-markdown]' ); } },
            { src: '%(reveal_dir)s/plugin/highlight/highlight.js', async: true, condition: function() { return !!document.querySelector( 'pre code' ); }, callback: function() { hljs.initHighlightingOnLoad(); } },
            { src: '%(reveal_dir)s/plugin/search/search.js', async: true },
            { src: '%(reveal_dir)s/plugin/zoom-js/zoom.js', async: true },
            { src: '%(reveal_dir)s/plugin/notes/notes.js', async: true }
        ]
    });

</script>
"""  # noqa
    reveal_math_option = """\
        math: {
            mathjax: '%(mathjax)s',
            config: '%(config)s'
        },
"""
    reveal_math_dep = """
            { src: '%(reveal_dir)s/plugin/math/math.js', async: true },"""

    def __init__(self, document):
        # html5_polyglot minimal.css and plain.css break reveal.js
        # Apparently, settings_override below gets rid of these,
        # but go ahead and check here anyway.
        settings = document.settings
        spath = settings.stylesheet_path
        if 'minimal.css' in spath:
            spath.remove('minimal.css')
        if 'plain.css' in spath:
            spath.remove('plain.css')
        sdir = settings.stylesheet_dirs
        for p in [d for d in sdir if 'html5_polyglot' in d]:
            sdir.remove(p)
        html_baseclass.__init__(self, document)  # super() broken in PY2
        self.reveal_dir = getattr(document, 'reveal_dir', REVEAL_DIR)
        # add this at the beginning, so that extra CSS are added afterwards
        # and can override the reveal.js CSS rules
        hljs = getattr(document, 'hljs', HLJS_STYLE)
        theme = getattr(document, 'theme', REVEAL_THEME)
        self.stylesheet.insert(0, self.reveal_stylesheet_template %
                               {'reveal_dir': self.reveal_dir,
                                'theme': theme, 'hljs_style': hljs})
        self.close_section = False

    def depart_document(self, node):
        self.head_prefix.extend([self.doctype,
                                 self.head_prefix_template %
                                 {'lang': self.settings.language_code}])
        self.html_prolog.append(self.doctype)
        meta_charset = self.content_type % self.settings.output_encoding
        self.meta.insert(0, meta_charset)
        self.head.insert(0, meta_charset)
        # skip content-type meta tag with interpolated charset value:
        self.html_head.extend(self.head[1:])
        self.body_prefix.append('<div class="reveal">\n<div class="slides">\n')
        reveal = {'reveal_dir': self.reveal_dir}
        if self.math_header:
            # Either a math role or directive is actually present.
            if hasattr(node, 'mathjax'):
                mathjax = node.mathjax
            else:
                mathjax = mathjax_default.copy()
            local_mathjax = glob(os.path.join(self.reveal_dir, 'MathJax*'))
            if local_mathjax:
                local_mathjax.sort()
                local_mathjax = local_mathjax[-1]
                mathjax['mathjax'] = os.path.join(local_mathjax, 'MathJax.js')
                local_mathjax = False  # already exists, no need to download
            elif (not mathjax['mathjax'].startswith('http') and
                      not os.path.exists(mathjax['mathjax'])):
                path = mathjax['mathjax'].rsplit('-', 1)
                if len(path) < 2 or not path[0].endswith('MathJax'):
                    print("WARNING: No such path as {}"
                          "".format(mathjax['mathjax']))
                    local_mathjax = None
                else:
                    i = len(os.path.join(self.reveal_dir, 'MathJax-'))
                    local_mathjax = os.path.join(path[-1][i:], 'MathJax.js')
            reveal['reveal_math_dep'] = self.reveal_math_dep % reveal
            reveal['reveal_math'] = self.reveal_math_option % mathjax
        else:
            reveal['reveal_math_dep'] = reveal['reveal_math'] = ''
            local_mathjax = None
        reveal['reveal_init'] = ''
        if hasattr(node, 'reveal'):
            # The reveal:: directive is present.
            for opt, val in node.reveal.items():
                if isinstance(val, bool):
                    val = repr(val).lower()
                elif isinstance(val, basestring):
                    try:
                        v = float(val)
                    except ValueError:
                        val = repr(val)
                        if val.startswith('u'):
                            val = val[1:]
                    else:
                        val = int(v)
                        if v != val:
                            val = v
                reveal['reveal_init'] += '        {}: {},\n'.format(opt, val)
        self.body_suffix.insert(0, '</div>\n</div>\n' +
                                self.reveal_ending_scripts % reveal)
        self.fragment.extend(self.body)  # self.fragment is the "naked" body
        self.html_body.extend(self.body_prefix[1:] + self.body_pre_docinfo
                              + self.docinfo + self.body
                              + self.body_suffix[:-1])
        assert not self.context, 'len(context) = %s' % len(self.context)
        # Download local copy of reveal.js and optionally MathJax.
        setup(self.reveal_dir, local_mathjax)

    def visit_section(self, node, *args, **kwargs):
        # Do not get here for title page section.
        # The title node is a child of the whole document.
        if hasattr(node, 'aside_section'):
            # Hack to get speaker notes aside sections.
            # There's probably a better way.
            self.body.append('\n' + self.starttag(node, 'aside'))
            return
        if self.close_section:
            # Close the extra vertical slide section tag.
            self.body.append('</section>\n')
            self.close_section = False

        self.section_level += 1
        if (self.section_level == 1 and any((isinstance(el, nodes.section) and
                                             not hasattr(el, 'aside_section'))
                                            for el in node.children)):
            # Has vertical slides, set reveal_data_attribs in visit_title.
            # Defer all section attributes until visit_title.
            tag = '<section>'
            self.close_section = True
        else:
            # No vertical slides, this is the only <section> tag.
            attribs = getattr(node, 'reveal_data_attribs', {})
            tag = self.starttag(node, 'section', **attribs)
        # Note that the attribs keys are not legal python symbols
        # as they contain dashes.  This does not seem to bother **...
        self.body.append('\n' + tag)

    def depart_section(self, node):
        if hasattr(node, 'aside_section'):
            self.body.append('</aside>\n')
            return
        self.section_level -= 1
        self.body.append('</section>\n')

    def visit_title(self, node):
        initlev = self.initial_header_level
        parent = node.parent
        is_doctitle = isinstance(parent, nodes.document)
        if self.close_section or is_doctitle:
            # If there are subsections add an extra <section> in order to
            # support vertical slides.
            # Also get here before the whole document title, since every
            # slide is a subsection of the whole document.
            # In every case, this <section> tag is the innermost one for the
            # slide, which is the one that should get reveal_data_attribs.
            # Note that the attribs keys are not legal python symbols
            # as the contain dashes.  This does not seem to bother **...
            attribs = getattr(parent, 'reveal_data_attribs', {})
            self.body.append('\n'+self.starttag(parent, 'section', **attribs))
            if is_doctitle:
                self.close_section = True
                # Handle document.titledata here.
                self.initial_header_level = 1
        if self.section_level > 1:
            # Vertical slides have same level headers as normal slides.
            self.initial_header_level -= 1
        html_baseclass.visit_title(self, node)
        self.initial_header_level = initlev

    def visit_subtitle(self, node):
        self.h3_subtitle = isinstance(node.parent, nodes.document)
        if self.h3_subtitle:
            # reveal.js demo makes presentation subtitle h3
            self.in_document_title = len(self.body)
            self.body.append(self.starttag(node, 'h3', '', CLASS='subtitle'))
        else:
            html_baseclass.visit_subtitle(self, node)

    def depart_subtitle(self, node):
        if self.h3_subtitle:
            self.body.append('</h3>\n')
            if self.in_document_title:
                self.subtitle = self.body[self.in_document_title:-1]
                self.in_document_title = 0
                self.body_pre_docinfo.extend(self.body)
                self.html_subtitle.extend(self.body)
                del self.body[:]
        else:
            html_baseclass.depart_subtitle(self, node)


def main():
    description = ('Generates reveal.js slideshow from reStructuredText '
                   'sources.  ' + default_description)
    writer = Writer()
    # Override settings to get a default set more consistent with
    # reveal.js slideshow.
    # The math_output and syntax_highlight switches are required.
    # The initial_header_level gets the section headers the level
    # the reveal.js demo expects.
    publish_cmdline(writer=writer, description=description,
                    settings_overrides={
                        'math_output': 'mathjax '+mathjax_default['mathjax'],
                        'syntax_highlight': 'none',
                        'initial_header_level': 2,
                        'xml_declaration': False,
                        'strip_comments': True,
                        'stylesheet_path': 'css/custom.css',
                        'embed_stylesheet': False})


if __name__ == '__main__':
    main()
