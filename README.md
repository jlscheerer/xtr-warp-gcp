### Prepare GCloud Environment
```bash
gcloud init
gcloud compute zones list

gcloud config set compute/zone europe-west3-a
gcloud auth application-default login
```

### Start and Configure XTR/WARP VM for Evaluation
```bash
source scripts/start_vm.sh
```

### Shutdown XTR/WARP VM
```bash
source scripts/stop_vm.sh
```