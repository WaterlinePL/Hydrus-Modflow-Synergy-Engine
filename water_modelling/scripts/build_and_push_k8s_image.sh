#!/bin/bash
# Scripts is meant to be used while in root of repo

docker build -t watermodelling/hydrus-modflow-synergy-engine:water-modelling-k8s -f Dockerfile.k8s .
docker push watermodelling/hydrus-modflow-synergy-engine:water-modelling-k8s