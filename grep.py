import sublime, sublime_plugin
import re
import pipes
from subprocess import Popen, PIPE
import codecs
from os.path import expanduser

from .common.utils import wait_for_view_to_be_loaded_then_do
from .common.utils import git_path_for_window

def grepSettings():
    return sublime.load_settings('Grep.sublime-settings')

def grepPath(window):
    path = grepSettings().get('git_path')
    if path == "<interpolate_from_open_folder>":
        return git_path_for_window(window)
    else:
        return path

def prefixPath(window):
    prefix = grepSettings().get('prefix_path')
    if prefix == "<same_as_path>":
        return grepPath(window)
    else:
        return prefix

def grepFormatStr():
    return grepSettings().get('grep_format_str')

def quickGrepFormatStr():
    return grepSettings().get('quick_grep_format_str')

def tmpFile():
    return grepSettings().get('tmp_file')

class GrepCommand(sublime_plugin.WindowCommand):
    def run(self, ask, show_in_view, grep_command = None):
        self.show_in_view = show_in_view
        self.grep_command = grep_command

        view = self.window.active_view()
        selection = view.sel()
        if selection:
            region = selection[0]
            if region.empty():
                grep_str = view.substr(view.word(region.begin()))
            else:
                grep_str = view.substr(region)

        if ask or len(grep_str) <= 4:
            input_panel = self.window.show_input_panel(
                'Grep for: ',
                grep_str,
                lambda query: self.search(query),
                None,
                None
            )
            input_panel.sel().add(sublime.Region(0, input_panel.size()))
        else:
            self.search(grep_str)

    def search(self, query):
        if self.grep_command is not None:
            command = self.grep_command.format(pipes.quote(query))
        elif self.show_in_view:
            command = grepFormatStr().format(
                grepPath(self.window),
                pipes.quote(query)
            )
        else:
            # we need quick results
            command = quickGrepFormatStr().format(
                grepPath(self.window),
                pipes.quote(query)
            )

        command = "{0} >{1}".format(command, tmpFile())

        sublime.status_message("grepping {0} ...".format(pipes.quote(query)))

        p = Popen(command, shell=True, close_fds=True,
                  stdin=PIPE, stdout=PIPE, stderr=PIPE)

        p.wait()

        sublime.status_message("Done grepping")

        with codecs.open(expanduser(tmpFile()), 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.show_results(query, lines)
        pass

    def show_results(self, query, lines):
        results = [SearchResult(line) for line in lines if line]
        total_count = len(results)

        if total_count == 0:
            sublime.status_message("Grep: no results found")
            return

        if total_count == 1:
            open_result(results[0], self.window)
            sublime.status_message("Grep: found 1 result, opening file")
            return

        if self.show_in_view:
            results_view = self.window.new_file()
            results_view.set_scratch(True)
            results_view.set_syntax_file('Packages/sublimeplugins/Grep.sublime-syntax')
            # git_diff_open will fallback when the name starts with "grep:"
            results_view.set_name('grep: ' + query)

            result_text = 'Query: {0}\n\n{1}\n'.format(
                query,
                ''.join(lines)
            )

            # deps: this is from utilities.py
            results_view.run_command('replace_content', {'new_content': result_text})
            results_view.sel().clear()
            results_view.sel().add(sublime.Region(0, 0))

            self.window.focus_view(results_view)
        else:
            self.open_files = []
            self.open_results = []

            for result in results:
                self.open_results.append(result)
                if result.content:
                    self.open_files.append([result.path, result.content])
                else:
                    self.open_files.append(result.path)

            self.window.show_quick_panel(self.open_files, self.tab_selected) # show the file list

        return 'Grep: found {0} results.'.format(total_count)

    def tab_selected(self, selected):
        if selected > -1:
            open_result(self.open_results[selected], self.window)
        return selected

class OpenCommand(sublime_plugin.WindowCommand):
    def run(self):
        text = ""
        view = self.window.active_view()
        for sel in view.sel():
            first_line = view.line(sel.begin())
            last_line = view.line(sel.end())
            text = view.substr(sublime.Region(first_line.begin(), last_line.end()))
            text_arr = text.split('\n')
            for text_line in text_arr:
                open_result(SearchResult(text_line), self.window)


def open_result(result, window):
    if result.isValid():
        if result.path.startswith("/"):
            path = result.path
        else:
            path = prefixPath(window) + result.path
        view = window.open_file(path)

        def handle_view():
            if result.row is not None:
                row = result.row - 1
                column = 0
                point = view.text_point(row, column)
                view.run_command('show_view_at_position', {"position": point})

        wait_for_view_to_be_loaded_then_do(view, handle_view)


class SearchResult():
    def __init__(self, line):
        self.search_result = re.search('([^:]+):(\d+):(.*)', line)
        if self.search_result is not None:
            matches = self.search_result.groups()
            self.path = matches[0]
            self.row = int(matches[1])
            self.content = matches[2]

    def isValid(self):
        return self.search_result is not None and self.path is not None
