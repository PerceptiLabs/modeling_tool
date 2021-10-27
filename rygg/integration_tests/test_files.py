import os
import platform
import pytest

def test_file_chooser(rest):
    if rest.is_enterprise:
        with pytest.raises(Exception, match="404"):
            rest.get("/files/pick_file", initial_dir="~")
    else:
        file_types = '[{"name": "csv file", "extensions": ["*.csv"]}]'
        rest.get("/files/pick_file", initial_dir=os.getcwd(), title="testing title", file_types=file_types)

def test_saveas_chooser(rest):
    if rest.is_enterprise:
        with pytest.raises(Exception, match="404"):
            rest.get("/files/saveas_file", initial_dir="~")
    else:
        file_types = '[{"name": "csv file", "extensions": ["*.csv"]}]'
        rest.get("/files/saveas_file", initial_dir=os.getcwd(), title="testing title", file_types=file_types)
