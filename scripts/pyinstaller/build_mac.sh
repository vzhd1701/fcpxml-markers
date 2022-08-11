#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname $0 )" && pwd )"

. "scripts/init_app_vars.sh"

PYINSTALLER_VERSION="5.1"

BUILD_DIR_PI="$BUILD_DIR/pyinstaller"
mkdir -p "$BUILD_DIR_PI"

cd "$BUILD_DIR_PI"

download_gifsicle() {
    # get binary from the earliest bottle
    for os_ver in "mojave" "catalina" "big_sur" "monterey"; do
        BOTTLE_URL=$(curl -s "https://formulae.brew.sh/api/bottle/gifsicle.json" | sed 's/.*"'$os_ver'":{"url":"\([^"]\+\)".*/\1/')
        [ -n "$BOTTLE_URL" ] && break
    done

    curl -s -L -H "Authorization: Bearer QQ==" -o bottle.tar.gz "$BOTTLE_URL"
    mkdir -p bottle && tar xf bottle.tar.gz --directory=bottle
    mv -f bottle/gifsicle/1.*/bin/gifsicle "$BUILD_DIR_PI"
    rm -rf bottle*
}

echo "Downloading gifsicle binary"
download_gifsicle

init_venv "$BUILD_DIR_PI/venv-pyinstaller"

pip install -r "$BUILD_DIR/requirements.txt"
pip install pyinstaller=="$PYINSTALLER_VERSION"

pyinstaller \
    --workpath "$BUILD_DIR_PI" \
    --distpath "$DIST_DIR" \
    --ascii --clean --noconfirm \
    --onedir --console --noupx \
    --name "$APP_NAME" \
    --osx-bundle-identifier "$APP_ID" \
    --add-binary "$BUILD_DIR_PI/gifsicle:." \
    --add-data "$ROOT_DIR/$APP_MODULE/custom_fpcxml_adapter:custom_fpcxml_adapter" \
    --collect-all "opentimelineio" \
    --collect-all "opentimelineio_contrib" \
    "$ROOT_DIR/$APP_MODULE/__main__.py"
