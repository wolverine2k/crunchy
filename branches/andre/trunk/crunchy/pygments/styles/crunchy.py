# -*- coding: utf-8 -*-
"""
    pygments.styles.crunchy
    ~~~~~~~~~~~~~~~~~~~~~~~

    The default Crunchy Style
"""

from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic, Whitespace


class CrunchyStyle(Style):
    """
    The Crunchy default Style
    """

    # work in progress...

    background_color = "#eeeeec"
    default_style = ""

    styles = {
        Whitespace:                "#bbbbbb",        # class: 'w',
        Error:                     "border:#FF0000", # 'err',

        Comment:                   "italic #555753",
        Comment.Preproc:           "noitalic #BC7A00",

        Keyword:                   "bold #204a87",
        Keyword.Pseudo:            "nobold",
        Keyword.Type:              "nobold #5c3566",

        Operator:                  "bold #ce5c00",
        Operator.Word:             "bold #ce5c00",

        Name.Builtin:              "#204a87",
        Name.Function:             "#0000FF",
        Name.Class:                "bold #0000FF",
        Name.Namespace:            "bold #0000FF",
        Name.Exception:            "bold #D2413A",
        Name.Variable:             "#19177C",
        Name.Constant:             "#880000",
        Name.Label:                "#A0A000",
        Name.Entity:               "bold #999999",
        Name.Attribute:            "#7D9029",
        Name.Tag:                  "bold #204a87",
        Name.Decorator:            "#AA22FF",

        String:                    "#4e9a06",
        String.Doc:                "italic",
        String.Interpol:           "bold #BB6688",
        String.Escape:             "bold #BB6622",
        String.Regex:              "#BB6688",
        #String.Symbol:             "#B8860B",
        String.Symbol:             "#19177C",
        String.Other:              "#008000",
        Number:                    "#5c3566",

        Generic.Heading:           "bold #000080",
        Generic.Subheading:        "bold #800080",
        Generic.Deleted:           "#A00000",
        Generic.Inserted:          "#00A000",
        Generic.Error:             "#FF0000",
        Generic.Emph:              "italic",
        Generic.Strong:            "bold",
        Generic.Prompt:            "bold #000080",
        Generic.Output:            "#888",
        Generic.Traceback:         "#04D",
    }