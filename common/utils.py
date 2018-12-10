import sublime
import os

from subprocess import Popen, PIPE
import codecs

from os.path import expanduser


def fix_command_str_if_windows(s):
    if sublime.platform() == "windows":
        return s.replace("'", "\"").replace(";", " &&")
    else:
        return s

def wait_for_view_to_be_loaded_then_do(view, func):

    def wait_for_view_to_be_loaded_then_do_exp(view, func, timeout):
        if view.is_loading():
            sublime.set_timeout(lambda: wait_for_view_to_be_loaded_then_do(view, func), timeout * 2)
            return
        sublime.set_timeout(lambda: func(), timeout * 2)

    wait_for_view_to_be_loaded_then_do_exp(view, func, 10)


saved_git_folders = set()

# return git root folder based on the first opened folder of the window
def git_path_for_window(window):
    folders = window.folders()
    if len(folders) > 0:
        folder = folders[0]

        global saved_git_folders
        for saved_git_folder in saved_git_folders:
            if folder.startswith(saved_git_folder):
                return saved_git_folder

        while folder != "/" and len(folder) > 3:
            git_folder = os.path.abspath(os.path.join(folder, ".git"))
            if os.path.isdir(git_folder):
                final_folder = os.path.join(folder, '')
                saved_git_folders.add(final_folder)
                return final_folder
            next_folder = os.path.abspath(os.path.join(folder, os.pardir))
            if next_folder == folder:
                break
            folder = next_folder
        return folder
    file_name = window.active_view().file_name()
    if file_name:
        path = os.path.join(os.path.dirname(file_name), '')
        return path
    # intentionally keep random result to avoid harming the file system although
    # we are running a `git grep` command in here and the command is read-only
    if sublime.platform() == "windows":
        return "C:\\R_A__N_D___O_M_F_I___L__E\\"
    return "/R_A__N_D___O_M_F_I___L__E/"

def dequeue_view(window, pool, count):
    d = {}
    for view in window.views():
        d[view.id()] = view
    active_group = window.active_group()
    per_group_pool = pool.get(active_group, [])
    while len(per_group_pool) >= count:
        vid = per_group_pool.pop()
        if vid in d:
            per_group_pool.insert(0, vid)
            return d[vid]

    view = window.new_file()
    per_group_pool.insert(0, view.id())
    pool[active_group] = per_group_pool
    return view

def run_bash_for_output(command):
    close_fds = True
    if sublime.platform() == "windows":
        close_fds = False
    p = Popen(command, shell=True, close_fds=close_fds,
                  stdin=PIPE, stdout=PIPE, stderr=PIPE)

    output, err = p.communicate()

    return (codecs.decode(output, 'utf-8'), codecs.decode(err, 'utf-8'))

def open_file_in_window(window, file_name):
    # keep old style open_file for now
    return window.open_file(file_name)
    # always open a file in the active group
    view = window.find_open_file(file_name)
    if view is None:
        return window.open_file(file_name)
    else:
        (group_id, view_index) = window.get_view_index(view)
        if group_id != window.active_group():
            window.set_view_index(view, window.active_group(), 0)
        return window.open_file(file_name)
