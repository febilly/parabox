@echo off

set "foldername=%cd%"
set "foldername=%foldername:~-8%"

if "%foldername%" == "filtered" (
    del hpprime.py
    del auto_test.py
    for %%f in (*.py) do (
        strip-hints --inplace %%f
        @REM start "" strip-hints --inplace %%f
    )
) else (
    if "%foldername%" == "hpappdir" (
        del hpprime.py
        del auto_test.py
        for %%f in (*.py) do (
            strip-hints --inplace %%f
            @REM start "" strip-hints --inplace %%f
        )
    ) else (
        echo "Warning: Current folder's name is not 'filtered' or ends with 'hpappdir'. script will not run."
        pause
        exit
    )
)
pause