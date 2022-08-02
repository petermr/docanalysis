from pathlib import Path
import os
from lxml import etree as LXET
import logging

from docanalysis.file_lib import FileLib

logging.debug("loading xml_lib")


# make leafnodes and copy remaning content as XML
TERMINAL_COPY = {
    "abstract",
    "aff",
    "article-id",
    "article-categories",
    "author-notes",
    "caption",
    "contrib-group",
    "fig",
    "history",
    "issue",
    "journal_id",
    "journal-title-group",
    "kwd-group",
    "name",
    "notes",
    "p",
    "permissions",
    "person-group",
    "pub-date",
    "publisher",
    "ref",
    "table",
    "title",
    "title-group",
    "volume",
}


TERMINALS = [
    "inline-formula",
]

TITLE = "title"

IGNORE_CHILDREN = {
    "disp-formula",
}

HTML_TAGS = {
    "italic": "i",
    "p": "p",
    "sub": "sub",
    "sup": "sup",
    "tr": "tr",
}

H_TD = "td"
H_TR = "tr"
H_TH = "th"
LINK = "link"
UTF_8 = "UTF-8"
SCRIPT = "script"
STYLESHEET = "stylesheet"
TEXT_CSS = "text/css"
TEXT_JAVASCRIPT = "text/javascript"

H_HTML = "html"
H_BODY = "body"
H_TBODY = "tbody"
H_DIV = "div"
H_TABLE = "table"
H_THEAD = "thead"
H_HEAD = "head"
H_TITLE = "title"

RESULTS = "results"

SEC_TAGS = {
    "sec",
}

LINK_TAGS = {
    "xref",
}

SECTIONS = "sections"

HTML_NS = "HTML_NS"
MATHML_NS = "MATHML_NS"
SVG_NS = "SVG_NS"
XMLNS_NS = "XMLNS_NS"
XML_NS = "XML_NS"
XLINK_NS = "XLINK_NS"

XML_LANG = "{" + XML_NS + "}" + 'lang'

NS_MAP = {
    HTML_NS: "http://www.w3.org/1999/xhtml",
    MATHML_NS: "http://www.w3.org/1998/Math/MathML",
    SVG_NS: "http://www.w3.org/2000/svg",
    XLINK_NS: "http://www.w3.org/1999/xlink",
    XML_NS: "http://www.w3.org/XML/1998/namespace",
    XMLNS_NS: "http://www.w3.org/2000/xmlns/",
}

logger = logging.getLogger("xml_lib")
logger.setLevel(logging.WARNING)


class XmlLib:
    """ """

    def __init__(self, file=None, section_dir=SECTIONS):
        self.max_file_len = 30
        self.file = file
        self.parent_path = None
        self.root = None
        self.logger = logging.getLogger("xmllib")
        self.section_dir = section_dir
        self.section_path = None
#         self.logger.setLevel(logging.INFO)

    def read(self, file):
        """reads XML file , saves file, and parses to self.root

        :param file: 

        """
        if file is not None:
            self.file = file
            self.parent_path = Path(file).parent.absolute()
            self.root = XmlLib.parse_xml_file_to_root(file)

    def make_sections(self, section_dir):
        """recursively traverse XML tree and write files for each terminal element

        :param section_dir: 

        """
        self.section_dir = self.make_sections_path(section_dir)
        # indent = 0
        # filename = "1" + "_" + self.root.tag
        # self.logger.debug(" " * indent, filename)
        # subdir = os.path.join(self.section_dir, filename)
        # FileLib.force_mkdir(subdir)

        self.make_descendant_tree(self.root, self.section_dir)
        self.logger.info(
            f"wrote XML sections for {self.file} {self.section_dir}")

    @staticmethod
    def parse_xml_file_to_root(file):
        """read xml path and create root element

        :param file: 

        """
        file = str(file)  # if file is Path
        if not os.path.exists(file):
            raise IOError("path does not exist", file)
        xmlp = LXET.XMLParser(encoding=UTF_8)
        element_tree = LXET.parse(file, xmlp)
        root = element_tree.getroot()
        return root

    @staticmethod
    def parse_xml_string_to_root(xml):
        """read xml string and parse to root element

        :param xml: 

        """
        from io import StringIO
        tree = LXET.parse(StringIO(xml), LXET.XMLParser(ns_clean=True))
        return tree.getroot()

    def make_sections_path(self, section_dir):
        """

        :param section_dir: 

        """
        self.section_path = os.path.join(self.parent_path, section_dir)
        if not os.path.exists(self.section_path):
            FileLib.force_mkdir(self.section_path)
        return self.section_path

    def make_descendant_tree(self, elem, outdir):
        """

        :param elem: 
        :param outdir: 

        """

        self.logger.setLevel(logging.INFO)
        if elem.tag in TERMINALS:
            self.logger.debug("skipped ", elem.tag)
            return
        TERMINAL = "T_"
        IGNORE = "I_"
        children = list(elem)
        self.logger.debug(f"children> {len(children)} .. {self.logger.level}")
        isect = 0
        for child in children:
            if "ProcessingInstruction" in str(type(child)):
                # print("PI", child)
                continue
            if "Comment" in str(type(child)):
                continue
            flag = ""
            child_child_count = len(list(child))
            if child.tag in TERMINAL_COPY or child_child_count == 0:
                flag = TERMINAL
            elif child.tag in IGNORE_CHILDREN:
                flag = IGNORE

            title = child.tag
            if child.tag in SEC_TAGS:
                title = XmlLib.get_sec_title(child)

            if flag == IGNORE:
                title = flag + title
            filename = str(
                isect) + "_" + FileLib.punct2underscore(title).lower()[:self.max_file_len]

            if flag == TERMINAL:
                xml_string = LXET.tostring(child)
                filename1 = os.path.join(outdir, filename + '.xml')
                self.logger.setLevel(logging.INFO)
                self.logger.debug(f"writing dbg {filename1}")
                try:
                    with open(filename1, "wb") as f:
                        f.write(xml_string)
                except Exception:
                    print(f"cannot write {filename1}")
            else:
                subdir = os.path.join(outdir, filename)
                # creates empty dirx, may be bad idea
                FileLib.force_mkdir(subdir)
                if flag == "":
                    self.logger.debug(f">> {title} {child}")
                    self.make_descendant_tree(child, subdir)
            isect += 1

    @staticmethod
    def get_sec_title(sec):
        """get title of JATS section
        
        :sec: section (normally sec element

        :param sec: 

        """
        title = None
        for elem in list(sec):
            if elem.tag == TITLE:
                title = elem.text
                break

        if title is None:
            # don't know where the 'xml_file' comes from...
            if not hasattr(sec, "xml_file"):
                title = "UNKNOWN"
            else:
                title = "?_" + str(sec["xml_file"][:20])
        title = FileLib.punct2underscore(title)
        return title

    @staticmethod
    def remove_all(elem, xpath):
        """

        :param elem: 
        :param xpath: 

        """
        for el in elem.xpath(xpath):
            el.getparent().remove(el)

    @staticmethod
    def get_or_create_child(parent, tag):
        """

        :param parent: 
        :param tag: 

        """
        child = None
        if parent is not None:
            child = parent.find(tag)
            if child is None:
                child = LXET.SubElement(parent, tag)
        return child

    @classmethod
    def get_text(cls, node):
        """get text children as string

        :param node: 

        """
        return ''.join(node.itertext())

    @staticmethod
    def add_UTF8(html_root):
        """adds UTF8 declaration to root

        :param html_root: 

        """
        from lxml import etree as LXET
        root = html_root.get_or_create_child(html_root, "head")
        LXET.SubElement(root, "meta").attrib["charset"] = "UTF-8"

    # replace nodes with text
    @staticmethod
    def replace_nodes_with_text(data, xpath, replacement):
        """replace nodes with specific text

        :param data: 
        :param xpath: 
        :param replacement: 

        """
        print(data, xpath, replacement)
        tree = LXET.fromstring(data)
        for r in tree.xpath(xpath):
            print("r", r, replacement, r.tail)
            text = replacement
            if r.tail is not None:
                text += r.tail
            parent = r.getparent()
            if parent is not None:
                previous = r.getprevious()
                if previous is not None:
                    previous.tail = (previous.tail or '') + text
                else:
                    parent.text = (parent.text or '') + text
                parent.remove(r)
        return tree

    @classmethod
    def remove_all_tags(cls, xml_string):
        """remove all tags from text
        
        :xml_string: string to be flattened

        :param xml_string: 
        :returns: flattened string

        """
        tree = LXET.fromstring(xml_string.encode("utf-8"))
        strg = LXET.tostring(tree, encoding='utf8',
                             method='text').decode("utf-8")
        return strg

    @classmethod
    def xslt_transform(cls, data, xslt_file):
        """

        :param data: 
        :param xslt_file: 

        """
        xslt_root = LXET.parse(xslt_file)
        transform = LXET.XSLT(xslt_root)
        print("XSLT log", transform.error_log)
        result_tree = transform(LXET.fromstring(data))
        assert(result_tree is not None)
        root = result_tree.getroot()
        assert(root is not None)

        return root

    @classmethod
    def xslt_transform_tostring(cls, data, xslt_file):
        """

        :param data: 
        :param xslt_file: 

        """
        root = cls.xslt_transform(data, xslt_file)
        return LXET.tostring(root).decode("UTF-8") if root is not None else None


class HtmlElement:
    """to provide fluent HTML builder and parser"""
    pass


class DataTable:
    """<html xmlns="http://www.w3.org/1999/xhtml">
     <head charset="UTF-8">
      <title>ffml</title>
      <link rel="stylesheet" type="text/css" href="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/css/jquery.dataTables.css"/>
      <script src="http://ajax.aspnetcdn.com/ajax/jQuery/jquery-1.8.2.min.js" charset="UTF-8" type="text/javascript"> </script>
      <script src="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/jquery.dataTables.min.js" charset="UTF-8" type="text/javascript"> </script>
      <script charset="UTF-8" type="text/javascript">$(function() { $("#results").dataTable(); }) </script>
     </head>


    """

    def __init__(self, title, colheads=None, rowdata=None):
        """create dataTables
        optionally add column headings (list) and rows (list of conformant lists)

        :param title: of data_title (required)
        :param colheads:
        :param rowdata:

        """
        self.html = LXET.Element(H_HTML)
        self.head = None
        self.body = None
        self.create_head(title)
        self.create_table_thead_tbody()
        self.add_column_heads(colheads)
        self.add_rows(rowdata)
        self.head = None
        self.title = None
        self.title.text = None


    def create_head(self, title):
        """<title>ffml</title>
          <link rel="stylesheet" type="text/css" href="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/css/jquery.dataTables.css"/>
          <script src="http://ajax.aspnetcdn.com/ajax/jQuery/jquery-1.8.2.min.js" charset="UTF-8" type="text/javascript"> </script>
          <script src="http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/jquery.dataTables.min.js" charset="UTF-8" type="text/javascript"> </script>
          <script charset="UTF-8" type="text/javascript">$(function() { $("#results").dataTable(); }) </script>

        :param title: 

        """

        self.head = LXET.SubElement(self.html, H_HEAD)
        self.title = LXET.SubElement(self.head, H_TITLE)
        self.title.text = title

        link = LXET.SubElement(self.head, LINK)
        link.attrib["rel"] = STYLESHEET
        link.attrib["type"] = TEXT_CSS
        link.attrib["href"] = "http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/css/jquery.dataTables.css"
        link.text = '.'  # messy, to stop formatter using "/>" which dataTables doesn't like

        script = LXET.SubElement(self.head, SCRIPT)
        script.attrib["src"] = "http://ajax.aspnetcdn.com/ajax/jQuery/jquery-1.8.2.min.js"
        script.attrib["charset"] = UTF_8
        script.attrib["type"] = TEXT_JAVASCRIPT
        script.text = '.'  # messy, to stop formatter using "/>" which dataTables doesn't like

        script = LXET.SubElement(self.head, SCRIPT)
        script.attrib["src"] = "http://ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.4/jquery.dataTables.min.js"
        script.attrib["charset"] = UTF_8
        script.attrib["type"] = TEXT_JAVASCRIPT
        script.text = "."  # messy, to stop formatter using "/>" which dataTables doesn't like

        script = LXET.SubElement(self.head, SCRIPT)
        script.attrib["charset"] = UTF_8
        script.attrib["type"] = TEXT_JAVASCRIPT
        script.text = "$(function() { $(\"#results\").dataTable(); }) "

    def create_table_thead_tbody(self):
        """<body>
              <div class="bs-example table-responsive">
               <table class="table table-striped table-bordered table-hover" id="results">
        <thead>
         <tr>
          <th>articles</th>
          <th>bibliography</th>
          <th>dic:country</th>
          <th>word:frequencies</th>
         </tr>
        </thead>


        """

        self.body = LXET.SubElement(self.html, H_BODY)
        self.div = LXET.SubElement(self.body, H_DIV)
        self.div.attrib["class"] = "bs-example table-responsive"
        self.table = LXET.SubElement(self.div, H_TABLE)
        self.table.attrib["class"] = "table table-striped table-bordered table-hover"
        self.table.attrib["id"] = RESULTS
        self.thead = LXET.SubElement(self.table, H_THEAD)
        self.tbody = LXET.SubElement(self.table, H_TBODY)

    def add_column_heads(self, colheads):
        """

        :param colheads: 

        """
        if colheads is not None:
            self.thead_tr = LXET.SubElement(self.thead, H_TR)
            for colhead in colheads:
                th = LXET.SubElement(self.thead_tr, H_TH)
                th.text = str(colhead)

    def add_rows(self, rowdata):
        """

        :param rowdata: 

        """
        if rowdata is not None:
            for row in rowdata:
                self.add_row_old(row)

    def add_row_old(self, row: [str]):
        """creates new <tr> in <tbody>
        creates <td> child elements of row containing string values

        :param row: list of str
        :param row: [str]: 

        """
        if row is not None:
            tr = LXET.SubElement(self.tbody, H_TR)
            for val in row:
                td = LXET.SubElement(tr, H_TD)
                td.text = val
                # print("td", td.text)

    def make_row(self):
        """:return: row element"""
        return LXET.SubElement(self.tbody, H_TR)

    def append_contained_text(self, parent, tag, text):
        """create element <tag> and add text child

        :param parent: 
        :param tag: 
        :param text: 

        """
        subelem = LXET.SubElement(parent, tag)
        subelem.text = text
        return subelem

    def write_full_data_tables(self, output_dir: str) -> None:
        """

        :param output_dir: str: 

        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        data_table_file = os.path.join(output_dir, "full_data_table.html")
        with open(data_table_file, "w") as f:
            text = bytes.decode(LXET.tostring(self.html))
            f.write(text)
            print("WROTE", data_table_file)

    def __str__(self):
        # s = self.html.text
        # print("s", s)
        # return s
        # ic("ichtml", self.html)
        htmltext = LXET.tostring(self.html)
        print("SELF", htmltext)
        return htmltext


class Web:
    """ """
    def __init__(self):
        import tkinter as tk
        root = tk.Tk()
        site = "http://google.com"
        self.display_html(root, site)
        root.mainloop()

    @classmethod
    def display_html(cls, master, site):
        """

        :param master: 
        :param site: 

        """
        import tkinterweb
        frame = tkinterweb.HtmlFrame(master)
        frame.load_website(site)
        frame.pack(fill="both", expand=True)

    @classmethod
    def tkinterweb_demo(cls):
        """ """
        from tkinterweb import Demo
        Demo()


def main():
    """ """

    XmlLib().test_recurse_sections()  # recursively list sections

#    test_data_table()
#    test_xml()

#    web = Web()
#    Web.tkinterweb_demo()


def test_xml():
    """ """
    xml_string = "<a>foo <b>and</b> with <d/> bar</a>"
    print(XmlLib.remove_all_tags(xml_string))


def test_data_table():
    """ """
    import pprint
    data_table = DataTable("test")
    data_table.add_column_heads(["a", "b", "c"])
    data_table.add_row_old(["a1", "b1", "c1"])
    data_table.add_row_old(["a2", "b2", "c2"])
    data_table.add_row_old(["a3", "b3", "c3"])
    data_table.add_row_old(["a4", "b4", "c4"])
    html = LXET.tostring(data_table.html).decode("UTF-8")
    HOME = os.path.expanduser("~")
    with open(os.path.join(HOME, "junk_html.html"), "w") as f:
        f.write(html)
    pprint.pprint(html)


if __name__ == "__main__":
    print("running file_lib main")
    main()
else:
    #    print("running file_lib main anyway")
    #    main()
    pass

# Credits: Peter Murray-Rust, py4ami (https://github.com/petermr/pyami/blob/main/py4ami/file_lib.py)