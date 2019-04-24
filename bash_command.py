import sublime, sublime_plugin

import os
from .common.utils import run_bash_for_output
from .common.utils import git_path_for_window

last_command = ""
last_path = ""

class RunBash(sublime_plugin.WindowCommand):
    def run(self):
        global last_command
        global last_path
        window = self.window
        view = window.active_view()
        file_name = None
        path = None
        if view.file_name() is not None:
            file_name = os.path.basename(view.file_name())
            path = os.path.join(os.path.dirname(view.file_name()), '')
        elif last_path:
            path = last_path
        elif len(window.folders()) > 0:
            path = window.folders()[0]

        if path:
            window.show_input_panel(
                'Bash:',
                last_command,
                lambda command: (
                    self.run_bash(path, file_name, command)
                ),
                None,
                None
            )

    def run_bash(self, path, file_name, command):
        global last_command
        global last_path
        last_command = command
        last_path = path

        if command.startswith('$'):
            command = command[1:]
            path = git_path_for_window(self.window)

        if file_name:
            command = command.replace("@", file_name)

        final_command = "cd '{0}'; {1}".format(path, command)
        output, err = run_bash_for_output(final_command)
        new_content = output + '\n' + (100 * '=') + '\n' + err

        results_view = self.window.new_file()
        results_view.set_scratch(True)

        results_view.set_name("BashOutput")

        # deps: this is from utilities.py
        results_view.run_command('replace_content', {"new_content": new_content})
        results_view.sel().clear()
        results_view.sel().add(sublime.Region(0, 0))

        self.window.focus_view(results_view)
