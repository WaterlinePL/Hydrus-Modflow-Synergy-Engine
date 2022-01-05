# Hydrus-Modflow Synergy Engine - AGH WATER MODELING
This repository is an engineering project that is also a part of WATERLINE project. 
Please refer to the README.md file on the main branch for general information about the project and a tutorial.

## Welcome to the docker branch
This branch serves as a repository for docker deployment. It is preconfigured for launching Docker version of HMSE. 

### Run application container
* use `docker compose` for automated approach - invoke inside the root of the repository:
```
docker compose up
```

* alternatively - manually pull and run image:
  * pull image from DockerHub:
  ```
  docker pull watermodelling/hydrus-modflow-synergy-engine:water-modelling-standalone
  ```
   * run image (for Windows an absolute path is probably required instead):
  ```
  docker run -p 5000:5000 -v ./water_modelling/workspace:/workspace watermodelling/hydrus-modflow-synergy-engine:water-modelling-standalone
  ```
* Note: it requires `water_modelling/workspace` to exist (mounted as a volume) in current PWD 
(recommended invoking commands inside the root of the repository or prepared earlier workspace) - this folder
is mounted to the image and will be used to store all the project created in the application

**Access the application from browser under `localhost:5000`.**

### Docker image development
* Building Docker image - invoke inside the root of the repository:
```
docker build -t watermodelling/hydrus-modflow-synergy-engine:water-modelling-standalone -f Dockerfile.docker .
```
* Building and pushing to DockerHub (for credentials please refer to the owners of the project) - invoke inside
the root of the repository:
```
sh scripts/build_and_push_docker_image.sh 
```


