import sublime

def wait_for_view_to_be_loaded_then_do(view, func):

    def wait_for_view_to_be_loaded_then_do_exp(view, func, timeout):
        if view.is_loading():
            sublime.set_timeout(lambda: wait_for_view_to_be_loaded_then_do(view, func), timeout * 2)
            return
        sublime.set_timeout(lambda: func(), timeout * 2)

    wait_for_view_to_be_loaded_then_do_exp(view, func, 10)
