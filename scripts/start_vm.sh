#!/bin/bash
gcloud deployment-manager deployments create xtr-warp-deployment --config vm-config.yaml

# Ensure the the VM is operational (ensure by sleeping for 10 seconds)
sleep 15

# Copy configuration files from the host to the VM
gcloud compute scp --recurse env xtr-warp-machine:~/

# Configure .ssh required for GitHub repository access
gcloud compute scp --recurse .ssh xtr-warp-machine:~/

# Prepare the VM for evaluation
gcloud compute scp deploy/setup_vm.sh xtr-warp-machine:~/
gcloud compute ssh xtr-warp-machine --zone=europe-west3-a --command='source ~/setup_vm.sh'

gcloud compute ssh xtr-warp-machine --zone=europe-west3-a