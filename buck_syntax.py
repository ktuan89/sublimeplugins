import sublime, sublime_plugin

class SetSyntaxForBuck(sublime_plugin.EventListener):
    def on_activated(self, view):
        if view.name() == "BUCK":
            view.set_syntax_file("Packages/Python/Python.tmLanguage")