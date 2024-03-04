@echo off
setlocal enabledelayedexpansion

:: Python plugins directory
set "gimpPluginsDir=C:\Program Files\GIMP 2\lib\gimp\2.0\plug-ins"

:: Get the current directory of the batch script
set "scriptDir=%~dp0"

:: Ensure path ends with a backslash
if not "!scriptDir:~-1!"=="\" set "scriptDir=!scriptDir!\"

:: Loop through each folder in the current directory with the prefix "jdl-"
for /d %%d in (jdl-*) do (
    :: Construct the target path
    set "folderName=%%d"
    set "targetPath=!scriptDir!!folderName!"
    set "copyPath=!gimpPluginsDir!\!folderName!"

    :: Warn if the folder already exists
    set "overwrite="
    if exist "!copyPath!" (
        set "overwrite= (Overwritten)"
    )

    :: Print the operation details
    echo Input  "!targetPath!"
    echo Output "!copyPath!" !overwrite!

    :: Execute the copy operation without showing any robocopy output, but check for errors
    robocopy "!targetPath!" "!copyPath!" /MIR /COPYALL /R:5 /W:2 /NFL /NDL /NS /NC /NP > nul 2>&1
    set "exitCode=%ERRORLEVEL%"

    :: Check the exit code for errors (codes 8 to 16 indicate an error)
    if !exitCode! GEQ 8 (
        echo Error occurred during copying. Error Level: !exitCode!
    )
)

endlocal