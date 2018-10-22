import sublime, sublime_plugin
from .common.utils import wait_for_view_to_be_loaded_then_do

reflect_window_id = None

class SetReflectWindow(sublime_plugin.ApplicationCommand):
    def run(self):
        global reflect_window_id
        # sublime.active_window().run_command("toggle_side_bar")
        sublime.active_window().set_sidebar_visible(False)
        reflect_window_id = sublime.active_window().id()

class FocusOutEventListener(sublime_plugin.EventListener):
    def on_deactivated(self, view):
        active_view = view.window().active_view()
        if active_view is None:
            return
        if view.id() == view.window().active_view().id():
            return
        if view.window().id() != reflect_window_id:
            for w in sublime.windows():
                if w.id() == reflect_window_id:

                    point = None
                    for sel in view.sel():
                        point = sel.begin()

                    file_name = view.file_name()
                    if file_name is not None:
                        new_view = w.open_file(file_name)
                        if point is not None:
                            # w.active_view().show_at_center(point)
                            def handle_view():
                                new_view.run_command('show_view_at_position', {"position": point})

                            wait_for_view_to_be_loaded_then_do(new_view, handle_view)
