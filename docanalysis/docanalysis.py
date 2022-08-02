import os
import logging
import sys
import configargparse
import coloredlogs
from time import gmtime, strftime
from tqdm import tqdm
from functools import partialmethod
from docanalysis.entity_extraction import EntityExtraction


class Docanalysis:

    def __init__(self):
        """This function makes all the constants"""
        self.entity_extraction = EntityExtraction()
        self.version = "0.1.9"

    def handle_logger_creation(self, args):
        """handles the logging on cml

        :param args: description]
        :type args: type]

        """
        coloredlogs.install()
        levels = {
            "critical": logging.CRITICAL,
            "error": logging.ERROR,
            "warn": logging.WARNING,
            "warning": logging.WARNING,
            "info": logging.INFO,
            "debug": logging.DEBUG,
        }
        level = levels.get(args.loglevel.lower())

        if level == logging.DEBUG:
            tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)

        if args.logfile:
            self.handle_logfile(args, level)
        else:
            coloredlogs.install(level=level, fmt='%(levelname)s: %(message)s')

    def handlecli(self):
        """Handles the command line interface using argparse"""
        version = self.version

        default_path = strftime("%Y_%m_%d_%H_%M_%S", gmtime())
        parser = configargparse.ArgParser(
            description=f"Welcome to docanalysis version {version}. -h or --help for help",
            add_config_file_help=False,
        )
        parser.add_argument(
            "--run_pygetpapers",
            default=False,
            action="store_true",
            help="[Command] downloads papers from EuropePMC via pygetpapers",
        )
        parser.add_argument(
            "--make_section",
            default=False,
            action="store_true",
            help="[Command] makes sections; requires a fulltext.xml in CTree directories",
        )
        parser.add_argument(
            "-q",
            "--query",
            default=None,
            type=str,
            help="[pygetpapers] query string",
        )
        parser.add_argument(
            "-k",
            "--hits",
            type=str,
            default=None,
            help="[pygetpapers] number of papers to download",
        )

        parser.add_argument(
            "--project_name",
            type=str,
            help="CProject directory name",
            default=os.path.join(os.getcwd(), default_path),
        )
        parser.add_argument(
            "-d",
            "--dictionary",
            default=[],
            type=str,
            nargs='*',
            help="[file name/url] existing ami dictionary to annotate sentences or support supervised entity extraction",
        )
        parser.add_argument(
            "-o",
            "--output",
            default=False,
            help="outputs csv with sentences/terms",
        )
        parser.add_argument(
            "--make_ami_dict",
            default=False,
            help="[Command] title for ami-dict. Makes ami-dict of all extracted entities; works only with spacy",
        )
        parser.add_argument(
            "--search_section",
            default=['ALL'],
            action='store',
            dest='search_section',
            type=str,
            nargs='*',
            help="[NER/dictionary search] section(s) to annotate. Choose from: ALL, ACK, AFF, AUT, CON, DIS, ETH, FIG, INT, KEY, MET, RES, TAB, TIL. Defaults to ALL",
        )

        parser.add_argument(
            "--entities",
            default=['ALL'],
            action='store', dest='entities',
            type=str, nargs='*',
            help="[NER] entities to extract. Default (ALL). Common entities "
            "SpaCy: GPE, LANGUAGE, ORG, PERSON (for additional ones check: ); "
            "SciSpaCy: CHEMICAL, DISEASE",
        )

        parser.add_argument(
            "--spacy_model",
            default=False,
            type=str,
            help="[NER] optional. Choose between spacy or scispacy models. Defaults to spacy",
        )

        parser.add_argument(
            "--html",
            default=False,
            type=str,
            help="outputs html with sentences/terms",
        )

        parser.add_argument(
            "--synonyms",
            default=False,
            type=str,
            help="annotate the corpus/sections with synonyms from ami-dict",
        )
        parser.add_argument(
            "--make_json",
            default=False,
            type=str,
            help="outputs json with sentences/terms",
        )
        parser.add_argument(
            "--search_html",
            default=False,
            action="store_true",
            help="searches html documents (mainly IPCC)",
        )
        parser.add_argument(
            "--extract_abb",
            default=False,
            help="[Command] title for abb-ami-dict. Extracts abbreviations and expansions; makes ami-dict of all extracted entities"
        )

        parser.add_argument(
            "-l",
            "--loglevel",
            default="info",
            help="provide logging level. "
            "Example --log warning <<info,warning,debug,error,critical>>, default='info'",
        )

        parser.add_argument(
            "-f",
            "--logfile",
            default=False,
            type=str,
            help="saves log to specified file in output directory as well as printing to terminal",
        )

        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            sys.exit()
        args = parser.parse_args()
        for arg in vars(args):
            if vars(args)[arg] == "False":
                vars(args)[arg] = False
        self.handle_logger_creation(args)
        self.entity_extraction.extract_entities_from_papers(args.project_name, args.dictionary, search_sections=args.search_section, entities=args.entities, query=args.query, hits=args.hits,
                                                            run_pygetpapers=args.run_pygetpapers, make_section=args.make_section, removefalse=True,
                                                            csv_name=args.output, make_ami_dict=args.make_ami_dict, spacy_model=args.spacy_model, html_path=args.html, synonyms=args.synonyms, make_json=args.make_json, search_html=args.search_html, extract_abb=args.extract_abb)


def main():
    """Runs the CLI"""
    calldocanalysis = Docanalysis()
    calldocanalysis.handlecli()


if __name__ == "__main__":
    main()
