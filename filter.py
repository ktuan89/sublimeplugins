import sublime, sublime_plugin

class FilterText(sublime_plugin.TextCommand):
	def run(self, edit):
		window = self.view.window()
		window.show_input_panel(
            'Filter for:',
            '',
            lambda query: (
                self.filter(edit, query)
            ),
            None,
            None
        )
		pass

	def filter(self, edit, text):
		negative = False
		if text.startswith("-"):
			text = text[1:]
			negative = True
		str = self.view.substr(sublime.Region(0, self.view.size()))
		lines = str.split('\n')
		new_lines = []
		for line in lines:
			if (line.find(text) > -1 and not negative) or (negative and line.find(text) == -1):
				new_lines.append(line)
		self.view.run_command('replace_content', {"new_content": '\n'.join(new_lines)})
		pass