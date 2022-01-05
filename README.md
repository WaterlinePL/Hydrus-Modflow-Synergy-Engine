# Hydrus-Modflow Synergy Engine - AGH WATER MODELING
This repository is an engineering project that is also a part of WATERLINE project. 
Please refer to the README.md file on the main branch for general information about the project and a tutorial.

## Welcome to the kubernetes branch
This branch serves as a repository for k8s deployment. It is preconfigured for launching Kubernetes version of HMSE. 

### Add NFS Server Provisioner to the cluster
It is required to have the [NFS Server Provisioner](https://github.com/helm/charts/tree/master/stable/nfs-server-provisioner) 
installed in the cluster using [Helm](https://helm.sh/docs/intro/install/). To install it, invoke following commands:
* `helm install nfs1 stable/nfs-server-provisioner`
* if this command causes trouble:
  * download whole [repository from GitHub](https://github.com/helm/charts)
  * find a folder `nfs-server-provisioner` inside the `stable` folder
  * create .tar: 
  ```
  helm package nfs-server-provisioner
  ```
  * install provisioner inside the cluster:
  ```
  helm install nfs1 nfs-server-provisioner-1.1.3.tar
  ```
* in order to customize the chart (ex. in order to give data persistence), it probably needs to be downloaded anyways
* Note: This chart is deprecated.

### Launch Kubernetes Deployment
Whole project is launched using .yaml manifests stored in `k8s` folder. To set up the cluster:
* `kubectl apply -f  k8s/nfs-pvc.yaml` - create PersistentVolumeClaim (acquire storage) 
* `kubectl apply -f  k8s/web-app-role.yaml` - create roles allowing particular Pods to create another Pods, Jobs, etc.
* `kubectl apply -f  k8s/web-app-deployment.yaml` - create Deployment of the application (launch application)

**Application can be accessed under `localhost:30036`**
### Kubernetes deployment development
* Building Docker image of the application - invoke inside the root of the repository:
```
docker build -t watermodelling/hydrus-modflow-synergy-engine:water-modelling-k8s -f Dockerfile.k8s .
```
* Building and pushing to DockerHub (for credentials please refer to the owners of the project) - invoke inside
the root of the repository:
```
sh scripts/build_and_push_k8s_image.sh 
```
Pushing project with `LOCAL_DEBUG_MODE` will most likely cause it not to work properly.

### Important notes:
* Deployment (`web-app-deployment.yaml`) has environmental variable `PVC` with the name of PVC.
It is used in code to create Job manifests with same PVC as main Pod.
* The manifest creating PVC (`nfs-pvc.yaml`) is adapted to small local environment, before launching it is essential
to increase its size
* For more advanced local test, there is a manifest `kind-dev-cluster.yaml` that creates local cluster
with 2 Control Panels and 3 Worker Nodes - it simulates cloud environment
* In `k8s` there are debug manifests which might be used to test changes done to different k8s componenets,
such as PVC