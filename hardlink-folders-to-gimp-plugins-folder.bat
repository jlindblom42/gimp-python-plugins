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