@echo off
setlocal enabledelayedexpansion

:: Define the default Python plugins directory
set "defaultDir=C:\Program Files\GIMP 2\lib\gimp\2.0\plug-ins"

:: Prompt the user for the Python plugins directory, showing the default
echo Provide Gimp Python plugins directory. (Press Enter to default to [%defaultDir%])
set /p "gimpPluginsDir=Directory: "

:: If user input is empty, use the default directory
if "!gimpPluginsDir!"=="" set "gimpPluginsDir=%defaultDir%"

:: Get the current directory of the batch script
set "scriptDir=%~dp0"

:: Ensure path ends with a backslash
if not "!scriptDir:~-1!"=="\" set "scriptDir=!scriptDir!\"

:: Loop through each folder in the current directory with the prefix "jdl-"
for /d %%d in (jdl-*) do (
    :: Construct the target path
    set "folderName=%%d"
    set "targetPath=!scriptDir!!folderName!"
    set "linkPath=!gimpPluginsDir!\!folderName!"

    :: Check if the symbolic link or directory already exists at the target location
    if exist "!linkPath!" (
        echo [Warning] Link already exists: "!linkPath!"
    ) else (
        :: If it doesn't exist, create the symbolic link
        mklink /D "!linkPath!" "!targetPath!"
    )
)

endlocal