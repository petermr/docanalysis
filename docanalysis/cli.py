import os
import logging
import sys
import docanalysis
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
        self.version="0.0.1"

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
            description=f"Welcome to Docanalysis version {version}. -h or --help for help",
            add_config_file_help=False,
        )
        parser.add_argument(
            "--run_pygetpapers",
            default=False,
            action="store_true",
            help="queries EuropePMC via pygetpapers",
        )

        parser.add_argument(
            "-q",
            "--query",
            default=None,
            type=str,
            help="query to pygetpapers",
        )
        parser.add_argument(
            "-k",
            "--hits",
            type=str,
            default=None,
            help="numbers of papers to download from pygetpapers",
        )

        parser.add_argument(
            "--project_name",
            type=str,
            help="name of CProject folder",
            default=os.path.join(os.getcwd(), default_path),
        )
        parser.add_argument(
            "--section",
            type=str,
            help="section of paper from which you want to extract information (entities and/or key phrases)",
        )
        parser.add_argument(
            "--entity_extraction",
            default=False,
            nargs='+',
            help="extracts specified entities chosen from a list of entities (CARDINAL, DATE, EVENT, FAC, GPE, LANGUAGE, LAW, LOC, MONEY, NORP, ORDINAL, ORG, PERCENT, PERSON, PRODUCT, QUANTITY, TIME, WORK_OF_ART, GGP, SO, TAXON, CHEBI, GO, CL)",
        )
        parser.add_argument(
            "--key_phrase_extraction",
            default=False,
            type=str,
            help="gives a list of keyphrases extracted either from specific sections or sentences for each paper in CProject. (unsupervised keyphrase extraction)",
        )
        parser.add_argument(
            "--make_dictionary",
            default=False,
            type=str,
            help="makes separate dictionaries from keyphrases and entities extracted. Merges duplicate entries into one",
        )
        parser.add_argument(
            "-d",
            "--dictionary",
            default=False,
            type=str,
            help="Ami Dictionary to extract keywords from",
        )
        parser.add_argument(
            "-o",
            "--output",
            default="entities.csv",
            help="Output CSV file",
        )
        parser.add_argument(
            "-l",
            "--loglevel",
            default="info",
            help="[All] Provide logging level.  "
            "Example --log warning <<info,warning,debug,error,critical>>, default='info'",
        )
        parser.add_argument(
            "-f",
            "--logfile",
            default=False,
            type=str,
            help="[All] save log to specified file in output directory as well as printing to terminal",
        )


        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            sys.exit()
        args = parser.parse_args()
        for arg in vars(args):
            if vars(args)[arg] == "False":
                vars(args)[arg] = False
        self.handle_logger_creation(args)
        self.entity_extraction.extract_entities_from_papers(args.project_name,args.dictionary,query=args.query,hits=args.hits,
                                     make_project=args.run_pygetpapers, install_ami=False, removefalse=True, create_csv=True,
                                     csv_name=args.output, labels_to_get=args.entity_extraction)



def main():
    """Runs the CLI"""
    calldocanalysis = Docanalysis()
    calldocanalysis.handlecli()


if __name__ == "__main__":
    main()
