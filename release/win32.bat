cd ..\branches\bryan
setup.py py2exe

cd ..\..\release
"%PROGRAMFILES%/Inno Setup 5/compil32" /cc "crunchy.iss"

rem Batch scripts have trouble removing directories so the win32 directory is not deleted