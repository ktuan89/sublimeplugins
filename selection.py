import sublime, sublime_plugin

_start = -1

class StartSelection(sublime_plugin.TextCommand):
    def run(self, edit):
        global _start
        for sel in self.view.sel():
            if sel.empty():
                _start = sel.begin()

class EndSelection(sublime_plugin.TextCommand):
    def run(self, edit):
        global _start
        start = _start
        end = -1
        for sel in self.view.sel():
            if sel.empty():
                end = sel.begin()

        if start != -1 and end != -1:
            self.view.sel().clear()
            self.view.sel().add(sublime.Region(start, end))
