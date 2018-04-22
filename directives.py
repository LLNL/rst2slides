import os.path
from glob import glob

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.transforms import Transform
from docutils.parsers.rst.directives.body import CodeBlock

# reveal.js section attributes:
#   id="Section title"
#   data-markdown
#   data-background-color="#rrggbb"  or  rgba()  or  hsl()
#   data-background-image="URL"
#     data-background-repeat="no-repeat", data-background-size="cover"
#     data-background-position='center'
#   data-transition="slide"
#     data-transition-speed="default"   default/fast/slow
#   data-state="myclass"  adds myclass to section element when open
#   data-state="customevent"  fires javascript listener for 'customevent'
#   data-notes="instead of aside"
#   data-timing=120   for speaker clock
#
# reveal.js tag classes:
#   fragment  -plus options- grow shrink fade-out fade-up current-visible
#   highlight-red highlight-blue highlight-green
#
# reveal.js queries:
#   ?transition=xxx#/transitions  (none, fade, slide, convex, concave, zoom)#
#
# highlight.js wants <code class="hljs <language>">
#   add data-trim attribute to remove surrounding whitespace
#
# Reveal.configure({
#   keyboard: {
#     13: 'next', // go to the next slide when the ENTER key is pressed
#     27: function() {}, // do something custom when ESC is pressed
#     32: null // don't do anything when SPACE is pressed
#           (i.e. disable a reveal.js default binding)
#   }
# });
#
#   Reveal.initialize options (or Reveal.configure after initialization):
# controls: true    control arrows visible
# controlsTutorial: true   arrows bounce on first encounter
# controlsLayout: 'bottom-right'   or 'edges'
# controlsBackArrows: 'faded'   or 'hidden' or 'visible'
# progress: bool    progress bar
# defaultTiming: 120   two minutes per slide
# slideNumber: false   display page number
# history: false   push slide changes to browser history
# keyboard: true   enable keyboard navigation shortcuts
# overview: true   enable slide overview mode
# center: true   vertically center slides
# touch: true   enable touch navigation
# loop: false   loop the presentation
# rtl: false   right-to-left presentation direction
# shuffle: false    randomize slide order each time presentation loads
# fragments: true    global fragments switch
# embedded: false    whether presentaion running o nlimited part of screen
# help: true    pressing ? shows help overlay
# showNotes: false   whether speaker notes shown to all viewers
# autoPlayMedia: null   only if data-autoplay present, bool to override
# autoSlide: 0   milliseconds (0 disables), data-autoslide for per slide
# autoSlideStoppable: true
# autoSlideMethod: Reveal.navigateNext
# mouseWheel: false   enable mouse wheel navigation
# hideAddressBar: true   hide address bar on mobile devices
# previewLinks: false   preview links in overlay, or data-preview-link per link
# transition: 'slide'   none/fade/slide/convex/concave/zoom
# transitionSpeed: 'default'   default/fast/slow
# backgroundTransition: 'fade'    none/fade/slide/convex/concave/zoom
# viewDistance: 3   number of slides away from current that are visible
# parallaxBackGroundImage: ''   URL
# parallaxBackgroundSize: ''    CSS syntax like "2100px 900px"
# parallaxBackgroundHorizontal: null   (and Vertical) in pixels, 0 disables
# display: 'block'   display mode used to show slides
#
#   Size options for Reveal.initialize only?
# width: 960
# height: 700
# margin: 0.1
# minScale: 0.2
# maxScale: 1.5
#   Use width=height=100%, margin=0, minScale=maxScale=1 to disable
#
# math: { mathjax: URL, config: 'TeX-AMS_HTML-full' }
#
#   dependencies require head.js to be loaded before reveal.js!
# dependencies: [
# 		// Cross-browser shim that fully implements classList
#       // - https://github.com/eligrey/classList.js/
# 		{ src: 'lib/js/classList.js', condition: function()
#              { return !document.body.classList; } },
#
# 		// Interpret Markdown in <section> elements
# 		{ src: 'plugin/markdown/marked.js', condition: function()
#              { return !!document.querySelector( '[data-markdown]' ); } },
# 		{ src: 'plugin/markdown/markdown.js', condition: function()
#              { return !!document.querySelector( '[data-markdown]' ); } },
#
# 		// Syntax highlight for <code> elements
# 		{ src: 'plugin/highlight/highlight.js', async: true, callback:
#              function() { hljs.initHighlightingOnLoad(); } },
#
# 		// Zoom in and out with Alt+click
# 		{ src: 'plugin/zoom-js/zoom.js', async: true },
#
# 		// Speaker notes
# 		{ src: 'plugin/notes/notes.js', async: true },
#
# 		// MathJax
# 		{ src: 'plugin/math/math.js', async: true }
# ]
#
# multiplex: --> audience clients controlled by presenter master presentation
#
# Speaker notes use <aside class="notes">...</aside>
#    --> need aside directive
#    short notes with data-notes section attribute


def choice_validator(values):
    """Wrapper around directives.choice to make it work properly."""
    def validate_choice(argument):
        return directives.choice(argument, values)
    return validate_choice


def validate_comma_separated_list(argument):
    """Convert argument to a list."""
    if not isinstance(argument, list):
        argument = [argument]
    last = argument.pop()
    items = [i.strip(u' \t\n') for i in last.split(u',') if i.strip(u' \t\n')]
    argument.extend(items)
    return argument


def validate_boolean(argument):
    """Return a boolean, recognizing yes/no, true/false, 0/1."""
    try:
        return _booleans[argument.strip().lower()]
    except KeyError:
        raise LookupError('unknown boolean value: "%s"' % argument)


def validate_ternary(argument):
    """If boolean yes/no, true/false, 0/1, convert, else unchanged."""
    try:
        return _booleans[argument.strip().lower()]
    except KeyError:
        return argument


_booleans = {'0': False, '1': True, 'no': False, 'yes': True,
             'false': False, 'true': True}


class VideoDirective(Directive):
    """ Restructured text extension for inserting videos """
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'align': choice_validator(['center', 'left', 'right']),
        'width': directives.unchanged_required,
        # 'height': directives.unchanged,
        'autoplay': directives.flag,
        'loop': directives.flag,
        'controls': validate_boolean}

    def run(self):
        href = directives.uri(self.arguments[0])
        codec = href.rsplit('.', 1)[-1].lower()
        if codec not in ['mp4', 'webm', 'ogg', 'ogv']:
            self.error("Error in directive: the video must be in .mp4, .webm, "
                       ".ogg, or .ogv format.")
        args = dict(align='center', width='50%', controls='controls',
                    autoplay='', loop='', href=href, codec=codec)
        opts = self.options
        for opt, value in opts.items():
            if opt in ('controls', 'loop', 'autoplay'):
                opts[opt] = '' if value or value is None else opt
            else:
                opts[opt] = value.strip()
        args.update(opts)
        return [nodes.raw('video', VIDEO_TAG % args, format='html')]


# Is the outer div really necessary?  Why not add class to video tag?
# Also, should style attribute in video be in css instead?
VIDEO_TAG = """\
<div class="align-%(align)s">
    <video style="text-align:%(align)s; float:%(align)s"
           width="%(width)s" %(autoplay)s %(loop)s %(controls)s>
        <source src="%(href)s" type="video/%(codec)s">
        Your browser does not support the video tag.
    </video>
</div>
"""


class ConfigureDirective(Directive):
    """Process configuration settings inside the document itself.
    """
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    has_content = False
    # Options are a subset of possible configuration settings.
    # Only settings which are unused until the writer can have any effect,
    # as obviously the parsing has already begun.
    # Options irrelevant to HTML slides are also omitted.
    option_spec = {
        'title': directives.unchanged_required,
        'attribution': choice_validator(['dash', 'parentheses', 'parens',
                                         'none']),
        'template': directives.uri,
        'stylesheet': validate_comma_separated_list,  # URLs
        'stylesheet_path': validate_comma_separated_list,  # paths
        'stylesheet_dirs': validate_comma_separated_list,
        'embed_stylesheet': validate_boolean,
        'initial_header_level': choice_validator('1 2 3 4 5 6'.split()),
        'compact_lists': validate_boolean,
        'compact_field_lists': validate_boolean,
        'table_style': directives.class_option,
        'footnote_references': choice_validator(['brackets', 'superscript']),
        'smart_quotes': validate_boolean,
        'strip_comments': validate_boolean,
        'xml_declaration': validate_boolean,
        'cloak_email_addresses': validate_boolean
        }

    def run(self):
        document = self.state_machine.document
        settings = document.settings
        for setting, value in self.options.items():
            if setting == 'title':
                document['title'] = value
            setattr(settings, setting, value)
        return []


class RevealDirective(Directive):
    """Reveal.js configuration settings inside the document itself."""
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    has_content = False
    # See http://github.com/hakimel/reveal.js/#configure
    option_spec = {
        'controls': validate_boolean,  # True
        'controlsTutorial': validate_boolean,  # True
        'controlsLayout': choice_validator(['bottom-right', 'edge']),
        'controlsBackArrows': choice_validator(['faded', 'hidden']),
        'progress': validate_boolean,  # True
        'defaultTiming': directives.nonnegative_int,  # 120
        'slideNumber': validate_boolean,  # False
        'history': validate_boolean,  # False
        'keyboard': validate_boolean,  # True
        'overview': validate_boolean,  # True
        'center': validate_boolean,  # True
        'touch': validate_boolean,  # True
        'loop': validate_boolean,  # False
        'rtl': validate_boolean,  # False
        'shuffle': validate_boolean,  # False
        'fragments': validate_boolean,  # True
        'embedded': validate_boolean,  # False
        'help': validate_boolean,  # True
        'showNotes': validate_boolean,  # False
        'autoPlayMedia': validate_ternary,  # 'null', True, False
        'autoSlide': directives.nonnegative_int,  # 0
        'autoSlideStoppable': validate_boolean,  # True
        'autoSlideMethod': directives.unchanged_required,  # (js function)
        'mouseWheel': validate_boolean,  # False
        'hideAddressBar': validate_boolean,  # True
        'previewLinks': validate_boolean,  # False
        'transition': choice_validator(['slide', 'none', 'fade', 'convex',
                                        'concave', 'zoom']),
        'transitionSpeed': choice_validator(['default', 'fast', 'slow']),
        'backgroundTransition': choice_validator([
            'slide', 'none', 'fade', 'convex', 'concave', 'zoom']),
        'viewDistance': directives.nonnegative_int,  # 3
        'parallaxBackgroundImage': directives.uri,
        'parallaxBackgroundSize': directives.unchanged,  # '' CSS "WWpx HHpx"
        'parallaxBackgroundHorizontal': directives.unchanged_required,
        'parallaxBackgroundVertical': directives.unchanged_required,
        'display': directives.unchanged_required,  # 'block'
        'width': directives.unchanged_required,  # 960
        'height': directives.unchanged_required,  # 700
        'margin': directives.unchanged_required,  # 0.1
        'minScale': directives.unchanged_required,  # 0.2
        'maxScale': directives.unchanged_required,  # 1.5
        # following pair added for math.js plugin initialization
        'mathjax': directives.uri,
        'mathjaxConfig': directives.unchanged_required,
        # following added for reveal.js theme and highlight.js style
        'theme': directives.unchanged_required,
        'highlightStyle': directives.unchanged_required,
        'revealPath': directives.unchanged_required
        }

    def run(self):
        document = self.state_machine.document
        document.reveal = opts = self.options
        document.mathjax = mathjax_default.copy()
        document.reveal_dir = path = opts.pop('revealPath', REVEAL_DIR)
        mathjax = glob(os.path.join(path, 'MathJax*'))
        if mathjax:
            mathjax.sort()
            document.mathjax['mathjax'] = mathjax[-1]
        for key, nm in [('mathjax', 'mathjax'), ('mathjaxConfig', 'config')]:
            v = opts.pop(key, None)
            if v:
                document.mathjax[nm] = v
        theme = opts.pop('theme', '').strip()
        if theme:
            document.theme = theme
        style = opts.pop('highlightStyle', '').strip()
        if style:
            document.hljs = style
        return []


mathjax_default = {
    'mathjax': 'https://cdnjs.cloudflare.com/ajax/libs/'
               'mathjax/2.7.0/MathJax.js',
    'config': 'TeX-AMS_HTML-full'}
REVEAL_DIR = 'ui'  # overwritten to make consistent


class BackgroundDirective(Directive):
    """Handle reveal.js data-background-* attributes in section tag."""
    # Directives are processed when the doctree is being built.
    # The background directive needs to change the state of its parent
    # (or formal grandparent in the case of subtitles) to put the
    # data-background-image or data-background-color attributes in the
    # containing section tag.  We defer this action until the first pass
    # doctree construction is complete and Transforms are being processed.
    # Thus BackgroundDirective pushes a pending node into the doctree
    # that holds the directive arguments and options, and BackgroundTransform
    # later adds the required attributes to the parent section.
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'size': directives.unchanged_required,
        'position': directives.unchanged_required,
        'repeat': validate_boolean}

    image_extensions = 'bmp', 'jpg', 'jpeg', 'png', 'gif', 'svg'

    def run(self):
        bg = self.arguments[0].strip()  # color or image URL
        details = dict(directive=self.name)
        ext = bg.rsplit('.', 1)
        if len(ext) > 1 and ext[-1].lower() in self.image_extensions:
            details.update(image=bg, **self.options)
        else:  # argument does not look like an image URL, assume a color
            if self.options:
                self.error("color background directive accepts no options")
            details.update(color=bg)
        pending = nodes.pending(BackgroundAttribute, details, self.block_text)
        self.state_machine.document.note_pending(pending)
        return [pending]


class BackgroundAttribute(Transform):
    """Find section node for data-background-* reveal.js attributes."""
    # This must run after the docutils.transforms.frontmatter
    # transforms which have priorities 320 (DocTitle), 350 (SectionSubTitle),
    # and 340 (DocInfo).  These three classes have extensive docstrings,
    # explaining what they do.  In a nutshell, they remove the nodes.section
    # containing the document title and subtitle, leaving the pending node
    # created by BackgroundDirective a child of the nodes.document.
    default_priority = 410

    def apply(self):
        pending = self.startnode
        pdg = pending.details.get
        color, image = pdg('color'), pdg('image')
        if image:
            atts = {'data-background-image': image}
            size, pos, repeat = pdg('size'), pdg('position'), pdg('repeat')
            if repeat:  # default no-repeat
                atts.update({'data-background-repeat': 'repeat'})
            if size:  # default cover
                atts.update({'data-background-size': size.strip().lower()})
            if pos:  # default center
                atts.update({'data-background-position': pos.strip().lower()})
        elif color:
            atts = {'data-background-color': color}
        else:
            pending.replace_self(
                self.document.reporter.error(
                    'Missing color or href for background directive',
                    nodes.literal_block(pending.rawsource, pending.rawsource),
                    line=pending.line))
            return
        parent = pending.parent
        parent.remove(pending)
        attribs = getattr(parent, 'reveal_data_attribs', None)
        if attribs is None:
            parent.reveal_data_attribs = atts
        else:
            attribs.update(atts)


class TransitionDirective(Directive):
    """Handle reveal.js data-transition attribute in next section tag."""
    required_arguments = 1
    optional_arguments = 0
    styles = 'none', 'fade', 'slide', 'convex', 'concave', 'zoom'
    option_spec = {'speed': choice_validator(['default', 'fast', 'slow'])}

    def run(self):
        style = self.arguments[0].strip().lower()
        if style not in self.styles:
            self.error("unrecognized reveal.js transition %s".format(style))
        details = dict(directive=self.name, style=style)
        details.update(self.options)
        pending = nodes.pending(TransitionAttribute, details, self.block_text)
        self.state_machine.document.note_pending(pending)
        return [pending]


class TransitionAttribute(Transform):
    """Find section node for data-transition-* reveal.js attributes."""
    default_priority = 411  # soon after BackgroundAttribute

    def apply(self):
        pending = self.startnode
        parent, child, nextsec = pending.parent, pending, None
        Section = (nodes.section, nodes.document)
        if isinstance(parent, Section):
            # Find the next section.  If this is the last subsection,
            # the next section will be the next sibling of the parent.
            while parent:
                for index in range(parent.index(child) + 1, len(parent)):
                    nextsec = parent[index]
                    if isinstance(nextsec, nodes.section):
                        parent = None
                        break
                else:
                    nextsec = None
                    if child is not pending:
                        break
                    child = parent
                    parent = parent.parent
                    if not isinstance(parent, Section):
                        break
        if nextsec is None:
            pending.replace_self(
                self.document.reporter.error(
                    'No find following section for transition directive',
                    nodes.literal_block(pending.rawsource, pending.rawsource),
                    line=pending.line))
            return
        pending.parent.remove(pending)
        atts = {'data-transition': pending.details.get('style')}
        speed = pending.details.get('speed')
        if speed:
            atts.update({'data-transition-speed': speed})
        attribs = getattr(nextsec, 'reveal_data_attribs', None)
        if attribs is None:
            nextsec.reveal_data_attribs = atts
        else:
            attribs.update(atts)


class TitlepageDirective(Directive):
    """Get author, date, etc. for presentation title page."""
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
        'author': directives.unchanged_required,
        'authors': directives.unchanged_required,
        'date': directives.unchanged_required,
        'organization': directives.unchanged_required,
        'event': directives.unchanged_required,
        'auspices': directives.unchanged_required}

    def run(self):
        document = self.state_machine.document
        opts = self.options
        a = opts.pop('author', None)
        if a is not None:
            opts['authors'] = a
        document.titledata = self.options
        return []


class RevealStateDirective(Directive):
    """Collect reveal.js data-state classes for current slide."""
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    # options for speaker view timing and short note
    option_spec = {'timing': int,
                   'notes': directives.unchanged_required}

    def run(self):
        details = self.options
        args = self.arguments
        if args:
            try:
                details.update(class_=directives.class_option(args[0]))
            except ValueError:
                raise self.error(
                    'Invalid class attribute value for "%s" directive: "%s".'
                    % (self.name, args[0]))
        pending = nodes.pending(RevealData, details, self.block_text)
        self.state_machine.document.note_pending(pending)
        return [pending]


class RevealData(Transform):
    """Find section node for data-state, data-timing reveal.js attributes."""
    default_priority = 415  # soon after BackgroundAttribute
    alias = {'class_': 'data-state', 'timing': 'data-timing',
             'notes': 'data-notes'}

    def apply(self):
        pending = self.startnode
        atts = [(k, pending.details.get(k)) for k in self.alias]
        atts = {self.alias[k]: value for k, value in atts if value}
        parent = pending.parent
        parent.remove(pending)
        attribs = getattr(parent, 'reveal_data_attribs', None)
        if attribs is None:
            parent.reveal_data_attribs = atts
        else:
            if 'data-state' in atts and 'data-state' in attribs:
                # Merge class lists
                clist = atts.pop('data-state')  # already a list
                existing = set(attribs.pop('data-state').split())
                clist = ' '.join(c for c in clist if c not in existing)
                if clist:
                    attribs['data-state'] += ' ' + clist
            attribs.update(atts)


class AsideDirective(Directive):
    """Collect reveal.js data-state classes for current slide."""
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    has_content = True

    def run(self):
        if not self.content:
            return []
        args = self.arguments
        if args:
            try:
                classes = directives.class_option(args[0])
            except ValueError:
                raise self.error(
                    'Invalid class attribute value for "%s" directive: "%s".'
                    % (self.name, args[0]))
        else:
            classes = None
        # Warning: An aside:: directive on the title page can badly damage
        # the entire document, as this section will be removed and its
        # contents reinterpreted in that case.
        node = nodes.section()
        self.state.nested_parse(self.content, self.content_offset, node)
        node.aside_section = True  # Hack to convert section to aside.
        if classes:
            node['classes'].extend(classes)
        return [node]


class HLjsCodeBlock(CodeBlock):
    """Parse code:: directive for highlight.js in reveal.js."""
    optional_arguments = 1
    option_spec = {'class': directives.class_option,
                   'name': directives.unchanged,
                   'noescape': directives.flag,
                   'trim': directives.flag
                  }
    has_content = True

    def run(self):
        self.state.document.settings.syntax_highlight = 'none'
        trim = self.options.pop('trim', Ellipsis)
        noescape = self.options.pop('noescape', Ellipsis)
        nodes = super(HLjsCodeBlock, self).run()
        # reveal.js highlight example has data-trim, data-noescape attributes
        # with no values, but HTMLTranslator.starttag does not support this.
        if trim is not Ellipsis:
            nodes[0].attributes['data-trim'] = 'true'
        if noescape is not Ellipsis:
            nodes[0].attributes['data-noescape'] = 'true'
        return nodes
