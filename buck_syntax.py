import sublime, sublime_plugin

class SetSyntaxForBuck(sublime_plugin.EventListener):
    def on_activated(self, view):
        if view.file_name() is not None and view.file_name().endswith("BUCK"):
            view.set_syntax_file("Packages/Python/Python.tmLanguage")
