# This repository is DEPRECATED - it will no longer be maintained!

# Hydrus-Modflow Synergy Engine - AGH WATER MODELING
This is the repository of the HMSE application, a thesis project aiming
to combine the functionalities of the Hydrus and Modflow simulation programs. 

## Welcome to the master branch
This branch serves as a repository for common components that are used by every deployment. 
So far, three deployments have been created:
* `desktop`
* `docker`
* `kubernetes`

Each deployment is located on a separate branch, with the same name as the deployment.
The branches have been preconfigured in the `water_modelling/app_config/deployment_config.py` file
to ease testing, launching and mitigate problems with changing deployment config while committing 
to a single branch.

### Important
* For application to run properly, it is required to have *cookies* enabled in the web browser.
* Sample projects are located in the `sample` folder. **TESTS SHOULD NOT BE RUN ON PROJECTS FROM THE `sample` FOLDER**.
Instead, they should be copied to a new `tests` folder using scripts.
	+ Linux script: scripts/copy_projects.sh (suggested)
	+ Windows 10 script: scripts/copy_projects.ps (requires enabled Powershell scripts)
	+ For further information refer to the comments in the scripts.
* Hydrus and Modflow projects used in Docker and Kubernetes deployment **MUST** be named in lowercase. Uppercase
symbols are not allowed due to Docker and Kubernetes naming policy

### Assumed workflow
* if a new feature relates to every deployment:
  + create a pull request to `master`
  + after merging the PR, rebase the other branches to `master` - while on another branch,
    use `git fetch origin master:master` and then `git rebase master`
* if a new feature relates to only one deployment - create a pull request to that deployment's branch
* if a new feature relates to more than one deployment - create a separate pull request for each branch

More detailed README files are located on the deployments' branches.


### Environment Configuration For Developers
Application was tested on two Python versions: 3.8 and 3.9. 
#### Pycharm configuration
It is necessary to set **water_modelling** directory as **Source** in project settings.
 
![Project Config](water_modelling/sample/screenshots/project_config.PNG)

#### Line Separators
Additional changes apply to line separators. Due to some .sh scrips, they need to be set to LF. 
Those files are prepared for Docker and Kubernetes versions running on linux os. Click
[here](https://www.jetbrains.com/help/idea/configuring-line-endings-and-line-separators.html) for further instruction.
#### Run/Debug Configuration
Provide correct main.py *Run and Debug Configuration* as presented below.

![Run/Debug Config](water_modelling/sample/screenshots/run_debug_config.PNG)

### Repository structure
* **hydrus_docker** - contains data related to the Docker image we created for Hydrus (hydrus executable compiled
from this [repository](https://github.com/AgriHarmony/HYDRUS-1-D-gfortran)
* **k8s** - deployment-related Kubernetes YAML manifests, as well as debug manifests
* **scripts** - bash and PowerShell (not recommended) scripts for building and pushing Docker images, as well 
as for creating test data inside `water_modelling`
* **water_modelling** - the main application. Contains the following packages:
  + `app_config` - deployment settings, modified on each deployment's branch
  + `datapassing` - logic related to passing Hydrus simulation outputs into the Modflow model 
  + `deployment` - deployers for each deployment (desktop, Docker and Kubernetes)
  + `hydrus` - logic related to launching Hydrus simulations
  + `kubernetes_controller` - logic related to monitoring kubernetes jobs (simulations are 
  launched as kubernetes jobs inside a cluster)
  + `modflow` - logic related to launching Modflow simulations
  + `sample` - sample data meant to be copied and used for tests (there is a script that makes a `tests` folder 
  with content from `sample`)
  + `server` - core logic (project management, simulation configuration, weather file upload)
  and web application components (endpoints, states, page templates and their javascript
  functionalities)
  + `simulation` - simulation management (launching Hydrus -> data passing -> launching Modflow)
  + `workspace` - storage space for all created projects (content is .gitignore`d)


### Simulation input files
#### Uploading Modflow/Hydrus models
Models must be uploaded as archives with correct structure. You need to provide it in a **.zip archive,
with the model files placed directly in the root**.

#### Uploading Weather Data
You can optionally modify a Hydrus model with meteorological data. This is done by uploading a **properly
structured .csv file**.

The file **must** contain the following columns:
* `Latitude` - latitude in Decimal Degrees (DD) format
* `Elevation` - elevation over the sea level (altitude) in meters

The file **may** also contain any of the following columns:
* `Date` - date of measurement, [m/d/yyyy] (US format)
* `Longitude` - longitude, [DD] (Decimal Degrees format)
* `Max Temperature` - maximum temperature, [deg. C]
* `Min Temperature` - minimum temperature, [deg. C]
* `Precipitation` - precipitation, [mm]
* `Wind` - wind speed, [m/s]
* `Relative Humidity` - relative humidity, number between 0 and 1
* `Solar` - solar radiation received, [MJ/m^2]

The latitude, longitude and elevation will be the same for every measurement. It's unfortunate,
but necessary.

Data following this format can be obtained via the
[Global Weather Data for SWAT](https://globalweather.tamu.edu) website (thank you TAMU).

You can also check out this [example weather file](water_modelling/sample/weather_data/weatherdata.csv).


### Simulation results
#### Archive Structure
```
├── hydrus
│   ├── hydrus_model_name_01
│   |   └── ...
|   └── hydrus_model_name_02
│       └── ...
├── modflow
│   ├── modflow_model_name
│   |   └── ...
│   └── results.json
└── project_name.json
```

The `results.json` file contains the result of the Modflow model, a 4D array with water table levels.
However, all models come with simulation result files, so you can access the result of all Hydrus models
as well if you need to.

The `project_name.json` file contains the project metadata, as described below.

#### Project metadata - *[project_name.json]*
```json
{
    "name": "Project_01",           // project name
    "lat": "12.12",                 // Modflow model top-right corner latitude
    "long": "13.13",                // Modflow model top-right corner longitude
    "start_date": "2001-01-12",     // simulation start date
    "end_date": "2002-02-03",       // simulation end date 
    "spin_up": "2",                 // Hydrus spin-up time, in days
    "rows": 5,                      // Modflow model rows count
    "cols": 5,                      // Modflow model columns count
    "grid_unit": "meters",          // Modflow model length unit
    "row_cells": [100.0, 100.0, 100.0, 100.0, 100.0],   // Modflow model row heights (given in the grid unit)
    "col_cells": [100.0, 100.0, 100.0, 100.0, 100.0],   // Modflow model column widths (given in the grid unit)
    "modflow_model": "project_01_modflow",              // Modflow model name
    "hydrus_models": ["project_01_hydrus", "project_02_hydrus"]   // Hydrus model names
}
```

#### Modflow simulation results - *[results.json]*
```
Contains a 4D array, indexed with [stress_period][layer][row][col]
ex. [
      [
        [ 
          [0.1, 0.5, 0.1], 
          [0.1, 0.5, 0.1] 
        ],
        [ 
          [0.1, 0.5, 0.1],
          [0.1, 0.5, 0.1] 
        ]
      ]
    ] (1 stress period, 2 layers, 2 rows, 3 columns)
```

### Contributors
#### [Izabela Czajowska](https://github.com/iczajowska)
* Running the Modflow simulation using the Kubernetes platform. Creation of the Kubernetes manifest as YAML files. Implementation of abstractions to generate manifests for Job Modflow and Hydrus.
* Development of the graphical interface using bootstrap technology
* Creation of the navigation to enable simple usage of the web application
* Views for uploading Modflow, Hydrus models.
* Securing application endpoints in order to correctly move between simulation windows.
* View for defining areas with the use of data retrieved from an RCH file.
* Creating an interface for defining local paths to Modflow and Hydrus programs.
* Saving application metadata with local paths to Modflow and Hydrus using the DAO design pattern.
* View of the list of simulation projects.
* Validation of uploaded by user metadata of newly created projects.
* Adaptation of the application for usage by many users at the same time. 

#### [Jerzy Jędrzejaszek](https://github.com/FluffyNinjaBrick) 
* Preparation of REST API using Flask library, partial implementation. Simple application views using Flask package. Connecting the frontend and backend - implementation of the functionality of loading models by the user.
* Basic view and logic managing the assignment of Hydrus models to areas designated in the Modflow model.
* Create a state tool to store cache variables and add a level of abstraction necessary for project management.
* Implementation of the project mechanism (Simulation abstraction).
* File persistence of project metadata (name, model coordinates, simulation duration) and information about loaded models (names, resolutions, dimensions of the rows and columns).
* Extracting the simulation results from the Hydrus and Modflow models, providing the simulation results to the user.
* Implementation of loading weather data from files.
* Building a desktop implementation of the project to the executable EXE file.

#### [Mateusz Pawłowicz](https://github.com/Observer46) 
* Checking the correct loading of the Hydrus model.
* Dockerization of the Hydrus-1D program. Adaptation of the developer version of Hydrus in order to run it on Linux distribution.
* Launching the parallel conversion of Hydrus-1D models.
* Transcription of the results of the Hydrus-1D models into the corresponding sub-areas.
* Creation of a component for uploading ZIP models using the drag and drop method.
* Dockerization of the created project and launching new containers from the main container.
* Implementation of monitoring module to check status of Hydrus and Modflow simulations.
* Code refactoring 
* Separation of the three types of deployment: desktop, docker, kubernetes
* Handling of hydrological simulation errors.
* Creation of the Kubernetes cluster architecture
* Adaptation of the application for usage by many users at the same time. 

#### [Maria Polak](https://github.com/BlqMary) 
* Analysis of Flopy and pHydrus libraries for convenient operation of Modflow and Hydrus model, respectively.
* Analysis of the result files of Hydrus and Modflow programs
* Implementation of pods management using Kubernetes platform
* Checking the correctness of the Modflow project provided by the user
* Implementation of Hydrus Modflow integration. Integration of simulation components.
* Modification of the RCH file based on the result from the Hydrus models
* Extracting Modflow model areas based on the input values in the RCH file. Implementing the DFS algorithm to search the Modflow mesh.
* Drawing complex and compacted Modflow model meshes.
* Preparation of compressed result data in an archive for the user.

