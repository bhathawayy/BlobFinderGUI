cd %0\..\..\..
call venv\Scripts\activate.bat
call python -m blob_detection.widget -n 0
call venv\Scripts\deactivate.bat
exit