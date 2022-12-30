import re
import json
import platform
import subprocess
import tkinter as tk
from tkinter import filedialog, font as tkFont
import os
from functools import partial


class DARK:
    a1 = "#25292f"
    a2 = "#333842"
    a3 = "#3b4048"
    a4 = "#e79d28"
    b1 = "#e06c70"
    b2 = "#abb2bf"
    b3 = "#469aef"
    b4 = "#98c379"


class LIGHT:
    a1 = "#fffefe"
    a2 = "#c6cddf"
    a3 = "#ebedf2"
    a4 = "#b630f4"
    b1 = "#9199f9"
    b2 = "#74839a"
    b3 = "#a4a8de"
    b4 = "#8f8e95"


class Theme(DARK):
    def __init__(self):
        self.fieldWidth = 60
        self.labelWidth = 12
        self.runButtonWidth = 8
        self.fontA = tkFont.Font(family='helvetica', size=13)
        self.fontB = tkFont.Font(
            family='helvetica', size=14, weight=tkFont.BOLD)
        self.fontC = tkFont.Font(family='helvetica', size=12, slant='italic')
        self.settings = {
            'root': {'bg': self.a1},
            'frame': {'bg': self.a1},
            'label': {'bg': self.a1, 'fg': self.b2},
            'breaker': {'bg': self.a1, 'fg': self.b1},
            'label_frame': {'bg': self.a1, 'fg': self.b1},
            'menu': {'bg': self.a2, 'fg': self.b2, 'activebackground': self.b3},
            'text_field': {'highlightthickness': 0, 'bg': self.a3, 'fg': self.b4},
            'button_1': {'highlightthickness': 0, 'bg': self.a2, 'fg': self.b2, 'activebackground': self.b3},
            'run_button': {'highlightthickness': 0, 'bg': self.a2, 'fg': self.b2, 'activebackground': self.b1},
            'check_button': {'highlightthickness': 0, 'bg': self.a1, 'fg': self.b2, 'activebackground': self.a1, 'activeforeground': self.b3, 'selectcolor': self.a2}
        }


class App:
    def __init__(self, root, theme):
        self.root = root
        self.theme = theme
        self.projects = self.getProjects('config.json')
        self.projectName = tk.StringVar()
        self.projectName.set(list(self.projects.keys())[0])
        self.projectName.trace("w", self.setCurrentProject)
        self.runInProjectPath = tk.BooleanVar(value=True)
        self.fields = []
        self.frameA()
        self.breaker()
        self.frameB()
        self.breaker()
        self.dynamicFrame = tk.Frame(self.root)
        self.setCurrentProject()
        self.breaker()
        self.frameD()

    def frameA(self):
        frame = tk.Frame(self.root)
        frame.config(**self.theme.settings.get('frame'))

        optionMenu = tk.OptionMenu(
            frame, self.projectName, *self.projects.keys())
        optionMenu.config(**self.theme.settings.get('menu'), borderwidth=0)
        optionMenu.config(width=30)
        optionMenu["menu"].config(
            **self.theme.settings.get('menu'), borderwidth=0)
        optionMenu.config(highlightthickness=0)
        optionMenu["font"] = self.theme.fontB
        optionMenu.grid(row=0, column=0)

        self.description = tk.Label(frame, text="Face swaping project")
        self.description.config(**self.theme.settings.get('label'))
        self.description["font"] = self.theme.fontC
        self.description.grid(row=1, column=0, padx=2, pady=2)

        frame.pack(padx=24, pady=(18, 0))

    def frameB(self):
        frame = tk.Frame(self.root)
        frame.config(**self.theme.settings.get('frame'))
        frame.pack(fill="y", expand="yes", padx=24, pady=0)

    def frameC(self):
        self.dynamicFrame.config(**self.theme.settings.get('frame'))
        for i, item in enumerate(self.currentProject['inputs']):
            self.fields.append(self.createInput(
                self.dynamicFrame, index=i, **item))
        self.dynamicFrame.pack(fill="y", expand="yes", padx=24)

    def frameD(self):
        frame = tk.Frame(self.root)
        frame.config(**self.theme.settings.get('frame'))

        checkButton = tk.Checkbutton(frame, variable=self.runInProjectPath)
        checkButton["text"] = "Run in project directory"
        checkButton.config(**self.theme.settings.get('check_button'))
        checkButton.grid(row=0, column=0, sticky='E')

        runButton = tk.Button(
            frame, width=self.theme.runButtonWidth, borderwidth=0)
        runButton.config(**self.theme.settings.get('run_button'))
        runButton["text"] = 'RUN'
        label = tk.Label(frame, text="", width=50, font=('Calibri 15'))
        label.grid(row=1, column=0)
        runButton["command"] = partial(
            self.runCommand, label)

        runButton["font"] = self.theme.fontB
        runButton.grid(row=0, column=1, padx=6, sticky='E')

        frame.pack(padx=24, pady=(0, 18), side=tk.RIGHT)

    def breaker(self):
        breaker = tk.Label(self.root, text="_____"*15, **
                           theme.settings.get("breaker"))
        breaker.pack(padx=0, pady=(0, 18))

    def removeFrame(self):
        for widget in self.dynamicFrame.winfo_children():
            widget.destroy()
        self.fields.clear()

    def setCurrentProject(self, *args):
        self.removeFrame()
        self.currentProject = self.projects[self.projectName.get()]
        self.frameC()
        description = self.currentProject.get('description')
        description = re.sub("(.{100})", "\\1\n", description, 0, re.DOTALL)
        self.description.configure(text="( " + description + " )")

    def getProjects(self, configPath):
        with open(configPath) as json_file:
            return json.load(json_file)

    def generateCommand(self):
        command = ""
        for i, arg in enumerate(self.currentProject['arguments']):
            value = self.fields[i].get()
            command = " ".join([command, arg, f'"{value}"'])

        commands = ["docanalysis", command]
        commands = filter(None, commands)
        finalCommand = " ".join(commands)
        return finalCommand

    def runCommand(self, label):
        command = self.generateCommand()
        print("---------------------- Command --------------------------------")
        print(command)
        label.config(text="Command Being Exectued")

        print("---------------------- Execution started ----------------------")
        output = subprocess.check_output(command, shell=True)
        print(output)
        label.config(text="command executed")
        print("---------------------- Execution ended ------------------------")

    # https://stackoverflow.com/questions/4266566/stardand-context-menu-in-python-tkinter-text-widget-when-mouse-right-button-is-p

    def rClickMenu(self, e):
        try:
            def rCopy(e, apnd=0):
                e.widget.event_generate('<Control-c>')

            def rCut(e):
                e.widget.event_generate('<Control-x>')

            def rPaste(e):
                e.widget.event_generate('<Control-v>')
            e.widget.focus()
            nclst = [
                (' Cut', lambda e=e: rCut(e)),
                (' Copy', lambda e=e: rCopy(e)),
                (' Paste', lambda e=e: rPaste(e)),]
            rMenu = tk.Menu(None, tearoff=0, takefocus=0)
            rMenu.config(**self.theme.settings.get('menu'))
            for (txt, cmd) in nclst:
                rMenu.add_command(label=txt, command=cmd)
            rMenu.tk_popup(e.x_root + 40, e.y_root + 10, entry="0")
        except tk.TclError:
            pass
        return "break"

    def rClickBinder(self, r):
        try:
            for b in ['Text', 'Entry', 'Listbox', 'Label']:
                r.bind_class(b, sequence='<Button-3>',
                             func=self.rClickMenu, add='')
        except tk.TclError:
            pass

    def createInput(self, frame, index=0, name="", type="STRING", value=None):
        text = tk.StringVar()
        if isinstance(value, (str, int, float)):
            text.set(value)
        name = name[:12] + (name[12:] and '..')
        label = tk.Label(frame, text=name,
                         width=self.theme.labelWidth, anchor="e")
        label.config(**self.theme.settings.get('label'))
        label.grid(row=index, column=0, padx=2, pady=2, sticky="E")
        if type == "FILE":
            button = tk.Button(frame, anchor="n", borderwidth=0)
            button["text"] = "..."
            button["command"] = lambda: text.set(
                filedialog.askopenfilename(title="Select file"))
            button.config(**self.theme.settings.get('button_1'))
            button.grid(row=index, column=2, padx=2, pady=2)
        elif type == "DIRECTORY":
            button = tk.Button(frame, anchor="n", borderwidth=0)
            button["text"] = "..."
            button["command"] = lambda: text.set(
                filedialog.askdirectory(title="Select directory"))
            button.config(**self.theme.settings.get('button_1'))
            button.grid(row=index, column=2, padx=2, pady=2)
        elif type == "LIST":
            menu = tk.OptionMenu(frame, text, *value)
            menu.config(**self.theme.settings.get('menu'), borderwidth=0)
            menu["menu"].config(
                **self.theme.settings.get('menu'), borderwidth=0)
            menu.config(highlightthickness=0)
            menu.grid(row=index, column=1, padx=2, pady=2, sticky="W")
            text.set(value[0])
        elif type == "STRING":
            pass
        if type != "LIST":
            field = tk.Entry(frame, textvariable=text,
                             width=self.theme.fieldWidth, borderwidth=0)
            field.config(**self.theme.settings.get('text_field'))
            field.bind('<Button-3>', self.rClickMenu, add='')
            field.grid(row=index, column=1, padx=4, pady=2)
        return text


if __name__ == "__main__":
    root = tk.Tk()
    theme = Theme()
    root.title("Docanalysis")
    root.config(**theme.settings.get('root'))
    root.option_add("*font", theme.fontA)
    root.resizable(width=False, height=False)
    app = App(root, theme)
    root.mainloop()
