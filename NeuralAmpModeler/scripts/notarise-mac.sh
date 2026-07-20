#!/bin/sh -e

#============================================================
# Notarise a .app, .component (AU), .vst3, .pkg, or .dmg using notarytool.
#
# Replaces iPlug2/Scripts/notarise.sh, which used `xcrun altool
# --notarize-app` -- Apple shut down altool's notarization service in
# November 2023, so that script no longer works. This one uses
# `notarytool` and a keychain-stored credential profile instead of
# passing an Apple ID/app-specific password on the command line.
#
# Before running this script:
#   1. Code-sign the bundle with hardened runtime + a secure timestamp:
#      codesign --force -s "$SIGN_ID" -v "$BUNDLE" --deep --strict --options=runtime --timestamp
#   2. One-time setup -- store your Apple ID + app-specific password in
#      the keychain under a profile name (interactive, hidden prompt):
#      xcrun notarytool store-credentials "<profile>" --apple-id "<apple-id>" --team-id "<team-id>"
#------------------------------------------------------------
#  arg 1  Absolute path where the script's tmp dir should be created
#  arg 2  Absolute path to the .app / .component / .vst3 / .pkg / .dmg to notarise
#  arg 3  Keychain profile name (as passed to `notarytool store-credentials`)
#------------------------------------------------------------

ROOT="$1"
BUNDLE_PATH="$2"
KEYCHAIN_PROFILE="$3"

if [ -z "$ROOT" ]; then
  echo "ERROR: First arg needs to be the absolute path where the script should run" && exit 1
fi

if [ -z "$BUNDLE_PATH" ]; then
  echo "ERROR: Second arg needs to be the path to the .app/.component/.vst3/.pkg/.dmg to notarise" && exit 1
fi

if [ -z "$KEYCHAIN_PROFILE" ]; then
  echo "ERROR: Third arg needs to be the notarytool keychain profile name" && exit 1
fi

if [ ! -e "$BUNDLE_PATH" ]; then
  echo "ERROR: $BUNDLE_PATH does not exist" && exit 1
fi

cd "$ROOT"

TMP="$ROOT/notarise-tmp"
rm -rf "$TMP"
mkdir "$TMP"

function onExit {
  rm -rf "$TMP"
}
trap onExit EXIT

BUNDLE_NAME=$(basename "$BUNDLE_PATH")
EXTENSION="${BUNDLE_NAME##*.}"

# pkg/dmg can be submitted as-is; anything else (.app/.component/.vst3/a bare
# executable) needs to be zipped first -- the Notary API only accepts
# zip/pkg/dmg, not arbitrary bundle directories.
if [ "$EXTENSION" = "pkg" ] || [ "$EXTENSION" = "dmg" ]; then
  SUBMIT_PATH="$BUNDLE_PATH"
else
  echo "============================================================"
  echo "Verifying signature before submitting:"
  codesign -dvv "$BUNDLE_PATH"
  codesign -vvv --deep --strict "$BUNDLE_PATH"

  SUBMIT_PATH="$TMP/$BUNDLE_NAME.zip"
  /usr/bin/ditto -c -k --keepParent "$BUNDLE_PATH" "$SUBMIT_PATH"
fi

echo "============================================================"
echo "Submitting to notary service: $SUBMIT_PATH"

SUBMIT_LOG="$TMP/submit.log"
if xcrun notarytool submit "$SUBMIT_PATH" --keychain-profile "$KEYCHAIN_PROFILE" --wait | tee "$SUBMIT_LOG"; then
  :
else
  echo "ERROR: notarytool submit failed to run" && exit 1
fi

SUBMISSION_ID=$(grep -m1 '^  id:' "$SUBMIT_LOG" | awk '{print $2}')
STATUS=$(grep -m1 '^  status:' "$SUBMIT_LOG" | awk '{print $2}')

if [ "$STATUS" != "Accepted" ]; then
  echo "============================================================"
  echo "ERROR: notarization status was '$STATUS', not 'Accepted'. Fetching log:"
  if [ -n "$SUBMISSION_ID" ]; then
    xcrun notarytool log "$SUBMISSION_ID" --keychain-profile "$KEYCHAIN_PROFILE"
  fi
  exit 1
fi

echo "============================================================"
echo "Stapling notarization ticket to $BUNDLE_PATH"
xcrun stapler staple "$BUNDLE_PATH"
xcrun stapler validate "$BUNDLE_PATH"

echo "============================================================"
echo "Done: $BUNDLE_PATH is notarized and stapled."
