# Google Cloud Evaluation of XTR/WARP

> This repository contains the code to reproduce the evaluation of [XTR/WARP](https://github.com/jlscheerer/xtr-warp), [XTR/ScaNN](https://github.com/jlscheerer/xtr-eval), and [ColBERTv2/PLAID](https://github.com/jlscheerer/colbert-eval) on Google Cloud. It includes scripts to initialize and configure the VM instance, clone the necessary repositories, set up the Conda environments, and download the required indexes and datasets.

### Prerequisites

- Google Cloud SDK installed and initialized.
- Access rights to the required Google Cloud Storage buckets.

### Prepare Google Cloud Environment#
First, initialize `gcloud` and set the compute zone:
```sh
gcloud init
gcloud compute zones list

gcloud config set compute/zone europe-west3-a
gcloud auth application-default login
```

### Start and Configure the VM Instance
To start and configure the VM instance, run:
```sh
source scripts/start_vm.sh
```

This script will:
- Create and configure the VM instance.
- Clone the necessary repositories.
- Set up the Conda environments.

### Logging into the VM Instance
After the VM instance is running, log in to the instance:

```sh
gcloud compute ssh xtr-warp-machine --zone=europe-west3-a
```

### Download Indexes and Datasets

To obtain the required indexes and datasets, use the `index_pull.py` script provided in the user's root directory. Ensure you have the necessary access rights to the Google Cloud Storage buckets.

#### Example Usage
- **Download specific indexes and datasets for XTR/WARP:** 
```sh
python index_pull.py xtr-warp -c beir -d nfcorpus -s dev -n 4
```
- **Download datasets for ColBERTv2/PLAID evaluation:**
```sh
python index_pull.py colbert-eval -c beir -d quora -s dev
```
- **Download datasets for XTR/ScaNN evaluation:**
```sh
python index_pull.py xtr-eval -c lotte -d lifestyle -s dev -i scann
```

### Shutdown the VM Instance
To shut down the VM instance and avoid incurring costs when not in use, run:
```bash
source scripts/stop_vm.sh
```