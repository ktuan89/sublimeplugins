import sublime, sublime_plugin
import os
from os import listdir
from os.path import isfile, join

def settings():
    return sublime.load_settings('ViewNavigation.sublime-settings')

def xcodePath():
    return settings().get('xcodepath')

# this class is not my code, copied from internet
class ExtendedSwitcherHaha(sublime_plugin.WindowCommand):
    # declarations
    open_files = []
    open_views = []
    open_paths = []
    window = []
    settings = []
    active_view_path = ""

    # lets go
    def run(self, list_mode):
        self.open_files = []
        self.open_views = []
        self.open_paths = []
        self.window = sublime.active_window()
        self.settings = sublime.load_settings('ExtendedSwitcher.sublime-settings')
        self.active_view_path = self.window.active_view().file_name()

        for f in self.getViews(list_mode):
            # if skip the current active is enabled do not add the current file it for selection
            # if self.settings.get('skip_current_file') == True:
            if True:
                if f.id() == self.window.active_view().id():
                    continue

            self.open_views.append(f) # add the view object
            file_name = f.file_name() # get the full path
            self.open_paths.append(file_name)

            if file_name:
                if f.is_dirty():
                    file_name += self.settings.get('mark_dirty_file_char') # if there are any unsaved changes to the file

                if self.settings.get('show_full_file_path') == True:
                    self.open_files.append(os.path.basename(file_name) + ' - ' + os.path.dirname(file_name))
                elif self.settings.get('show_last_folder') == True:
                    last_folder = os.path.basename(os.path.normpath(os.path.dirname(file_name)))
                    self.open_files.append(os.path.basename(file_name) + ' - ' + last_folder)
                else:
                    self.open_files.append(os.path.basename(file_name))

            else:
                self.open_files.append("Untitled")

        if self.check_for_sorting():
            self.sort_files()

        self.window.show_quick_panel(self.open_files, self.tab_selected) # show the file list

    # display the selected open file
    def tab_selected(self, selected):
        if selected > -1:
            self.window.focus_view(self.open_views[selected])

        return selected

    # sort the files for display in alphabetical order
    def sort_files(self):
        # TODO
        pass

    # flags for sorting
    def check_for_sorting(self):
        return False

    def getViews(self, list_mode):
        views = []
        # get only the open files for the active_group
        if list_mode == "active_group":
            views = self.window.views_in_group(self.window.active_group())

        # get all open view if list_mode is window or active_group doesnt not have any files open
        if (list_mode == "window") or (len(views) < 1):
            views = self.window.views()

        return views

class InFolderSwitcher(sublime_plugin.WindowCommand):

    files = []
    is_file = []

    mypath = ""

    def run(self):

        file_name = self.window.active_view().file_name()
        if file_name is not None:
            self.mypath = os.path.join(os.path.dirname(file_name), '')
            self.open_for_current_path()

        pass

    def open_for_current_path(self):
        self.files = []
        self.is_file = []
        for f in listdir(self.mypath):
            self.files.append(f)
            self.is_file.append(isfile(join(self.mypath, f)))

        if self.mypath != "/":
            self.files.append("`")
            self.is_file.append(False)

        self.window.show_quick_panel(self.files, self.tab_selected)

    def tab_selected(self, selected):
        if selected > -1:
            if self.is_file[selected]:
                self.window.open_file(os.path.join(self.mypath,self.files[selected]))
            else:
                folder = self.files[selected]
                if folder == "`":
                    folder = ".."
                self.mypath = os.path.join(self.mypath, folder)
                sublime.set_timeout_async(self.open_for_current_path, 50)

        return selected

class OpenFileInXcode(sublime_plugin.TextCommand):
    def run(self, edit):
        if self.view.file_name() is not None:
            #print self.view.file_name()
            #subprocess.call(["open", "-a", "/Applications/Xcode.app", self.view.file_name()])
            os.system(("open -a {0} '" + self.view.file_name() + "'").format(xcodePath()))

class OpenInFinder(sublime_plugin.TextCommand):
    def run(self, edit):
        if self.view.file_name() is not None:
            #print self.view.file_name()
            #subprocess.call(["open", "-a", "/Applications/Xcode.app", self.view.file_name()])
            os.system("open '" + os.path.dirname(self.view.file_name()) + "'")
