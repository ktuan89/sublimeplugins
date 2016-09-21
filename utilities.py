import sublime, sublime_plugin
import re

class ReplaceAllAppearances(sublime_plugin.WindowCommand):

    original_text = ""

    def run(self):
        text = ""
        active_view = self.window.active_view()
        for region in active_view.sel():
            if region.empty():
                text = active_view.substr(active_view.word(region.begin()))

        if not re.match(r'^[A-Za-z0-9_]+$', text):
            return

        if len(text) <= 2:
            return

        self.original_text = text

        self.window.show_input_panel(
            'Replace {0} with'.format(text),
            '',
            lambda query: (
                self.replace(query)
            ),
            None,
            None
        )

    def replace(self, query):
        if query.startswith("#"):
            query = query[1:]
            views = self.window.views()
        else:
            views = [self.window.active_view()]

        total = 0
        for view in views:
            original_string = view.substr(sublime.Region(0, view.size()))
            pp = '\\b' + self.original_text + '\\b'
            p = re.compile(pp)
            (new_string, count) = p.subn(query, original_string)
            total = total + count
            if new_string != original_string:
                view.run_command('replace_content', {"new_content": new_string})
        sublime.status_message("Replace {0} occurrences from {1} files".format(total, len(views)))
        pass

class ReplaceContent(sublime_plugin.TextCommand):
    def run(self, edit, new_content):
        view = self.view
        view.replace(edit, sublime.Region(0, view.size()), new_content)

class AlignColon(sublime_plugin.TextCommand):
    def previousLine(self, line):
        return self.view.line(sublime.Region(line.begin() - 1))
    def firstColon(self, str):
        return str.find(':')
    def totalBeginingSpace(self, str):
        r = 0
        while r < len(str) and str[r] == ' ':
            r = r + 1
        return r
    def run(self, edit):
        for region in self.view.sel():
            if region.empty():
                cur = self.view.line(region)
                prev = self.previousLine(cur)
                prev_line = self.view.substr(prev)
                cur_line = self.view.substr(cur)
                p = self.firstColon(prev_line)
                c = self.firstColon(cur_line)
                print(prev_line)
                print(cur_line)
                if p >= 0 and c >= 0:
                    if p > c:
                        self.view.insert(edit, cur.begin(), ' ' * (p - c))
                    elif c > p:
                        r = self.totalBeginingSpace(cur_line)
                        r = min(r, c - p)
                        self.view.erase(edit, sublime.Region(cur.begin(), cur.begin() + r))

class CopyCurrentWord(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if region.empty():
                sublime.set_clipboard(self.view.substr(self.view.word(region.begin())))

