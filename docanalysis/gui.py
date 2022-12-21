import eel
from pygetpapers import Pygetpapers
import os

eel.init(f'{os.path.dirname(os.path.realpath(__file__))}/gui')


@eel.expose
def create_corpus(path, query, number):
    pygetpapers_call = Pygetpapers()
    pygetpapers_call.run_command(
        query=query, limit=number, output=path, xml=True)


eel.start('main.html')
