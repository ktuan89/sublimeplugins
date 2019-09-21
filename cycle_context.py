import sublime, sublime_plugin

values = {}

class CycleContextTracker(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        prefix = "cycle_"
        if key.startswith(prefix):
            number = int(key[len(prefix):len(prefix)+1])
            actual_key = key[len(prefix)+1]
            if actual_key not in values:
                values[actual_key] = 0
            if int(operand) == values[actual_key]:
                values[actual_key] = (values[actual_key] + 1) % number
                return True
            else:
                return False
        return None
