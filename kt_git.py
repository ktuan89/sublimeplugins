import sublime, sublime_plugin
from sublime import Phantom, PhantomSet
import re
from subprocess import Popen, PIPE
import codecs
from os.path import expanduser
import webbrowser

from .common.utils import wait_for_view_to_be_loaded_then_do
from .common.utils import git_path_for_window

def gitSettings():
    return sublime.load_settings('Git.sublime-settings')

def gitPath(window):
    path = gitSettings().get('path')
    if path == "<interpolate_from_open_folder>":
        return git_path_for_window(window)
    else:
        return path

def gitWebBlameUrl():
    return gitSettings().get('web_blame_url')

def tmpFile():
    return gitSettings().get('tmp_file')

class GitBase(sublime_plugin.WindowCommand):
    def gitCommand(self):
        return ""

    def gitName(self):
        return ""

    def run(self):
        p = Popen(self.gitCommand(), shell=True, close_fds=True,
                  stdin=PIPE, stdout=PIPE, stderr=PIPE)

        p.wait()

        with codecs.open(expanduser(tmpFile()), 'r', encoding='utf-8') as f:
            lines = f.readlines()
            stdout = ''.join(lines)

            results_view = self.window.new_file()
            results_view.set_scratch(True)
            results_view.set_syntax_file('Packages/Diff/Diff.tmLanguage')

            results_view.set_name(self.gitName())

            # deps: this is from utilities.py
            results_view.run_command('replace_content', {"new_content": stdout})
            results_view.sel().clear()
            results_view.sel().add(sublime.Region(0, 0))

            self.window.focus_view(results_view)
        pass

class GitShow(GitBase):
    def gitCommand(self):
        return "cd '{0}';git show >{1}".format(gitPath(self.window), tmpFile())
    def gitName(self):
        return "GitShow"

class GitStatus(GitBase):
    def gitCommand(self):
        return "cd '{0}';git status >{1}".format(gitPath(self.window), tmpFile())
    def gitName(self):
        return "GitStatus"

class GitDiff(GitBase):
    def gitCommand(self):
        return "cd '{0}';git diff >{1}".format(gitPath(self.window), tmpFile())
    def gitName(self):
        return "GitDiff"

class GitDiffOpen(sublime_plugin.WindowCommand):
    def positionFromView(self, view):
        for region in view.sel():
            if region.empty():
                return region.begin()
        return -1
    def run(self):
        view = self.window.active_view()
        if view.name().startswith("Git") or (view.file_name() is not None and view.file_name().endswith("diff")):
            print("ere")
            pos = self.positionFromView(view)
            line = view.line(pos)

            current_line = view.substr(line)


            line_offset = pos - line.begin()
            position_str = ""
            file_str = ""
            line_count = 0
            while True:
                if line.begin() <= 0:
                    break
                line = view.line(line.begin() - 1)
                str = view.substr(line)

                if position_str=="" and not str.startswith("-"):
                    line_count = line_count + 1

                if position_str=="" and str.startswith("@@"):
                    position_str = str

                if file_str=="" and str.startswith("+++"):
                    file_str = str

                if file_str != "" and position_str != "":
                    break

            if file_str == "" or position_str == "":
                return

            file_name = file_str[len("+++ b/"):]
            matches = re.search('@@.*\+(.*),(.*) @@', position_str)
            extract_position = (int(matches.group(1)) - 1) + (line_count - 1)

            new_view = self.window.open_file(gitPath(self.window) + file_name.strip())

            def handle_view():
                new_position = new_view.text_point(extract_position, line_offset)
                new_view.run_command('show_view_at_position', {"position": new_position})

            wait_for_view_to_be_loaded_then_do(new_view, handle_view)
            pass # happy dancing
        elif view.name().startswith("grep:"):
            # deps: going to add this fallback soon
            self.window.run_command('open')
            pass
        pass

class GitListModifiedFiles(sublime_plugin.WindowCommand):

    files = []

    def run(self):
        command = "cd '{0}';git status".format(gitPath(self.window))
        p = Popen(command, shell=True, close_fds=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        p.wait()
        files = []

        for line in p.stdout.readlines():
            str = line.decode("utf-8")
            print(str)
            matches = re.search('both modified:\s+((((\w|-)+)\/)*(\w+)\.(\w+))', str)
            if matches is not None:
                file_name = matches.group(1)
                files.append(file_name)

        self.files = files
        print(files)

        self.window.show_quick_panel(self.files, self.tab_selected)

        pass

    def tab_selected(self, selected):
        if selected > -1:
            file_name = self.files[selected]
            self.window.open_file(gitPath(self.window) + file_name)
            pass

class GitAdd(sublime_plugin.WindowCommand):

    files = []

    def run(self):
        file_name = self.window.active_view().file_name()
        if file_name is None:
            return
        sublime.status_message("git: add ...")
        command = ("cd '{0}';git add " + file_name).format(gitPath(self.window))
        p = Popen(command, shell=True, close_fds=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        p.wait()
        sublime.status_message("git: added")
        for line in p.stdout.readlines():
            str = line.decode("utf-8")
            print(str)
        pass

class GitListBranches(sublime_plugin.WindowCommand):

    branches = []

    def run(self):
        command = "cd '{0}';git branch".format(gitPath(self.window))
        p = Popen(command, shell=True, close_fds=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        p.wait()
        branches = []
        display_branches = []

        for line in p.stdout.readlines():
            str = line.decode("utf-8")
            matches = re.search('(\*|\s)+(.*)', str)
            if matches is not None:
                branch = matches.group(2)
                branches.append(branch)
                display_branches.append(str)

        self.branches = branches

        self.window.show_quick_panel(display_branches, self.tab_selected)

        pass

    def tab_selected(self, selected):
        if selected > -1:
            branch = self.branches[selected]
            command = ("cd '{0}';git checkout " + branch).format(gitPath(self.window))
            p = Popen(command, shell=True, close_fds=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            p.wait()
            sublime.status_message("git: checkout " + branch)
            pass

viewIdToPhantomSet = {}

class GitBlame(sublime_plugin.TextCommand):
    def run(self, edit):
        (viewport_x, viewport_y) = self.view.viewport_position()
        path = gitPath(self.view.window())
        current_path = self.view.file_name()
        if current_path is not None and current_path.startswith(path):
            remaining_path = current_path[len(path):]
            command = ("cd '{0}';git blame --show-email '{1}' >{2}").format(path, remaining_path, tmpFile())
            print(command)
            p = Popen(command, shell=True, close_fds=True,
                  stdin=PIPE, stdout=PIPE, stderr=PIPE)

            p.wait()

            with codecs.open(expanduser(tmpFile()), 'r', encoding='utf-8') as f:
                lines = f.readlines()
                line_count = 0

                regions = self.view.lines(sublime.Region(0, self.view.size()))
                phantoms = []

                last_hash = None

                for line in lines:
                    matches = re.search(r'^([0-9a-z]+).*?\(<(.*?)>', line)
                    # print(line, ' ', matches)
                    if matches is not None and line_count < len(regions):
                        hash = matches.group(1)
                        email = matches.group(2)
                        at_position = email.find("@")
                        if at_position != -1:
                            email = email[:at_position]
                        if len(email) > 10:
                            email = email[:10]
                        email = "{:*>10}".format(email)

                        if hash == last_hash:
                            email = "." * 10
                            html = "<b>{0}</b>".format(email)
                        else:
                            html = "<a href='{0}'>{1}</a>".format(hash, email)

                        last_hash = hash

                        r = regions[line_count]
                        phantom = Phantom(sublime.Region(r.begin(), r.begin()), html, sublime.LAYOUT_INLINE, lambda link: self.click(link) )
                        phantoms.append(phantom)

                    line_count = line_count + 1
                global phantomSet
                phantomSet = PhantomSet(self.view, 'git_blame')
                phantomSet.update(phantoms)
                global viewIdToPhantomSet
                viewIdToPhantomSet[self.view.id()] = phantomSet
                self.view.set_viewport_position((0, viewport_y))

    def click(self, link):
        path = gitPath(self.view.window())
        command = ("cd '{0}';git show {1} >{2}").format(path, link, tmpFile())
        p = Popen(command, shell=True, close_fds=True,
              stdin=PIPE, stdout=PIPE, stderr=PIPE)

        p.wait()

        with codecs.open(expanduser(tmpFile()), 'r', encoding='utf-8') as f:
            lines = f.readlines()
            stdout = ''.join(lines)

            window = self.view.window()
            results_view = window.new_file()
            results_view.set_scratch(True)
            results_view.set_syntax_file('Packages/Diff/Diff.tmLanguage')

            results_view.set_name('GitBlame')

            # deps: this is from utilities.py
            results_view.run_command('replace_content', {"new_content": stdout})
            results_view.sel().clear()
            results_view.sel().add(sublime.Region(0, 0))

            window.focus_view(results_view)

            """for line in lines:
                matches = re.search(r'Differential Revision: (http.*/D[0-9]+)', line)
                if matches is not None:
                    actual_link = matches.group(1)
                    webbrowser.open_new(actual_link)"""

class GitBlameRemove(sublime_plugin.TextCommand):
    def run(self, edit):
        global viewIdToPhantomSet
        if self.view.id() in viewIdToPhantomSet:
            viewIdToPhantomSet[self.view.id()].update([])
            viewIdToPhantomSet.pop(self.view.id(), None)

class GitBlameInBrowser(sublime_plugin.TextCommand):
    def run(self, edit):
        path = gitPath(self.view.window())
        current_path = self.view.file_name()
        if current_path is not None and current_path.startswith(path) and gitWebBlameUrl() is not None:
            remaining_path = current_path[len(path):]
            print(remaining_path,' ', current_path, ' ', path)
            link = gitWebBlameUrl().format(remaining_path)
            webbrowser.open_new(link)