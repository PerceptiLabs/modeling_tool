from contextlib import contextmanager
import os
import platform
SYS_NAME = platform.system().lower()

from rygg.settings import IS_CONTAINERIZED

if IS_CONTAINERIZED:
    def open_file_dialog(*args, **kwargs):
        pass

    def open_saveas_dialog(*args, **kwargs):
        pass

    def open_directory_dialog(*args, **kwargs):
        pass
else:
    # Some systems allow you to install python w/o tk. Check for that and warn the user
    import pkgutil
    if not pkgutil.find_loader('tkinter'):
        raise Exception("Unable to import tkinter. Do you have the python tk package installed on your system?")

    from tkinter import filedialog, Tk

    from rygg.files.utils.procs import run_on_main_thread
    from multiprocessing import get_start_method, set_start_method
    import platform

    def _set_start_method():
        if not platform.system().lower().startswith("darwin"):
            return

        start_method = get_start_method(allow_none=True)

        if not start_method:
            set_start_method("spawn")

        # if osx and not spawn then error
        elif start_method != "spawn":
            raise Exception("Integration error: start method must be spawn on osx")


    # Different OSes have different ways to get the window to the top of the z-order
    @contextmanager
    def _toplevel_window():
        # Make a top-level instance and hide since it is ugly and big.
        root = Tk()

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f"{screen_width}x{screen_height}")


        if SYS_NAME.startswith("darwin"):
            # OSX-dependent from https://stackoverflow.com/questions/19080499/transparent-background-in-a-tkinter-window
            # Turn off the window shadow
            root.wm_attributes("-transparent", True)
            # Set the root window background color to a transparent color
            root.config(bg='systemTransparent')

            # Cocoa-based incantation to raise the app window to the top
            import os
            from Cocoa import NSRunningApplication, NSApplicationActivateIgnoringOtherApps
            app = NSRunningApplication.runningApplicationWithProcessIdentifier_(os.getpid())
            app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
        elif SYS_NAME.startswith('linux'):
            root.wait_visibility(root)

        root.wm_attributes("-alpha", 0.01)

        # Show window again and lift it to top so it can get focus,
        # otherwise dialogs will end up behind the terminal.
        root.deiconify()
        root.lift()
        root.attributes('-topmost',True)
        root.after_idle(root.attributes,'-topmost',False)
        root.focus_force()

        yield root

        root.destroy()

    def _open_file_dialog(fn, initial_dir=os.path.expanduser('~'), title = None, file_types=None):
        # If the initial dir isn't a directory, then askopenfilename will default to the cwd, which isn't helpful
        if not os.path.isdir(initial_dir):
            initial_dir = "~"
        initial_dir = os.path.expanduser(initial_dir)
        file_types = file_types or []
        title = title or "Choose a File"

        with _toplevel_window() as root:
            filename = fn(parent=root, initialdir=initial_dir, title=title, filetypes=file_types)
            return filename or None

    def open_file_dialog(initial_dir="~", title=None, file_types=None):
        _set_start_method()

        # tkinter requires that you open the dialog from the main thread
        # We're in a server, so we need to spawn a process for that.
        if file_types:
            file_types = list(file_types)
        return run_on_main_thread(
            _open_file_dialog,
            filedialog.askopenfilename,
            initial_dir=initial_dir,
            title=title,
            file_types=file_types
        )

    def open_saveas_dialog(initial_dir="~", title=None, file_types=None):
        _set_start_method()

        # tkinter requires that you open the dialog from the main thread
        # We're in a server, so we need to spawn a process for that.
        if file_types:
            file_types = list(file_types)
        return run_on_main_thread(
            _open_file_dialog,
            filedialog.asksaveasfilename,
            initial_dir=initial_dir,
            title=title,
            file_types=file_types
        )

    def _open_directory_dialog(initial_dir=os.path.expanduser('~'), title = None, file_types=None):
        # If the initial dir isn't a directory, then askopenfilename will default to the cwd, which isn't helpful
        if not os.path.isdir(initial_dir):
            initial_dir = "~"
        initial_dir = os.path.expanduser(initial_dir)
        title = title or "Choose a Directory"

        with _toplevel_window() as root:
            ret = filedialog.askdirectory(parent=root, initialdir=initial_dir, title=title)
            return ret or None

    def open_directory_dialog(initial_dir="~", title=None, file_types=None):
        _set_start_method()

        # tkinter requires that you open the dialog from the main thread
        # We're in a server, so we need to spawn a process for that.
        return run_on_main_thread(_open_directory_dialog, initial_dir=initial_dir, title=title)
