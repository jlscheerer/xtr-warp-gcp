#!/bin/bash

sudo apt update
sudo apt-get install -y wget bzip2
sudo apt-get install -y htop
sudo apt-get install -y gcc g++

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

# Create (expected) folder structure
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

# Configure XTR/WARP repository with environment paths
cp ~/env/xtr_warp.env ~/xtr-warp/.env

# Prepare the Conda Environment for XTR/WARP
cd xtr-warp
${CONDA_PATH} env create -f conda_env_cpu.yml

# We need to install torch-scatter manually
conda activate xtr-warp
TORCH_VERSION=$(python -c "import torch; print(torch.__version__)")
pip install torch-scatter -f "https://data.pyg.org/whl/torch-${TORCH_VERSION}.html"
conda deactivate
cd ..

# Addresses issue related to missing crpyt.h, see: https://github.com/stanford-futuredata/ColBERT/issues/309
export PATH="${CONDA_ROOT}/bin:$PATH"
sudo apt-get install -y libc6-dev
cp /usr/include/crypt.h "${CONDA_ROOT}/envs/warp/include/"
echo "export CPATH=\"${CONDA_ROOT}/envs/warp/include\"" >> ~/.bashrc
export CPATH="${CONDA_ROOT}/envs/warp/include"


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