import sublime, sublime_plugin
import hashlib
import os

def backupSettings():
    return sublime.load_settings('Backup.sublime-settings')

def backupPath():
    return backupSettings().get('path')

class StoreBackupUnsavedBuffer(sublime_plugin.ApplicationCommand):
    def run(self):
        path = backupPath()
        if not path:
            return
        if not os.path.exists(path):
            os.makedirs(path)

        for window in sublime.windows():
            for view in window.views():
                if not view.is_scratch() and not view.file_name():
                    # store the view
                    content = view.substr(sublime.Region(0, view.size()))
                    content_hash = hashlib.md5(content.encode('utf-8'))
                    content_hash = content_hash.hexdigest()[:10]
                    file_path = os.path.join(path, content_hash)

                    text_file = open(file_path + ".txt", "w", encoding='utf-8')
                    text_file.write(content)
                    text_file.close()
