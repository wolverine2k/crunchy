cd ..\branches\bryan
setup.py py2exe

rem The 'dist' directory must not exist
move dist ..\..\release

rem Cannot remove build directory?
rem rmdir /S build

cd ..\..\release
"%PROGRAMFILES%/Inno Setup 5/compil32" /cc "crunchy.iss"