from abc import ABC
from pathlib import Path
import logging
from lxml import etree as LXET

from docanalysis.xml_lib import XmlLib


class AMIAbsSection(ABC):
    """ """
    logger = logging.getLogger("ami_abs_section")

    SECTIONS = "sections"

    def __init__(self) -> None:
        pass

    
    @classmethod
    def make_xml_sections(cls, file, outdir: str, force: bool) -> None:
        """make sections

        :param file: 
        :param outdir: str: 
        :param force: bool: 

        """
        if file is None or outdir is None:
            return None
        path = Path(file)
        if not path.exists():
            cls.logger.warning(f"file {file} does not exist")
            return
        #        sections = Path(self.dirx)
        if force or not Path(outdir).exists():
            cls.logger.warning(f"Making sections in {str(path)}")
            xml_libx = XmlLib()
            xml_libx.logger.setLevel(logging.DEBUG)
            xml_libx.read(file)
            xml_libx.make_sections(outdir)


class AMIFigure(AMIAbsSection):
    """holds data on figure captions and hopefully later pointers to pdfimages
    
    Figures are a mess in JATS. They can be held in different places and often not linked
    to the bitmap. This class will include heuristics for uniting and standardising this.
    
    JATS encoding depends on the publisher. Typically:
    <fig xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:mml="http://www.w3.org/1998/Math/MathML" id="F6"
         fig-type="figure" orientation="portrait" position="float">
      <label>Fig. 6</label>
      <caption>
        <title>XPS core spectra comparison for aged baseline and SEB-3 electrodes.</title>
        <p>The graphite and NCM622 electrodes are taken from the baseline cell after 956 cycles and
            the SEB-3 cell after 4021 cycles.</p>
      </caption>
      <graphic xlink:href="aay7633-F6"/>
    </fig>'
    
    There are sometimes 2 or more <p> as children of caption.


    """

    # JATS tags
    LABEL = "label_xml"
    CAPTION = "caption"
    P = "p"
    TITLE = "title"

    def __init__(self):
        super().__init__()
        self.root = None
        self.root_str = None
        self.label_xml = None
        self.label_text = None
        self.caption = None
        self.caption_p = None
        self.p_text = None
        self.caption_title = None
        self.title_text = None

    @classmethod
    def create_from_jats(cls, xml_path):
        """

        :param xml_path: 

        """
        ami_figure = AMIFigure()
        ami_figure.root = XmlLib.parse_xml_file_to_root(str(xml_path))
        ami_figure.add_figure_structure()
        return ami_figure

    def add_figure_structure(self):
        """creates label, caption, title, test(p) from JATS xml"""
        self.root_str = LXET.tostring(self.root)
        self.label_xml = XmlLib.get_or_create_child(self.root, self.LABEL)
        self.label_text = XmlLib.get_text(self.label_xml)
        self.caption = XmlLib.get_or_create_child(self.root, self.CAPTION)
        self.caption_p = XmlLib.get_or_create_child(self.caption, self.P)
        self.p_text = XmlLib.get_text(self.caption_p)
        self.caption_title = XmlLib.get_or_create_child(self.caption, self.TITLE)
        self.title_text = XmlLib.get_text(self.caption_title)

    def get_xml_str(self):
        """ """
        return LXET.tostring(self.root)

    def __str__(self):
        s = f" --- {self.label_xml} ----\n" \
            f"[{self.title_text}] \n" \
            f"        {self.p_text}"
        return s
