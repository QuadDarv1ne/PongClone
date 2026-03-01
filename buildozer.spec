[app]

# (str) Title of your application
title = Enhanced Pong

# (str) Package name
package.name = enhancedpong

# (str) Package domain (needed for android/ios packaging)
package.domain = org.pongclone

# (str) Source code where the main.py live
source.dir = PyPong

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,wav,ogg,mp3,json,md

# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,pygame_sdl2

# (str) Supported orientation (landscape, portrait or all)
orientation = landscape

# (str) Presplash background color (for new android toolchain)
android.presplash_color = #808080

# (str) Icon of the application
#android.icon.filename = %(source.dir)s/data/icon.png

# (str) Presplash of the application
#android.presplash.filename = %(source.dir)s/data/presplash.png

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (string) Presplash background color (for old android toolchain)
#android.presplash_color = #FFFFFF

# (list) Permissions
android.permissions = INTERNET,VIBRATE,WRITE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 23b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a,armeabi-v7a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .ipa) storage
bin_dir = ./bin
