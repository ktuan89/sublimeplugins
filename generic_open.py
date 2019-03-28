import sublime, sublime_plugin
import re

import os
from os.path import isdir, isfile, join

from .common.utils import wait_for_view_to_be_loaded_then_do
from .common.utils import open_file_in_window

def genericOpenSettings():
    return sublime.load_settings('GenericOpen.sublime-settings')

def genericOpenPaths():
    return genericOpenSettings().get("path_list")

def actual_file_from_partial_file_path(str):
    path_list = genericOpenPaths()
    for path in path_list:
        if isdir(path):
            standard_path = os.path.join(path, '')
            file_name = os.path.join(standard_path, str)
            if isfile(file_name):
                return file_name
    return None

def split_positions_from_file_path(str):
    index = str.find(":")
    if index > 0:
        return (str[0:index], str[index + 1:])
    else:
        return (str, None)

def row_col_from_positions(str):
    numbers = str.split(":")
    if len(numbers) > 1 and len(numbers[0]) > 0 and len(numbers[1]) > 0:
        try:
            return (int(numbers[0]), int(numbers[1]))
        except ValueError:
            return (int(numbers[0]), 1)
    elif len(numbers) > 0 and len(numbers[0]) > 0:
        return (int(numbers[0]), 1)
    else:
        return None

class GenericOpenCommand(sublime_plugin.WindowCommand):
    def run(self):
        text = ""
        view = self.window.active_view()
        for sel in view.sel():
            if sel.empty():
                start = sel.begin()
                end = sel.begin()
                while end < view.size() and self.match(view.substr(end)):
                    end = end + 1
                while start - 1 >= 0 and self.match(view.substr(start - 1)):
                    start = start - 1
                self.open(view.substr(sublime.Region(start, end)))

    def open(self, str):
        (file_path, positions) = split_positions_from_file_path(str)
        file_name = actual_file_from_partial_file_path(file_path)
        if file_name is not None:
            view = open_file_in_window(self.window, file_name)
            def reposition():
                if positions is not None:
                    rowcol = row_col_from_positions(positions)
                    if rowcol is not None:
                        view = self.window.active_view()
                        (row, col) = rowcol
                        point = view.text_point(row - 1, col - 1)
                        view.run_command('show_view_at_position', {"position": point})
            wait_for_view_to_be_loaded_then_do(view, reposition)

    def match(self, str):
        return re.match(r'[A-Za-z0-9\.\/\\_\-@:]+', str)
