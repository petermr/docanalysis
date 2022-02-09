"""classes and methods to support path operations

"""
import json
import copy
import glob
import re
import os
import shutil
from pathlib import Path, PurePath
import logging
from glob import glob
from braceexpand import braceexpand

logging.debug("loading file_lib")

py4ami = "py4ami"
RESOURCES = "resources"

# section keys
_DESC = "_DESC"
PROJ = "PROJ"
TREE = "TREE"
SECTS = "SECTS"
SUBSECT = "SUBSECT"
SUBSUB = "SUBSUB"
FILE = "FILE"
SUFFIX = "SUFFIX"

ALLOWED_SECTS = {_DESC, PROJ, TREE, SECTS, SUBSECT, SUBSUB, FILE, SUFFIX}

# wildcards
STARS = "**"
STAR = "*"

# suffixes
S_PDF = "pdf"
S_PNG = "png"
S_SVG = "svg"
S_TXT = "txt"
S_XML = "xml"

# markers for processing
_NULL = "_NULL"
_REQD = "_REQD"

# known section names
SVG = "svg"
PDFIMAGES = "pdfimages"
RESULTS = "results"
SECTIONS = "sections"

# subsects
IMAGE_STAR = "image*"

# subsects
OCTREE = "*octree"

# results
SEARCH = "search"
WORD = "word"
EMPTY = "empty"

# files
FULLTEXT_PAGE = "fulltext-page*"
CHANNEL_STAR = "channel*"
RAW = "raw"


class Globber:
    """utilities for globbing - may be obsolete"""

    def __init__(self, ami_path, recurse=True, cwd=None) -> None:
        self.ami_path = ami_path
        self.recurse = recurse
        self.cwd = os.getcwd() if cwd is None else cwd

    def get_globbed_files(self) -> list:
        """uses the glob_string_list in ami_path to create a path list"""
        files = []
        if self.ami_path:
            glob_list = self.ami_path.get_glob_string_list()
            for gl_str in glob_list:
                files += glob.glob(gl_str, recursive=self.recurse)
        return files


class AmiPath:
    """holds a (keyed) scheme for generating lists of path globs
    The scheme has several segments which can be set to create a glob expr.
    """
    # keys for path scheme templates
    T_FIGURES = "fig_captions"
    T_OCTREE = "octree"
    T_PDFIMAGES = "pdfimages"
    T_RESULTS = "results"
    T_SECTIONS = "sections"
    T_SVG = "svg"

    logger = logging.getLogger("ami_path")
    # dict

    def __init__(self, scheme=None):
        self.scheme = scheme

    def print_scheme(self):
        """for debugging and enlightenment"""
        if self.scheme is not None:
            for key in self.scheme:
                print("key ", key, "=", self.scheme[key])
            print("")

    @classmethod
    def create_ami_path_from_templates(cls, key, edit_dict=None):
        """creates a new AmiPath object from selected template
        key: to template
        edit_dict: dictionary with values to edit in
        """
        key = key.lower()
        if key is None or key not in TEMPLATES:
            cls.logger.error(f"cannot find key {key}")
            cls.logger.error("no scheme for: ", key,
                             "expected", TEMPLATES.keys())
        ami_path = AmiPath()
        # start with default template values
        ami_path.scheme = copy.deepcopy(TEMPLATES[key])
        if edit_dict:
            ami_path.edit_scheme(edit_dict)
        return ami_path

    def edit_scheme(self, edit_dict):
        """edits values in self.scheme using edit_dict"""
        for k, v in edit_dict.items():
            self.scheme[k] = v

    def permute_sets(self):
        self.scheme_list = []
        self.scheme_list.append(self.scheme)
        # if scheme has sets, expand them
        change = True
        while change:
            change = self.expand_set_lists()

    def expand_set_lists(self):
        """expands the sets in a scheme
        note: sets are held as lists in JSON

        a scheme with 2 sets of size n and m is
        expanded to n*m schemes covering all permutations
        of the set values

        self.scheme_list contains all the schemes

        returns True if any sets are expanded

        """
        change = False
        for scheme in self.scheme_list:
            for sect, value in scheme.items():
                if type(value) == list:
                    change = True
                    # delete scheme with set, replace by copies
                    self.scheme_list.remove(scheme)
                    for set_value in value:
                        scheme_copy = copy.deepcopy(scheme)
                        self.scheme_list.append(scheme_copy)
                        scheme_copy[sect] = set_value  # poke in set value
                    break  # after each set processed

        return change

    def get_glob_string_list(self):
        """expand sets in AmiPath
        creates m*n... glob strings for sets with len n and m
        """
        self.permute_sets()
        self.glob_string_list = []
        for scheme in self.scheme_list:
            glob_string = AmiPath.create_glob_string(scheme)
            self.glob_string_list.append(glob_string)
        return self.glob_string_list

    @classmethod
    def create_glob_string(cls, scheme):
        globx = ""
        for sect, value in scheme.items():
            cls.logger.debug(sect, type(value), value)
            if sect not in ALLOWED_SECTS:
                cls.logger.error(f"unknown sect: {sect}")
            elif _DESC == sect:
                pass
            elif _REQD == value:
                cls.logger.error("must set ", sect)
                globx += _REQD + "/"
            elif _NULL == value:
                pass
            elif FILE == sect:
                globx += AmiPath.convert_to_glob(value)
            elif STAR in value:
                globx += AmiPath.convert_to_glob(value) + "/"
            elif SUFFIX == sect:
                globx += "." + AmiPath.convert_to_glob(value)
            else:
                globx += AmiPath.convert_to_glob(value) + "/"
        cls.logger.debug("glob", scheme, "=>", globx)
        return globx

    @classmethod
    def convert_to_glob(cls, value):
        valuex = value
        if type(value) == list:
            # tacky. string quotes and add commas and parens
            valuex = "("
            for v in value:
                valuex += v + ","
            valuex = valuex[:-1] + ")"
        return valuex

    def get_globbed_files(self):
        files = Globber(self).get_globbed_files()
        self.logger.debug("files", len(files))
        return files


class BraceGlobber:

    def braced_glob(self, path, recursive=False):
        ll = [glob(x, recursive=recursive) for x in braceexpand(path)]
        return ll


class FileLib:

    logger = logging.getLogger("file_lib")

    @classmethod
    def force_mkdir(cls, dirx):
        """ensure dirx exists

        :dirx: directory
        """
        if not os.path.exists(dirx):
            try:
                os.mkdir(dirx)
            except Exception as e:
                cls.logger.error(f"cannot make dirx {dirx} , {e}")

    @classmethod
    def force_mkparent(cls, file):
        """ensure parent directory exists

        :path: whose parent directory is to be created if absent
        """
        if file is not None:
            cls.force_mkdir(cls.get_parent_dir(file))

    @classmethod
    def force_write(cls, file, data, overwrite=True):
        """:write path, creating dirtectory if necessary
        :path: path to write to
        :data: str data to write
        :overwrite: force write iuf path exists

        may throw exception from write
        """
        if file is not None:
            if os.path.exists(file) and not overwrite:
                logging.warning(f"not overwriting existsnt path {file}")
            else:
                cls.force_mkparent(file)
                with open(file, "w", encoding="utf-8") as f:
                    f.write(data)

    @classmethod
    def copy_file_or_directory(cls, dest_path, src_path, overwrite):
        if dest_path.exists():
            if not overwrite:
                file_type = "dirx" if dest_path.is_dir() else "path"
                raise TypeError(
                    str(dest_path), f"cannot overwrite existing {file_type} (str({dest_path})")

        else:
            # assume directory
            cls.logger.warning(f"create directory {dest_path}")
            dest_path.mkdir(parents=True, exist_ok=True)
            cls.logger.info(f"created directory {dest_path}")
        if src_path.is_dir():
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(src_path, dest_path)
            cls.logger.info(f"copied directory {src_path} to {dest_path}")
        else:
            try:
                shutil.copy(src_path, dest_path)  # will overwrite
                cls.logger.info(f"copied path {src_path} to {dest_path}")
            except Exception as e:
                cls.logger.fatal(f"Cannot copy direcctory {src_path} to {dest_path} because {e}")

    @staticmethod
    def create_absolute_name(file):
        """create absolute/relative name for a path relative to py4ami

        TODO this is messy
        """
        absolute_file = None
        if file is not None:
            file_dir = FileLib.get_parent_dir(__file__)
            absolute_file = os.path.join(os.path.join(file_dir, file))
        return absolute_file

    @classmethod
    def get_py4ami(cls):
        """ gets paymi_m pathname

        """
        return Path(__file__).parent.resolve()

    @classmethod
    def get_pyami_root(cls):
        """ gets paymi root pathname

        """
        return Path(__file__).parent.parent.resolve()

    @classmethod
    def get_pyami_resources(cls):
        """ gets paymi root pathname

        """
        return Path(cls.get_py4ami(), RESOURCES)

    @classmethod
    def get_parent_dir(cls, file):
        return None if file is None else PurePath(file).parent

    @classmethod
    def read_pydictionary(cls, file):
        """read a json path into a python dictiomary"""
        import ast
        with open(file, "r") as f:
            pydict = ast.literal_eval(f.read())
        return pydict

    @classmethod
    def punct2underscore(cls, text):
        """ replace all ASCII punctuation except '.' , '-', '_' by '_'

        for filenames

        """
        from py4ami.text_lib import TextUtil
        # this is non-trivial https://stackoverflow.com/questions/10017147/removing-a-list-of-characters-in-string

        non_file_punct = '\t \n{}!@#$%^&*()[]:;\'",|\\~+=/`'
        # [unicode(x.strip()) if x is not None else '' for x in row]

        text0 = TextUtil.replace_chars(text, non_file_punct, "_")
        return text0

    @classmethod
    def get_suffix(cls, file):
        """get suffix
        INCLUDES the "."

        """
        _suffix = None if file is None else Path(file).suffix
        return _suffix


# see https://realpython.com/python-pathlib/

def main():
    print("started file_lib")
    # test_templates()

    print("finished file_lib")


if __name__ == "__main__":
    print("running file_lib main")
    main()
else:
    #    print("running file_lib main anyway")
    #    main()
    pass

# examples of regex for filenames


def glob_re(pattern, strings):
    return filter(re.compile(pattern).match, strings)


filenames = glob_re(r'.*(abc|123|a1b).*\.txt', os.listdir())
