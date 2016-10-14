import sublime, sublime_plugin

import os
from .common.utils import run_bash_for_output
from .common.utils import git_path_for_window

last_command = ""

class RunBash(sublime_plugin.WindowCommand):
    def run(self):
        global last_command
        window = self.window
        view = window.active_view()
        if view.file_name() is not None:
            path = os.path.join(os.path.dirname(view.file_name()), '')
            window.show_input_panel(
                'Bash:',
                last_command,
                lambda command: (
                    self.run_bash(path, command)
                ),
                None,
                None
            )

    def run_bash(self, path, command):
        global last_command
        last_command = command

        if command.startswith('$'):
            command = command[1:]
            path = git_path_for_window(self.window)

        final_command = "cd '{0}'; {1}".format(path, command)
        output, _ = run_bash_for_output(final_command)
        print(final_command, " ", output)

        results_view = self.window.new_file()
        results_view.set_scratch(True)

        results_view.set_name("BashOutput")

        # deps: this is from utilities.py
        results_view.run_command('replace_content', {"new_content": output})
        results_view.sel().clear()
        results_view.sel().add(sublime.Region(0, 0))

        self.window.focus_view(results_view)
