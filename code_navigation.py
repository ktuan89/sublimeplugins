import sublime, sublime_plugin
import re

from .common.utils import wait_for_view_to_be_loaded_then_do

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

class JumpToKthView(sublime_plugin.WindowCommand):
    def run(self, index):
        view_id_to_view = {}
        for v in self.window.views():
            view_id_to_view[v.id()] = v
        filtered_ids = [i for i in kt_active_view_list if i in view_id_to_view]
        if index < len(filtered_ids):
            self.window.focus_view(view_id_to_view[filtered_ids[index]])
        pass

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
            # print("find_text ", s)
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
            the_view.run_command('show_view_at_position', {"position": the_position})

        return selected

class QuickFind(sublime_plugin.WindowCommand):

    all_views = []
    last_string_to_find = ""
    last_line = -1
    current_file_index = 0

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
        self.all_views = views[0:MAX_VIEWS]

        current_view = self.window.active_view()
        text = ""
        for region in current_view.sel():
            if region.empty():
                text = current_view.substr(current_view.word(region.begin()))

        input_panel = None
        input_panel = self.window.show_input_panel(
            'Quick search: ',
            text,
            lambda query: self.search(query),
            lambda query: self.on_change(input_panel),
            None)
        input_panel.settings().set("tab_completion", False)
        input_panel.sel().add(sublime.Region(input_panel.size(), input_panel.size()))
        input_panel.show(input_panel.size())
        sublime.set_timeout(lambda: input_panel.show(0), 100)

    def find_str(self, stringToFind):
        if len(stringToFind) < 2 or len(self.all_views) == 0:
            return

        original_file_index = self.current_file_index
        for tt in range(len(self.all_views)):
            view_to_consider = self.all_views[self.current_file_index]
            result = self.find_text(view_to_consider, self.last_line, stringToFind)
            if result is not None:
                (found_line, found_pos) = result
                self.last_line = found_line
                self.window.focus_view(view_to_consider)
                the_position = view_to_consider.text_point(found_line, found_pos)
                def focus():
                    view_to_consider.run_command('show_view_at_position', {"position": the_position, "length": len(stringToFind)})
                wait_for_view_to_be_loaded_then_do(view_to_consider, focus)
                break
            else:
                self.current_file_index = (self.current_file_index + 1) % len(self.all_views)
                self.last_line = -1
                if self.current_file_index == original_file_index:
                    break

    def find_text(self, view, last_line, text):
        regions = view.split_by_newlines(sublime.Region(0, view.size()))
        for i in range(0, len(regions)):
            if i > last_line:
                line = view.substr(regions[i])
                pos = line.find(text)
                if pos >= 0:
                    return (i, pos)
        return None

    def on_change(self, view):
        if not view:
            return
        selection = view.sel()
        if len(selection) != 1:
            return
        region = selection[0]
        if not region.empty():
            return
        pos = region.begin()
        # print("\"" + view.substr(sublime.Region(0, view.size())) + "\"")
        if view.substr(pos - 1) == '\t':
            stringToFind = view.substr(sublime.Region(0, pos - 1))
            view.run_command('remove_last_tab')
            self.find_str(stringToFind)
        else:
            current_file_index = 0
            last_line = -1

    def search(self, stringToFind):
        self.find_str(stringToFind)

        input_panel = None
        input_panel = self.window.show_input_panel(
            'Quick search: ',
            stringToFind,
            lambda query: self.search(query),
            lambda query: self.on_change(input_panel),
            None)
        input_panel.settings().set("tab_completion", False)
        input_panel.sel().add(sublime.Region(input_panel.size(), input_panel.size()))
        input_panel.show(input_panel.size())
        sublime.set_timeout(lambda: input_panel.show(0), 100)

class RemoveLastTab(sublime_plugin.TextCommand):
    def run(self, edit):
        length = self.view.size()
        self.view.erase(edit, sublime.Region(length - 1, length))

