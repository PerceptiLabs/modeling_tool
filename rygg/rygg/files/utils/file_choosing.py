from contextlib import contextmanager
import os
import platform
SYS_NAME = platform.system().lower()

from rygg.settings import IS_CONTAINERIZED

if IS_CONTAINERIZED:
    def open_file_dialog(*args, **kwargs):
        pass
else:
    # Some systems allow you to install python w/o tk. Check for that and warn the user
    import pkgutil
    if not pkgutil.find_loader('tkinter'):
        raise Exception("Unable to import tkinter. Do you have the python tk package installed on your system?")

    from tkinter import filedialog, Tk

    from rygg.files.utils.procs import run_on_main_thread

    # Different OSes have different ways to get the window to the top of the z-order
    @contextmanager
    def _toplevel_window():
        # Make a top-level instance and hide since it is ugly and big.
        root = Tk()
        root.withdraw()

        if SYS_NAME.startswith("darwin"):
            import os
            from Cocoa import NSRunningApplication, NSApplicationActivateIgnoringOtherApps

            app = NSRunningApplication.runningApplicationWithProcessIdentifier_(os.getpid())
            app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
        else:
            # Make it almost invisible - no decorations, 0 size, top left corner.
            root.overrideredirect(True)
            root.geometry('0x0+0+0')

            # Show window again and lift it to top so it can get focus,
            # otherwise dialogs will end up behind the terminal.
            root.deiconify()
            root.lift()
            root.attributes('-topmost',True)
            root.after_idle(root.attributes,'-topmost',False)
            root.focus_force()
        yield root
        root.destroy()

    def _open_file_dialog(initial_dir=os.path.expanduser('~'), title = None, file_types=None):
        # If the initial dir isn't a directory, then askopenfilename will default to the cwd, which isn't helpful
        if not os.path.isdir(initial_dir):
            initial_dir = "~"
        initial_dir = os.path.expanduser(initial_dir)
        file_types = file_types or []
        title = title or "Choose a File"

        with _toplevel_window() as root:
            filename = filedialog.askopenfilename(parent=root, initialdir=initial_dir, title=title, filetypes=file_types)
            return filename or None

    def open_file_dialog(initial_dir="~", title=None, file_types=None):
        # tkinter requires that you open the dialog from the main thread
        # We're in a server, so we need to spawn a process for that.
        if file_types:
            file_types = list(file_types)
        return run_on_main_thread(_open_file_dialog, initial_dir=initial_dir, title=title, file_types=file_types)
