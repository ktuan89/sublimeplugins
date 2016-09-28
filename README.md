# sublimeplugins

This is a set of plugins to empower Sublime Text 3 editor for regular developers. It's especially useful for git users.

## Installation

Go to `Packages` folder of Sublime Text (on MacOS, it is `~/Library/Application Support/Sublime Text 3/Packages/`), then clone this repo by running:

```
git clone https://github.com/ktuan89/sublimeplugins.git
```

## Usage

You can take a look at `Default (OSX).sublime-keymap` to see all features and shortcuts. Feel free to change shortcuts based on your preferences. Here is the list of features:

### Git Integration

By default, the plugin takes a look at your first open folder and use git repo of that folder. You can hardcode your own folder in `Git.sublime-settings`.

 1. `Ctrl + g d`: Run `git diff` and show the result in Sublime Text.
 2. `Ctrl + g s`: Run `git show` and show the result in Sublime Text.
 3. `Command + Shift + \`: If you are viewing `git diff` or `git show` content, this shortcut brings you to the file you are viewing (under the current cursor) at the exact position.
 4. `Ctrl + g o`: If you are rebasing and having conflicts. It will list all files with conflicts and you can open these files in Sublime Text.
 5. `Ctrl + g a`: Mark the conflicted file as resolved.

### Grep

 1. `Command + Shift + t`: Grep for a text. Currently I use `git grep` as my codebase is quite big. You can change settings in `Grep.sublime-settings`
 2. `Command + Shift + \`: If you are viewing grep result file, this shortcut brings you to the file under the cursor. It's actually the same shortcut with number 3 of `Git Integration`.
 3. `Ctrl + Enter`: Perform a "quick grep". It uses the current word under the cursor without asking you again. It looks for the word preceeded by word `class|protocol|struct|etc` so it always look for definition of the word in codebase. If there is only one result, it brings you to the file immediately. Take a look at `quick_grep_format_str` option in `Grep.sublime-settings` to see how it works.

### Navigation

### Other utilities


## Credits

Although I have done most of the coding by myself. I copied and/or was inspired by:
 1. [Sublime's Extended Tab Switcher](https://github.com/rajeshvaya/Sublime-Extended-Tab-Switcher) with modifications to fit to my own work flow.
 2. Facebook internal tools for code search.

## License

MIT