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
        self.version="0.1.1"

    def handle_logger_creation(self, args):
        """[summary]

        :param args: [description]
        :type args: [type]
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
            help="downloads papers from EuropePMC via pygetpapers",
        )
        parser.add_argument(
            "--make_section",
            default=False,
            action="store_true",
            help="makes sections",
        )
        parser.add_argument(
            "-q",
            "--query",
            default=None,
            type=str,
            help="provide query to pygetpapers",
        )
        parser.add_argument(
            "-k",
            "--hits",
            type=str,
            default=None,
            help="specify number of papers to download from pygetpapers",
        )

        parser.add_argument(
            "--project_name",
            type=str,
            help="provide CProject directory name",
            default=os.path.join(os.getcwd(), default_path),
        )
        parser.add_argument(
            "-d",
            "--dictionary",
            default=False,
            type=str,
            help="provide ami dictionary to annotate sentences or support supervised entity extraction",
        )
        parser.add_argument(
            "-o",
            "--output",
            default=False,
            help="outputs csv file",
        )
        parser.add_argument(
            "--make_ami_dict",
            default=False,
            help="provide title for ami-dict. Makes ami-dict of all extracted entities",
        )
        parser.add_argument(
            "--search_section",
            default=['ALL'],
            action='store', 
            dest='search_section',
            type=str, 
            nargs='*', 
            help="provide section(s) to annotate. Choose from: ALL, ACK, AFF, AUT, CON, DIS, ETH, FIG, INT, KEY, MET, RES, TAB, TIL. Defaults to ALL",
        )

        parser.add_argument(
            "--entities",
            default=['ALL'],
            action='store', dest='entities',
                    type=str, nargs='*', 
            help="provide entities to extract. Default(ALL). Choose from "
            "SpaCy: CARDINAL, DATE, EVENT, FAC, GPE, LANGUAGE, LAW, LOC, MONEY, NORP, ORDINAL, ORG, PERCENT, PERSON, PRODUCT, QUANTITY, TIME, WORK_OF_ART; "
            "SciSpaCy: CHEMICAL, DISEASE",
        )

        parser.add_argument(
            "--spacy_model",
            default=False,
            type=str,
            help="optional. Choose between spacy or scispacy models. Defaults to spacy",
        )

        parser.add_argument(
            "--html",
            default=False,
            type=str,
            help="saves output in html format to given path",
        )

        parser.add_argument(
            "--synonyms",
            default=False,
            type=str,
            help="searches the corpus/sections with synonymns from ami-dict",
        )
        parser.add_argument(
            "--make_json",
            default=False,
            type=str,
            help="output in json format",
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
        self.entity_extraction.extract_entities_from_papers(args.project_name,args.dictionary,search_section=args.search_section,entities=args.entities,query=args.query,hits=args.hits,
                                     run_pygetpapers=args.run_pygetpapers, make_section= args.make_section, removefalse=True,
                                     csv_name=args.output,make_ami_dict=args.make_ami_dict,spacy_model=args.spacy_model,html_path=args.html, synonyms=args.synonyms, make_json=args.make_json)



def main():
    """Runs the CLI"""
    calldocanalysis = Docanalysis()
    calldocanalysis.handlecli()


if __name__ == "__main__":
    main()
