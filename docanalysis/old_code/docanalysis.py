version = "0.0.1"
from docanalysis.extract_entities import DocAnalysis
import configargparse
def handlecli():
    parser = configargparse.ArgParser(
            description=f"Welcome to docanalysis version {version}. -h or --help for help",
            add_config_file_help=False,)
    parser.add_argument("--section", "-s", nargs='*', )



    return parser

    """
    --section
    --extract_terms
    --extract_entites
    --dictionary
    --project_name
    --pygetpapers
    --
    """

def handle_cli_logic():
     pass