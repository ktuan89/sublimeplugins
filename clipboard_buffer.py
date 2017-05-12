import sublime, sublime_plugin
import os

clipboard_buffer = []

MAX_BUFFER = 10
MAX_LENGTH = 100

class HandleClipboardBuffer(sublime_plugin.TextCommand):
    def run(self, edit):
        position_to_add = None
        string_to_add = None
        for region in self.view.sel():
            if region.empty():
                position_to_add = self.view.rowcol(region.begin())
            else:
                string_to_add = self.view.substr(region)

        global clipboard_buffer

        if string_to_add is not None:
            file_name = self.view.file_name()
            if file_name is None:
                file_name = "Untitled"
            else:
                file_name = os.path.basename(file_name)
            clipboard_buffer.insert(0, (file_name, string_to_add))
            if len(clipboard_buffer) > MAX_BUFFER:
                clipboard_buffer.pop()
        else:
            items = []
            for i in range(0, len(clipboard_buffer)):
                (file_name, display_string) = clipboard_buffer[i]
                if len(display_string) > MAX_LENGTH:
                    display_string = display_string[:MAX_LENGTH]
                items.append([file_name, display_string])
            self.view.window().show_quick_panel(items, lambda selected: self.on_done(edit, position_to_add, selected))

    def on_done(self, edit, position_to_add, index):
        if index > -1:
            (file_name, string_to_add) = clipboard_buffer[index]
            (row, col) = position_to_add
            self.view.run_command('insert_clipboard_buffer', {"row": row, "col": col, "text": string_to_add})

class InsertClipboardBuffer(sublime_plugin.TextCommand):
    def run(self, edit, row, col, text):
        line_range = self.view.line(self.view.text_point(row, 0))
        position = self.view.text_point(row, col)
        # take care of space auto-trim on focus lost
        if position > line_range.end():
            position = line_range.end()
        self.view.insert(edit, position, text)
