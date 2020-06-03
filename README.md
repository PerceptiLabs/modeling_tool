# PerceptiLabs Modeling Tool

This is the main repo for the modeling tool, including the ML kernel,
frontend, and rygg

# Adding new files to the backend build

All files that should be a part of the build (usually, everything except tests) must be added to one of:

*  scripts/included_files_common.txt (most files)
*  scripts/included_files_test.txt   (files just needed for tests)
*  scripts/included_files_docker.txt (files just needed for the docker build
*  scripts/included_files_wheel.txt  (files just needed for the pip package)


# Adding new Python dependencies

Dependencies must be declared in:

* Docker/Core/requirements.txt
* backend/requirements_wheel_backend.txt
* backend/requirements_posix_testing.txt
* backend/requirements_posix_common.txt
* backend/requirements_windows.txt
* backend/requirements_docker.txt
* backend/requirements_pip_windows.txt

(yes, they're in need of some organization)
