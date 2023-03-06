@ECHO OFF
call C:/Users/jb/miniconda3/Scripts/activate.bat
cd %~dp0
call conda activate herobook
streamlit run app.py --server.port 8340
call conda deactivate
pause