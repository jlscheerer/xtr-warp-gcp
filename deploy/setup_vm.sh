DOWNLOAD_LOTTE=false

# Indexes to pull/download for evaluation
INDEXES=("beir-scifact.split=test.nbits=4")

XTR_INDEXES=("BEIR.SCIFACT.split=test.XTRIndexType.SCANN")

CONFIG_FILES=("metadata.json" "plan.json")

# Used to update existing indexes to the new configuration values.
PRE_INDEX_ROOT="\\\/future\\\/u\\\/scheerer\\\/home\\\/data\\\/xtr-warp\\\/indexes"
PRE_EXPERIMENT_ROOT="\\\/future\\\/u\\\/scheerer\\\/home\\\/development\\\/xtr-warp\\\/experiments"
PRE_BEIR_COLLECTION_PATH="\\\/lfs\\\/1\\\/scheerer\\\/datasets\\\/beir\\\/datasets"
PRE_LOTTE_COLLECTION_PATH="\\\/lfs\\\/1\\\/scheerer\\\/datasets\\\/lotte\\\/lotte"

PRE_XTR_OPT_INDEX_ROOT="/future/u/scheerer/home/data/xtr-eval/indexes"

INDEX_ROOT="\/home\/jlscheerer\/data\/xtr-warp\/indexes"
EXPERIMENT_ROOT="\/home\/jlscheerer\/data\/xtr-warp\/experiments"
BEIR_COLLECTION_PATH="\/home\/jlscheerer\/datasets\/gcp\/datasets\/beir\/datasets"
LOTTE_COLLECTION_PATH="\/home\/jlscheerer\/datasets\/gcp\/lotte\/lotte"

XTR_OPT_INDEX_ROOT="/home/jlscheerer/data/xtr-eval/indexes"

sudo apt update
sudo apt-get install -y wget bzip2
sudo apt-get install -y htop

# Install the Conda Package Manager
MINICONDA_VERSION="latest"
CONDA_ROOT="$HOME/miniconda"
CONDA_PATH="${CONDA_ROOT}/bin/conda"
wget "https://repo.anaconda.com/miniconda/Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh" -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
$HOME/miniconda/bin/conda init bash

export PATH="${CONDA_ROOT}/etc/profile.d/conda.sh:$PATH"
export PATH="${CONDA_ROOT}/bin:$PATH"

source "${CONDA_ROOT}/etc/profile.d/conda.sh"
source ~/.bashrc
source ~/.zshrc

conda init
conda activate base

# Create (expected) folder structure for XTR/WARP
mkdir -p ~/datasets
mkdir -p ~/data/xtr-warp/experiments
mkdir -p ~/data/xtr-warp/indexes
mkdir -p ~/models

# Configure SSH to be able to clone the GitHub Repositories
sudo chmod 600 /home/jlscheerer/.ssh/id_rsa
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa
ssh-keyscan github.com >> ~/.ssh/known_hosts

# Clone the GitHub repositories required for evaluation
git clone git@github.com:jlscheerer/xtr-warp.git
git clone git@github.com:jlscheerer/xtr-eval.git

# Pull the datasets to evaluate XTR/WARP on
gsutil cp gs://xtr_warp_datasets/beir.tar.gz datasets/
tar -xvzf datasets/beir.tar.gz -C datasets/

if $DOWNLOAD_LOTTE; then
    gsutil cp gs://xtr_warp_datasets/lotte.tar.gz datasets/
    tar -xvzf datasets/lotte.tar.gz -C datasets/
fi

# Pull the already created indexes for XTR/WARP
for index in "${INDEXES[@]}"; do
    gsutil cp gs://xtr_warp_indices/${index}.tar.gz data/
    tar -xvzf data/${index}.tar.gz -C data/xtr-warp/indexes
done

# Configure XTR/WARP repository with environment paths
cp ~/env/xtr_warp.env ~/xtr-warp/.env

# Prepare the Conda Environment for XTR/WARP
cd xtr-warp
${CONDA_PATH} env create -f conda_env_cpu.yml
cd ..

# Apply changes to the configuration files
for index in "${INDEXES[@]}"; do
    for file in "${CONFIG_FILES[@]}"; do
        config_file="/home/jlscheerer/data/xtr-warp/indexes/${index}/${file}"
        sed -i "s#${PRE_INDEX_ROOT}#${INDEX_ROOT}#g" $config_file
        sed -i "s#${PRE_EXPERIMENT_ROOT}#${EXPERIMENT_ROOT}#g" $config_file
        sed -i "s#${PRE_BEIR_COLLECTION_PATH}#${BEIR_COLLECTION_PATH}#g" $config_file
        sed -i "s#${PRE_LOTTE_COLLECTION_PATH}#${LOTTE_COLLECTION_PATH}#g" $config_file
    done
done

# Addresses issue related to missing crpyt.h, see: https://github.com/stanford-futuredata/ColBERT/issues/309
export PATH="${CONDA_ROOT}/bin:$PATH"
sudo apt-get install -y libc6-dev
cp /usr/include/crypt.h "${CONDA_ROOT}/envs/colbert/include/"
echo "export CPATH=\"${CONDA_ROOT}/envs/colbert/include\"" >> ~/.bashrc
export CPATH="${CONDA_ROOT}/envs/colbert/include"

# Create (expected) folder structure for XTR/WARP
mkdir -p ~/data/xtr-eval/indexes

# Pull the already created indexes for XTROpt
for index in "${XTR_INDEXES[@]}"; do
    gsutil cp gs://xtr_baseline_indices/${index}.tar.gz data/
    tar -xvzf data/${index}.tar.gz -C data/xtr-eval/indexes
done

# Configure the Conda Environment for XTROpt
cd xtr-eval
git checkout opt
${CONDA_PATH} env create -f environment.yml

# We need to install torch-scatter manually
conda activate xtr-eval
TORCH_VERSION=$(python -c "import torch; print(torch.__version__)")
pip install torch-scatter -f "https://data.pyg.org/whl/torch-${TORCH_VERSION}.html"
conda deactivate
cd ..

# Configure XTROpt repository with environment paths
cp ~/env/xtr_opt.config.yml ~/xtr-eval/config.yml

# Apply changes to the configuration files
# [Sic] This will just fail for non ScaNN indexes...
for index in "${XTR_INDEXES[@]}"; do
    config_file="/home/jlscheerer/data/xtr-eval/indexes/${index}/scann/scann_assets.pbtxt"
    sed -i "s#${PRE_XTR_OPT_INDEX_ROOT}#${XTR_OPT_INDEX_ROOT}#g" $config_file
done