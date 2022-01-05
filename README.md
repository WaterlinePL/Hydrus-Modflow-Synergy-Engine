# Hydrus-Modflow Synergy Engine - AGH WATER MODELING
This repository is an engineering project that is also a part of WATERLINE project. 
Please refer to the README.md file on the main branch for general information about the project and a tutorial.

## Welcome to the desktop branch
This branch serves as a repository for desktop deployment. It is preconfigured for launching desktop version of HMSE. 

### Create executable of the application
In order to create the executable of the application PyInstaller is required.
Command with sample paths would look like the one bellow:
```
pyinstaller --onedir 
--paths "<your path to repository>\water_modelling\server" 
--add-data "<your path to repository>\water_modelling\server\templates;templates" 
--add-data "<your path to repository>\water_modelling\server\static;static" 
--add-data "<your path to repository>\venv\Lib\site-packages\flopy\export\longnames.json;flopy\export" 
--add-data "<your path to repository>\venv\Lib\site-packages\flopy\export\unitsformat.json;flopy\export" 
<your path to repository>\water_modelling\server\main.py
```

### Run application
* For devs: launch `main.py` from PyCharm, can be used with debugger
* App can be also run from executable (after creating one)

**Access the application from web browser under `localhost:5000`.**

