# Adding new files to the backend build

All files that should be a part of the build (usually, everything except tests) must be added to the backend/included_files.txt


# Adding new Python dependencies

Dependencies must be declared in:

* backend/setup.py
* backend/requirements.txt [windows]
* backend/requirements_linux.txt
* backend/requirements_osx.txt
* Docker/Core/requirements.txt


