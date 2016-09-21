import sublime
import os

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

        while folder != "/":
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
    return "/"
