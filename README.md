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

#### Important: For application to run properly, it is required to have *cookies* enabled in the web browser.

### Assumed workflow
* if a new feature relates to every deployment:
  + create a pull request to `master`
  + after merging the PR, rebase the other branches to `master` - while on another branch,
    use `git fetch origin master:master` and then `git rebase master`
* if a new feature relates to only one deployment - create a pull request to that deployment's branch
* if a new feature relates to more than one deployment - create a separate pull request for each branch

More detailed README files are located on the deployments' branches.

### Important
Sample projects are located in the `sample` folder. **TESTS SHOULD NOT BE RUN ON PROJECTS FROM THE `sample` FOLDER**.
Instead, they should be copied to a new `tests` folder using scripts.

* Linux script: scripts/copy_projects.sh (suggested)
* Windows 10 script: scripts/copy_projects.ps (requires enabled Powershell scripts)

For further information refer to the comments in the scripts.

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
##### Archive Structure
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

##### Project metadata - *[project_name.json]*
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

##### Modflow simulation results - *[results.json]*
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