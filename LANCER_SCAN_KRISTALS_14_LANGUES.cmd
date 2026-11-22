@echo off
setlocal
set "DIK_DIR=%~dp0"
set "KRISTALS_ROOT=C:\mycode"
if not exist "%KRISTALS_ROOT%\" (
    echo ERREUR: le dossier %KRISTALS_ROOT% est introuvable.
    pause
    exit /b 2
)
pushd "%DIK_DIR%" || exit /b 2
set "PYTHONPATH=%DIK_DIR%src"
echo.
echo === diK : AUDIT LOCAL DE TOUS LES KRISTALS x 14 LANGUES ===
echo Sources : %KRISTALS_ROOT%
echo Rapports : %DIK_DIR%reports\scans_14_langues
echo.
py -3 -m dik coverage kristals14 --root "%KRISTALS_ROOT%" --dik-root "%DIK_DIR%"
set "EXIT_CODE=%ERRORLEVEL%"
popd
echo.
if not "%EXIT_CODE%"=="0" echo Audit interrompu : code %EXIT_CODE%.
if "%EXIT_CODE%"=="0" echo Audit termine. Voir la synthese JSON et le dossier de rapports ci-dessus.
pause
exit /b %EXIT_CODE%
