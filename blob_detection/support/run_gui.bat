cd %0\..\..\..
call venv\Scripts\activate.bat
call python -m blob_detection.ui_widget
call venv\Scripts\deactivate.bat
exit