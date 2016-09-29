# sublimeplugins

This is a set of plugins to empower Sublime Text 3 editor for regular developers. It's especially useful for git users.

## Installation

Go to `Packages` folder of Sublime Text (on MacOS, it is `~/Library/Application Support/Sublime Text 3/Packages/`), then clone this repo by running:

```
git clone https://github.com/ktuan89/sublimeplugins.git
```

## Usage

You can take a look at `Default (OSX).sublime-keymap` to see all features and shortcuts.

Tip: If you want to change a shortcut or a setting value inside one of `.sublime-settings` files, you can create a file with same name in `~/Library/Application Support/Sublime Text 3/Packages/User/` folder. Files with same name will be merged by Sublime Text and shortcuts/values in `User` folder take precedence. By doing so, you can keep this repo clean and you can pull future fixes/improvements without conflicts.

### Git Integration

By default, the plugin takes a look at your first open folder and use git repo of that folder. You can hardcode your own folder in `Git.sublime-settings`.

 1. `Ctrl + g d`: Run `git diff` and show the result in Sublime Text.
 2. `Ctrl + g s`: Run `git show` and show the result in Sublime Text.
 3. `Command + Shift + \`: If you are viewing `git diff` or `git show` content, this shortcut brings you to the file you are viewing (under the current cursor) at the exact position.
 4. `Ctrl + g o`: If you are rebasing and having conflicts. It will list all files with conflicts and you can open these files in Sublime Text.
 5. `Ctrl + g a`: Mark the conflicted file as resolved. This is flaky for some reason so I usually use git command line directly.

### Grep

 1. `Command + Shift + t`: Grep for a text. Currently I use `git grep` as my codebase is quite big. You can change settings in `Grep.sublime-settings`
 2. `Command + Shift + \`: If you are viewing grep result file (result of the previous command), this shortcut brings you to the file under the cursor. It's actually the same shortcut with number 3 of `Git Integration`. If you are selecting multiple lines, it will open all files under selection.
 3. `Ctrl + Enter`: Perform a "quick grep". It uses the current word under the cursor without asking you again. It looks for the word preceeded by word `class|protocol|struct|etc` so it always look for definition of the word in codebase. If there is only one result, it brings you to the file immediately. Take a look at `quick_grep_format_str` option in `Grep.sublime-settings` to see how it works.

### Navigation

 1. `Command + Shift + o`: List all open files so that you can search for a file name and open it.
 2. `Command + Shift + i`: List all files in the same folder with current file. This is useful when you structure files i
 3. `Ctrl + \`: List all files (among open files) which contain the current word (under the cursor). Generally this command isn't useful as it is replaceable by one of Grep commands.
 4. `Ctrl + o`: Open the current file in Xcode. If your are opening Xcode project has the file, it will open the file under that project.
 5. `Ctrl + 0`: Open the folder of the current file in Finder.
 6. `Ctrl + 9`: Open the folder of the current file in Terminal.
 7. `Command + number` (from 1 - 9): By default, Sublime will open one of your first-opened files (with 1 is the first ever opened file). This isn't useful when you work on a project with 20+ files. You probably don't even remember when you opened the first file. If you set `"use_recent_file_navigation": true` in Sublime Preference settings, it reverts the behavior. For example, `Command + 1` will open the previous file, `Command + 2` will open the file before the previous file, etc.


### Other utilities
 1. `Ctrl + w`, `Ctrl + e`: Go to the previous/next occurrence of the current word (under the cursor). It avoids "copy-search-paste-enter" sequence of keys.
 2. `Ctrl + f`: Filter and only keep lines that contain a string. Prefix the string with minus (`-`) char to filter lines that don't contain the string.
 3. `Ctrl + [` to mark the beginning of a selection and `Ctrl + ]` to mark the end. Useful to select a large block of text.
 4. `Ctrl + c`: Copy (to clipboard) current word under the cursor - no need to select the word.
 5. `Ctrl + r`: Replace the current word with something else. It affects all occurrences of current file. Prefix the string with `#` to replace in all open files.
 6. BUCK syntax: If you are using BUCK build system from Facebook, you can notice that BUCK file is actually a python file but Sublime Text doesn't highlight the file in python syntax. One of the plugins fixes the issue.

## Credits

Although I have done most of the coding by myself. I copied and/or was inspired by:
 1. [Sublime's Extended Tab Switcher](https://github.com/rajeshvaya/Sublime-Extended-Tab-Switcher) with modifications to fit to my own work flow.
 2. Facebook internal tools for code search.

## License

MIT