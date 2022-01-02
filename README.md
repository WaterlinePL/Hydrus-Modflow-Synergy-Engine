# AGH WATER MODELING
This repository is an engineering project that is also a part of WATERLINE project

## Welcome to the main branch
This branch serves as a repository for common components that are used by every deployment. 
So far we have 3 deployments:
* `desktop`
* `docker`
* `kubernetes`

These versions of application are located on the branches with same name as deployment name.
Each branch has been preconfigured in the file `water_modelling/app_config/deployment_config.py`
to ease testing, launching and mitigate problem with changing deployment config while committing 
to one branch (thus we split master into 3 deployment branches).

### Assumed workflow
* if a new feature relates to every application deployment:
  + create a Pull Request to `master`
  + after merging it, rebase other branches to `master`  - while on another branch,
  use `git fetch origin master:master` and then `git rebase master`
* if a new feature relates to two deployments - create two Pull Requests to each branch
* if a new feature relates to only one deployment - create Pull Request to the deployment's branch

More detailed README are located on the deployments' branches.
### Important
* sample projects are located in folder `sample`
* TESTS SHOULD NOT BE RUN ON PROJECT FROM `sample` FOLDER
* instead, they should be copied to new folder `tests` using scripts
* copy sample projects (please refer to the comments in the scripts):
    + Linux script: scripts/copy_projects.sh (suggested)
    + Windows 10 script: scripts/copy_projects.ps (requires enabled Powershell scripts)

### Repository structure
* **hydrus_docker** - folder with data related to hydrus docker image created by us (hydrus executable compiled
from this [repository](https://github.com/AgriHarmony/HYDRUS-1-D-gfortran)
* **k8s** - .yaml kubernetes manifests related to kubernetes deployment, contains also debug manifests
* **scripts** - bash and PowerShell (not recommended) scripts for building and pushing docker images as well 
as for creating test data inside `water_modelling`
* **water_modelling** - main application
  + `app_config` - module containing deployment settings, modified on each deployment's branch
  + `datapassing` - module containing logic related to passing output from the Hydrus simulation 
  as input to the Modflow simulation 
  + `deployment` - module with deployers for each deployment version (desktop, docker, kubernetes)
  + `hydrus` - module with logic related to launching Hydrus simulations
  + `kubernetes_controller` - module with logic related to monitoring kubernetes jobs (simulations are 
  launched as kubernetes jobs inside the cluster)
  + `modflow` - module with logic related to launching Hydrus simulations
  + `sample` - sample data meant to be copied and used for tests (there is a script that makes a `tests` folder 
  with content from `sample`)
  + `server` - module with web application components (endpoints, states, page templates and their javascript
  functionalities)
  + `simulation` - module related to launching simulation (hydrus -> data passing -> modflow)
  + `workspace` - necessary folder where all created projects is stored (content is ignored by `.gitignore`)