@echo off

set "foldername=%cd%"
set "foldername=%foldername:~-8%"

if "%foldername%" == "filtered" (
    for %%f in (*.py) do (
        strip-hints --inplace %%f
        @REM start "" strip-hints --inplace %%f
    )
) else (
    if "%foldername%" == "hpappdir" (
        for %%f in (*.py) do (
            strip-hints --inplace %%f
            @REM start "" strip-hints --inplace %%f
        )
    ) else (
        echo "Warning: Current folder is not named 'filtered', script will not run."
        pause
        exit
    )
)
pause