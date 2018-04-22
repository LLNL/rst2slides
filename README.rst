reStructuredText to reveal.js
=============================

Rst2slides is a docutils writer to convert rst source into a reveal.js slide
show.  It is a mashup of several previous efforts, with some original
ideas thrown into the mix.  Sources:

* git://repo.or.cz/docutils.git (the s5_html writer in docutils)
* http://bitbucket.org/ezio_melotti/rst2reveal by Ezio Melotti
* http://bitbucket.org/vitay/rst2reveal (or http://github.com/vitay/rst2reveal)
  by Julien Vitay
* http://github.com/mgaitan/charla__doc__ by Martin Gaitan

In a nutshell, each major section of your rst document becomes one
slide.  Top level subsections within each section become sub-slides.

Reveal.js presents top level slides as you (the presenter) hit the
left or right arrow keys; you get to subslides by hitting the down
arrow key (or up arrow to return to the previous sub-slide).  Spacebar
or page down takes you to the next slide or sub-slide; page up is a
"back button".  Reveal.js also goes to fullscreen when you hit the
f-key, and will blank the screen when you hit the period or b-key
(toggling back on with a second press).  Alt-click toggles a zoom
operation around the mouse location.  Finally, the o-key takes you to
and overview mode to rapidly page through the presentation, and the
s-key pops up a speaker display in a separate window.  Reveal.js
supports MathJax and highlight.js source code syntax highlighting.
You can choose from a half dozen themes, and supply css stylesheets of
your own to customize more extensively.

The docutils math directive or role will use MathJax, and code syntax
highlighting will use highlight.js, per the reveal.js recommendations.

Rst2slides provides several new docutils directives:

reveal
   reveal.js options, see http://github.com/hakimel/reveal.js/#configure

   In addition to all the reveal.js initializer options, accepts ``mathjax``,
   ``mathjaxConfig`` for local MathJax path or URL and options, ``theme``
   for the reveal.js theme, ``highlightStyle`` for the highligh.js style,
   and ``revealPath`` for reveal.js path or URL (``ui`` by default).

configure
   Docutils configuration options, including stylesheet_path, attribution,
   table_style, strip_comments and others.

   Several docutils configuration option defaults have been modified for
   consistency with reveal.js.

video
   Create html ``<video>`` tag, similar to image directive, with
   ``width``, ``align``, ``autoplay``, ``loop``, and ``controls`` options.

background
   Argument is html color or image URL (recognized by .jpg, .jpeg, .png, .svg,
   .bmp, or .gif extension) to specify background to be used for current
   slide only.  Accepts ``size``, ``position``, and ``repeat`` CSS options.

transition
   Argument is revel.js transition, one of ``none``, ``fade``, ``slide``,
   ``convex``, ``concave``, or ``zoom``, to specify the transition from
   the current slide to the next slide only.  The reveal directive accepts
   a ``transition`` option for unspecified transitions; its default has
   been changed from the reveal.js ``slide`` default to ``fade``.  Accepts
   ``speed`` option (one of ``default``, ``fast``, or ``slow``).

reveal-state
   Arguments are CSS classes for the reveal.js ``data-state`` attribute
   for the current slide.  Accepts ``timing`` and ``notes`` options to
   set reveal.js ``data-timing`` and ``data-notes`` attributes.

aside
   Content placed in an html ``<aside>`` tag, similar to the docutils
   container directive.  Arguments are CSS classes.  In particular, use
   the ``notes`` class to generate reveal.js speaker notes which appear
   only in the reveal.js speaker view of the presentation.

code
   The docutils code directive has been modified for highlight.js syntax
   highlighting.  Any argument is the syntax language (although highlight.js
   will probably guess correctly without any help).  The line-number option
   has been removed, since highlight.js does not support it, and ``trim``
   and ``noescape`` options have been added for those reveal.js features.

Also, rst2slides will find an optional ``css/custom.css`` file if you
do not specify a stylesheet_path in the configure options.

After preparing your presentation.rst file, you convert it to html with::

  python -m rst2slides presentation.rst presentation.html

You can download a local copy of reveal.js and optionally MathJax with::

  python -m rst2slides.download

This will happen automatically the first time you run rst2slides, unless
you have a reveal directive ``revealPath`` option the points to another
location.
