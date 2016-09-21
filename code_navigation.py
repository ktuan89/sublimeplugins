import sublime, sublime_plugin
import re

kt_last_same_word = ""

class GoToSameWord(sublime_plugin.TextCommand):

    def find_text(self, str, text):

        if self.reverse:
            text = text[::-1]
            str = str[::-1]

        pp = '\\b' + text + '\\b'
        p = re.compile(pp)
        result = p.search(str)
        if result is not None:
            if self.reverse:
                return len(str) - (result.start() + len(text))
            else:
                return result.start()
        return -1

    def scrollToPosition(self, position):
        self.view.show(position)
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(position, position))

    def run(self, edit, reverse):
        self.reverse = reverse
        text = ""
        start = -1
        for region in self.view.sel():
            if region.empty():
                start = region.begin()
                text = self.view.substr(self.view.word(region.begin()))

        global kt_last_same_word

        if not re.match(r'^[A-Za-z0-9_]+$', text):
            if kt_last_same_word == "":
                return
            text = kt_last_same_word

        kt_last_same_word = text

        if reverse:
            if 0 < start:
                s = self.view.substr(sublime.Region(0, start))
                next = self.find_text(s, text)
                if next != -1:
                    print("here2 ", next)
                    self.scrollToPosition(next)
                    return

            if start + 1 < self.view.size():
                s = self.view.substr(sublime.Region(start + 1, self.view.size()))
                next = self.find_text(s, text)
                if next != -1:
                    print("here ", next)
                    self.scrollToPosition(next + start + 1)
                    return

        else:

            if start + 1 < self.view.size():
                s = self.view.substr(sublime.Region(start + 1, self.view.size()))
                next = self.find_text(s, text)
                if next != -1:
                    print("here ", next)
                    self.scrollToPosition(next + start + 1)
                    return

            if 0 < start:
                s = self.view.substr(sublime.Region(0, start))
                next = self.find_text(s, text)
                if next != -1:
                    print("here2 ", next)
                    self.scrollToPosition(next)
                    return

        pass


MAX_VIEWS = 50
kt_active_view_list = []

class KeepTrackActiveViews(sublime_plugin.EventListener):

    def on_activated(self, view):
        if kt_active_view_list.count(view.id()) > 0:
            kt_active_view_list.remove(view.id())
        kt_active_view_list.insert(0, view.id())
        if len(kt_active_view_list) > MAX_VIEWS:
            kt_active_view_list.pop()

class JumpToAppearances(sublime_plugin.WindowCommand):

    open_files = []
    open_views = []
    open_positions = []

    def run(self):
        global kt_active_view_list
        current_view = self.window.active_view()

        other_views = [v for v in self.window.views() if v.id() != current_view.id()]
        other_views_in_order = []
        added_view_ids = set()
        # TODO: optimize it
        for ordered_index in kt_active_view_list:
            for cur_view in other_views:
                if cur_view.id() == ordered_index and cur_view.id() not in added_view_ids:
                    other_views_in_order.append(cur_view)
                    added_view_ids.add(cur_view.id())
        for cur_view in other_views:
            if cur_view.id() not in added_view_ids:
                other_views_in_order.append(cur_view)
                added_view_ids.add(cur_view.id())

        views = other_views_in_order
        views = views[0:MAX_VIEWS]

        self.open_files = []
        self.open_views = []
        self.open_positions = []

        current_view = self.window.active_view()
        text = ""
        for region in current_view.sel():
            if region.empty():
                text = current_view.substr(current_view.word(region.begin()))

        if len(text) <= 2:
            return

        for v in views:
            l_file_name = v.file_name()
            if l_file_name is None:
                l_file_name = "Untitled"
                continue
            s = self.find_text(v, text)
            print(s)
            if s is not None:
                self.open_files.append([l_file_name, s[0]])
                self.open_views.append(v)
                self.open_positions.append(s[1])

        self.window.show_quick_panel(self.open_files, self.tab_selected) # show the file list

    def find_text(self, view, text):
        s = view.substr(sublime.Region(0, view.size()))
        pp = '\\b' + text + '\\b'
        p = re.compile(pp)
        result = p.search(s)
        if result is not None:
            return [view.substr(view.line(result.start())), result.start()]
        return None

    def tab_selected(self, selected):
        if selected > -1:
            the_view = self.open_views[selected]
            the_position = self.open_positions[selected]
            self.window.focus_view(the_view)
            the_view.show_at_center(the_position)
            the_view.sel().clear()
            the_view.sel().add(sublime.Region(the_position, the_position))

        return selected