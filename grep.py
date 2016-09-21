import sublime, sublime_plugin
import re
import pipes
from subprocess import Popen, PIPE
import codecs
from os.path import expanduser

from .common.utils import wait_for_view_to_be_loaded_then_do

def grepSettings():
    return sublime.load_settings('Grep.sublime-settings')

def grepPath():
    return grepSettings().get('git_path')

def prefixPath():
    return grepSettings().get('prefix_path')

def grepFormatStr():
    return grepSettings().get('grep_format_str')

def quickGrepFormatStr():
    return grepSettings().get('quick_grep_format_str')

def tmpFile():
    return grepSettings().get('tmp_file')

class GrepCommand(sublime_plugin.WindowCommand):
    def run(self, ask, show_in_view):
        self.show_in_view = show_in_view
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

        if self.show_in_view:
            command = grepFormatStr().format(
                grepPath(),
                pipes.quote(query)
            )
        else:
            # we need quick results
            command = quickGrepFormatStr().format(
                grepPath(),
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
            results_view.set_syntax_file('Packages/C++/C++.tmLanguage')
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
            if sel.empty():
                line = view.line(sel.begin())
                text = view.substr(line)
                open_result(SearchResult(text), self.window)
                break

def open_result(result, window):
    if result.path:
        view = window.open_file(prefixPath() + result.path)

        def handle_view():
            if result.row is not None:
                row = result.row - 1
                column = 0
                point = view.text_point(row, column)
                view.show_at_center(point)
                view.sel().clear()
                view.sel().add(sublime.Region(point, point))

        wait_for_view_to_be_loaded_then_do(view, handle_view)


class SearchResult():
    def __init__(self, line):
        matches = re.search('([^:]+):(\d+):(.*)', line).groups()
        self.path = matches[0]
        self.row = int(matches[1])
        self.content = matches[2]

