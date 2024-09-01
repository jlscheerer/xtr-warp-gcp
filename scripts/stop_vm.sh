#!/bin/bash

gcloud compute instances stop xtr-warp-machine --quiet
gcloud compute instances delete xtr-warp-machine  --quiet
gcloud deployment-manager deployments delete xtr-warp-deployment --quiet