@echo off
setlocal
set "VERSION=8.11.1"
set "GRADLE_HOME=%~dp0.gradle\bootstrap\gradle-%VERSION%"
if not exist "%GRADLE_HOME%\bin\gradle.bat" (
  powershell -NoProfile -Command "$ErrorActionPreference='Stop'; $p='%~dp0.gradle\bootstrap'; New-Item -ItemType Directory -Force -Path $p | Out-Null; Invoke-WebRequest -Uri 'https://services.gradle.org/distributions/gradle-8.11.1-bin.zip' -OutFile ($p+'\gradle.zip'); Expand-Archive -Path ($p+'\gradle.zip') -DestinationPath $p -Force; Remove-Item ($p+'\gradle.zip')"
  if errorlevel 1 exit /b 1
)
call "%GRADLE_HOME%\bin\gradle.bat" %*
