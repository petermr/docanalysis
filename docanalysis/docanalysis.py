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
        self.version="0.0.4"

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
            "--run_sectioning",
            default=False,
            action="store_true",
            help="make sections",
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
            "-d",
            "--dictionary",
            default=False,
            type=str,
            help="Ami Dictionary to tag sentences and support supervised entity extraction",
        )
        parser.add_argument(
            "-o",
            "--output",
            default="entities.csv",
            help="Output CSV file [default=entities.csv]",
        )
        parser.add_argument(
            "--make_ami_dict",
            default=False,
            help="if provided will make ami dict with given title",
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
                                     run_pygetpapers=args.run_pygetpapers, run_sectioning= args.run_sectioning, removefalse=True, create_csv=True,
                                     csv_name=args.output,make_ami_dict=args.make_ami_dict)



def main():
    """Runs the CLI"""
    calldocanalysis = Docanalysis()
    calldocanalysis.handlecli()


if __name__ == "__main__":
    main()
