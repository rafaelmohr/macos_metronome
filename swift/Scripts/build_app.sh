#!/bin/bash
# Assembles a distributable Metronome.app from a release build, replacing
# `python setup.py py2app` from the Python version. Run from anywhere; paths
# below are relative to the swift/ package root.
set -euo pipefail
cd "$(dirname "$0")/.."

APP_NAME="Metronome"
BUNDLE_ID="com.rafaelmohr.metronome"
BUILD_DIR=".build/release"
DIST_DIR="dist"
APP_BUNDLE="$DIST_DIR/$APP_NAME.app"
ICON_SOURCE="../icon.icns"

echo "Building release binary..."
swift build -c release

rm -rf "$DIST_DIR"
mkdir -p "$APP_BUNDLE/Contents/MacOS" "$APP_BUNDLE/Contents/Resources"

cp "$BUILD_DIR/$APP_NAME" "$APP_BUNDLE/Contents/MacOS/$APP_NAME"
cp "$ICON_SOURCE" "$APP_BUNDLE/Contents/Resources/icon.icns"

# Bundle resources SwiftPM produced (the two .wav files) into the app.
RESOURCE_BUNDLE=$(find "$BUILD_DIR" -maxdepth 1 -name "*.bundle" | head -n1)
if [ -n "$RESOURCE_BUNDLE" ]; then
  cp -R "$RESOURCE_BUNDLE" "$APP_BUNDLE/Contents/Resources/"
fi

cat > "$APP_BUNDLE/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>CFBundleIdentifier</key>
    <string>$BUNDLE_ID</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>14.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.music</string>
</dict>
</plist>
PLIST

# Ad-hoc sign so Gatekeeper and the Dock icon behave like a normal local app.
codesign --force --deep --sign - "$APP_BUNDLE"

echo "Built $APP_BUNDLE"
