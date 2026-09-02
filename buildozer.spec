[app]
title = GestureVoice Pro
package.name = gesturevoicepro
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json
source.exclude_dirs = .git,.buildozer,bin,venv,.venv,__pycache__
version = 0.2.1
requirements = python3,kivy==2.3.1,kivymd==1.2.0
orientation = portrait
fullscreen = 0

# Esta versão unificada ainda não usa câmera/microfone.
# Portanto não solicita permissões desnecessárias.
android.api = 36
android.minapi = 21
android.ndk = 28c
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 0
