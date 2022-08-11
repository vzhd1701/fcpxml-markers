#!/bin/bash

die() {
    printf '%s\n' "$*" >&2
    exit 1
}

if ! command -v realpath &> /dev/null; then
    realpath() {
        [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
    }
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
  function sed() { command gsed "$@"; }
fi

replace_app_vars() {
    TARGET_FILE="$1"

    [ ! -f "$TARGET_FILE" ] && return

    VARS=$(env | cut -d '=' -f1 | grep "^APP_")

    while IFS= read -r var; do
        eval replace='$'$var

        [ -z "$replace" ] && die "$var variable is empty!"

        sed -i "s#{$var}#$replace#g" "$TARGET_FILE"
    done <<< "$VARS"
}

copy_with_app_vars() {
    SOURCE_FILE="$1"
    DESTINATION="$2"

    if [ -d "$DESTINATION" ]; then
        DEST_FILE="$(realpath $DESTINATION)/$(basename $SOURCE_FILE)"
    else
        DEST_FILE="$DESTINATION"
    fi

    cp "$SOURCE_FILE" "$DEST_FILE"
    replace_app_vars "$DEST_FILE"
}

init_venv() {
    VENV_DIR="$1"

    if which python3 >/dev/null; then
        python_cmd=python3
    else
        python_cmd=python
    fi

    if [ ! -d "$VENV_DIR" ]; then
        $python_cmd -m venv "$VENV_DIR"

        activate_venv "$VENV_DIR"

        python -m pip install --upgrade pip
    else
        activate_venv "$VENV_DIR"
    fi
}

activate_venv() {
    VENV_DIR="$1"

    if [ -f "$VENV_DIR/Scripts/activate" ]; then
        . "$VENV_DIR/Scripts/activate"
    else
        . "$VENV_DIR/bin/activate"
    fi
}

export ROOT_DIR="$(realpath $(pwd))"

export RESOURCES_DIR="$ROOT_DIR/resources"
export BUILD_DIR="$ROOT_DIR/build"
export DIST_DIR="$ROOT_DIR/dist"
export SCRIPTS_DIR="$ROOT_DIR/scripts"

export APP_MODULE="fcpxml_markers"
export APP_BASE_DIR=$(realpath "./$APP_MODULE")

export APP_NAME="fcpxml-markers"
export APP_ID="com.vzhd1701.fcpxmlmarkers"
export APP_VERSION=$(sed -n 's/__version__ = "\([^"]*\).*/\1/p' "$APP_BASE_DIR/version.py")
