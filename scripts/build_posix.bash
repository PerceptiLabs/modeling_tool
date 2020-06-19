#!/usr/bin/env bash

test -z "$1" && { echo "USAGE: $0 <target>"; exit 1; }
BUILD_TYPE="$1"

# Set the defaults for some variables. You can override them.
: "${PROJECT_ROOT:=$(dirname $(pwd))}"

BACKEND_SRC_ROOT=${PROJECT_ROOT}/backend
FRONTEND_SRC_ROOT=${PROJECT_ROOT}/frontend
RYGG_ROOT=${PROJECT_ROOT}/rygg
BUILD_DIR=${PROJECT_ROOT}/build
BUILD_TMP=${BUILD_DIR}/tmp
SCRIPTS=${PROJECT_ROOT}/scripts

get_os(){
  case "${OSTYPE}" in
    *darwin*) echo "osx" ;;
    *linux*) echo "linux" ;;
    *) echo "OS '${OSTYPE}' isn't supported"; return 1 ;;
  esac
  return 0
}

: "${OS:=$(get_os)}"
echo "Building for ${OS}"

# OSX's built-in sed is non-compliant. Use gnu sed.
get_sed(){
  case "${OS}" in
    osx) echo "gsed" ;;
    *) echo "sed" ;;
  esac
  return 0
}
: "${SED:=$(get_sed)}"

pushd_q(){ pushd "${1}" &>/dev/null; }
popd_q(){ popd &>/dev/null; }

maybe_set_up_linux(){
  test "${OS}" = "linux" || return 0

  echo "Installing gcc..."
  sudo apt install tree gcc -y || { exit 1; }

  echo "Installing node..."
  curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash - || { exit 1; }
  sudo apt-get install -y nodejs || { exit 1; }
}

set_up(){
  maybe_set_up_linux
  maybe_set_up_osx

  echo "======================================================="
  echo "Installing requirements..."
  python -m pip install --upgrade pip setuptools || { exit 1; }
  pip install -r ${BACKEND_SRC_ROOT}/requirements_posix_common.txt || { exit 1; }

  # Install os-specific packages
  test -f ${BACKEND_SRC_ROOT}/requirements_${OS}.txt && 
    pip install -r ${BACKEND_SRC_ROOT}/requirements_${OS}.txt

  echo "Installing npm packages"
  pushd_q ${FRONTEND_SRC_ROOT}
  npm install || { exit 1; }
  popd_q
}

assert_python_version(){
  py_ver=$(python --version 2>&1)
  echo ${py_ver} | grep -q "3\(\.[0-9]\+\)\+" || {
    echo "Wrong python version (${py_ver}). Have you set up your virtualenv?";
    exit 1
  }

  echo $(pip --version) | grep -q "3\.[67]" || {
    echo "Wrong pip version ($(pip --version)). Have you set up your virtualenv?";
    exit 1
  }
}

print_environment(){
  echo "======================================================="
  echo "Environment: "
  echo "Python location: $(which python)"
  echo "node.js version: $(node --version)"
  echo "npm version: $(npm --version)"

  echo "Pip list:"
  pip list
}

train_models(){
  echo "======================================================="
  echo -n "Training models ..."
  pushd_q ${BACKEND_SRC_ROOT}/perceptilabs/insights/csv_ram_estimator/
  python train_model.py data_1579288530.csv &>/dev/null || { echo "failed"; exit 1; }
  popd_q
  echo "done"
}

clean_build_dirs(){
  echo "======================================================="
  echo "Cleaning up build directory"
  rm -rf ${BUILD_DIR}
}

assemble_build_dirs_common(){
  echo "======================================================="
  echo -n "Copying files into ${BUILD_TMP} ... "

  mkdir -p ${BUILD_TMP}
  rsync --archive ${PROJECT_ROOT} --files-from=${SCRIPTS}/included_files_common.txt ${BUILD_TMP} || { exit 1; }
  rsync --archive ${PROJECT_ROOT} --files-from=${SCRIPTS}/included_files_${BUILD_TYPE}.txt ${BUILD_TMP} || { exit 1; }

  # pull subdirs up a level
  for subdir in wheelfiles rygg backend; do
    mv ${BUILD_TMP}/${subdir} ${BUILD_TMP}/todo_remove
    mv ${BUILD_TMP}/todo_remove/* ${BUILD_TMP}
    rmdir ${BUILD_TMP}/todo_remove
  done

  echo done
}

assemble_build_dirs_frontend(){
  echo "======================================================="
  echo -n "Copying frontend files into ${BUILD_TMP} ... "
  rsync --archive ${PROJECT_ROOT} --recursive --files-from=${SCRIPTS}/included_files_frontend.txt ${BUILD_TMP} || { exit 1; }

  mv ${BUILD_TMP}/frontend/static_file_server/static_file_server ${BUILD_TMP}/static_file_server

  mkdir ${BUILD_TMP}/static_file_server/dist
  cp -r ${BUILD_TMP}/frontend/src/dist/* ${BUILD_TMP}/static_file_server/dist
  
  rm -r ${BUILD_TMP}/frontend/*
  rmdir ${BUILD_TMP}/frontend

  echo done
}

set_wheel_version(){
  # for nightly builds, add the date string to the version
  version=$(cat ${PROJECT_ROOT}/wheelfiles/version)
  test "${BUILD_REASON}" = "Schedule" && version=${version}.${BUILD_NUM}
  echo "version: ${version}"
  if [ ! -z "${PACKAGE_VERSION_OVERRIDE}" ]; then
    version="${PACKAGE_VERSION_OVERRIDE}"
  fi
  ${SED} -i "s/^__version__ *=.*/__version__=\"$version\"/g" ${BUILD_TMP}/perceptilabs/__init__.py
  ${SED} -i "s/^VERSION_STRING.*/VERSION_STRING=\"$version\"/g" ${BUILD_TMP}/setup.py
  echo "Set wheel version: ${version}"
}

set_wheel_extension(){
  # for nightly builds, rename the package
  if [ "${BUILD_REASON}" = "Schedule" ]; then
    ${SED}  -i 's/^PACKAGE_NAME *= *"\(.*\)"$/PACKAGE_NAME="\1-nightly"/g' ${BUILD_TMP}/setup.py
  fi

  # If we've forced the package name, then just put that in there.
  if [ ! -z "${PACKAGE_NAME_OVERRIDE}" ]; then
    ${SED}  -i "s/^PACKAGE_NAME *=.*$/PACKAGE_NAME='${PACKAGE_NAME_OVERRIDE}'/g" ${BUILD_TMP}/setup.py
  fi
}

build_wheel(){

  echo "======================================================="
  for file in linreg_inputs linreg_outputs linreg_outputs_test mnist_input mnist_labels; do
    cp ${BACKEND_SRC_ROOT}/perceptilabs/tutorial_data/${file}.npy ${BUILD_TMP}/perceptilabs
  done

  echo "Listing files to be included in build (contents of 'tmp/')"
  tree ${BUILD_TMP}

  pushd_q ${BUILD_TMP}
  python setup.py build_ext bdist_wheel || { exit 1; }
  popd_q

  # ----- Set up the output ----
  BUILD_OUT=${BUILD_DIR}/out
  mkdir -p ${BUILD_OUT}
  cp ${BUILD_TMP}/dist/* ${BUILD_OUT}

  # ----- Test installation ----
  pip uninstall -y perceptilabs
  pip install perceptilabs --find-links ${BUILD_OUT} || { exit 1; }
  python -c "import perceptilabs" || { exit 1; }
}

maybe_build_core_docker(){
  test -z "${DO_DOCKER_BUILD}" && {
    echo "You can now run docker build";
    return 0;
  }

  pushd_q ${BUILD_TMP}
  docker build . --tag=core_quickcheck
  popd_q
  docker run -p 5000:5000 core_quickcheck || { exit 1; }

}

assemble_frontend_docker(){
  frontend_tmp=${BUILD_DIR}/frontend_out

  cp -r ${FRONTEND_SRC_ROOT}/src/dist/* $frontend_tmp

  ls -l -a ${PROJECT_ROOT}/Docker/Frontend
  cp -r ${PROJECT_ROOT}/Docker/Frontend/. $frontend_tmp
}

build_frontend(){
  echo "======================================================="
  echo -n "Building frontend"

  pushd_q ${FRONTEND_SRC_ROOT}
  npm run build-render || { exit 1; }
  popd_q
}

set_up_for_tests(){
  echo "Installing requirements..."
  python -m pip install --upgrade pip setuptools || { return 1; }
  pip install -r ${BACKEND_SRC_ROOT}/requirements_posix_testing.txt || { return 1; }
}

run_lint_test(){
  echo "running pylint"
  pushd_q ${PROJECT_ROOT}
  python ${SCRIPTS}/test_pylint.py ${SCRIPTS}/included_files_common.txt || { exit 1; }
  rm ${BUILD_TMP}/test_pylint.py
  popd_q
}

run_cython_test(){
  cp ${SCRIPTS}/test_cython.py ${BUILD_TMP}

  echo "Running cython tests"
  pushd_q ${BUILD_TMP}
  python --version

  # TODO: this fails. Do we keep it?
  python ${SCRIPTS}/test_cython.py # || { exit 1; }
  rm ${BUILD_TMP}/test_cython.py
  popd_q
}

run_pytest_tests(){
  echo "Running python tests"
  pushd_q ${BACKEND_SRC_ROOT}
  python -m pytest --capture=no || { exit 1; }
  popd_q
}

assert_python_version

case "$1" in
  wheel)
    set_up
    print_environment
    train_models
    clean_build_dirs
    build_frontend
    assemble_build_dirs_common
    assemble_build_dirs_frontend
    set_wheel_version
    set_wheel_extension
    build_wheel
    ;;
  docker)
    set_up
    print_environment
    train_models
    clean_build_dirs
    build_frontend
    assemble_build_dirs_common
    assemble_core_docker
    maybe_build_core_docker
    assemble_frontend_docker
    ;;
  test)
    set_up_for_tests
    print_environment
    train_models
    clean_build_dirs
    assemble_build_dirs_common
    run_lint_test
    run_cython_test
    run_pytest_tests
    ;;
  *)
    echo "build type '$1' isn't supported";
    return 1
    ;;
esac


