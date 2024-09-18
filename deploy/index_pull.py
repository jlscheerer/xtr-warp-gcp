import os
import argparse
import getpass

USERNAME = getpass.getuser()

BEIR_DATASETS = ["nfcorpus", "scifact", "scidocs", "fiqa", "webis-touche2020", "quora"]
LOTTE_DATASETS = ["lifestyle", "writing", "recreation", "technology", "science", "pooled"]

BEIR_COLLECTION_PATH = "datasets/gcp/datasets/beir/datasets"
LOTTE_COLLECTION_PATH = "datasets/gcp/datasets/lotte/lotte/"

# Used to update existing indexes to the new configuration values.
PRE_INDEX_ROOT="\\/future\\/u\\/scheerer\\/home\\/data\\/xtr-warp\\/indexes"
PRE_EXPERIMENT_ROOT="\\/future\\/u\\/scheerer\\/home\\/development\\/xtr-warp\\/experiments"
PRE_BEIR_COLLECTION_PATH="\\/lfs\\/1\\/scheerer\\/datasets\\/beir\\/datasets"
PRE_LOTTE_COLLECTION_PATH="\\/lfs\\/1\\/scheerer\\/datasets\\/lotte\\/lotte"
PRE_XTR_OPT_INDEX_ROOT="/future/u/scheerer/home/data/xtr-eval/indexes"

POST_INDEX_ROOT=f"\\/home\\/{USERNAME}\\/data\\/xtr-warp\\/indexes"
POST_EXPERIMENT_ROOT=f"\\/home\\/{USERNAME}\\/data\\/xtr-warp\\/experiments"
POST_BEIR_COLLECTION_PATH=f"\\/home\\/{USERNAME}\\/datasets\\/gcp\\/datasets\\/beir\\/datasets"
POST_LOTTE_COLLECTION_PATH=f"\\/home\\/{USERNAME}\\/datasets\\/gcp\\/lotte\\/lotte"
POST_XTR_OPT_INDEX_ROOT=f"/home/{USERNAME}/data/xtr-eval/indexes"

def ensure_collection_exists(collection):
    if not os.path.exists("datasets"):
        os.makedirs("datasets")
    if collection == "beir":
        if os.path.exists(BEIR_COLLECTION_PATH):
            print(f"#> BEIR collection located at './{BEIR_COLLECTION_PATH}'")
            return
        print("#> BEIR collection does not exist. Pulling collection...")
        os.system("gsutil cp gs://xtr_warp_datasets/beir.tar.gz datasets/")
        os.system("tar -xvzf datasets/beir.tar.gz -C datasets/")
    elif collection == "lotte":
        if os.path.exists(LOTTE_COLLECTION_PATH):
            print(f"#> LoTTE collection located at './{LOTTE_COLLECTION_PATH}'")
            return
        print("#> LoTTE collection does not exist. Pulling collection...")
        os.system("gsutil cp gs://xtr_warp_datasets/lotte.tar.gz datasets/")
        os.system("tar -xvzf datasets/lotte.tar.gz -C datasets/")
    else: raise AssertionError

def pull_xtr_warp_index(collection, dataset, split, nbits):
    index_name = f"{collection}-{dataset}.split={split}.nbits={nbits}"
    if not os.path.exists("data/xtr-warp/indexes"):
        os.makedirs("data/xtr-warp/indexes")

    if os.path.exists(f"data/xtr-warp/indexes/{index_name}"):
        print(f"#> xtr-warp index locatated at 'data/xtr-warp/indexes/{index_name}'")
        return

    print("#> Index does not exist. Pulling...")
    os.system(f"gsutil cp gs://xtr_warp_indices/{index_name}.tar.gz data/")
    os.system(f"tar -xvzf 'data/{index_name}.tar.gz' -C data/xtr-warp/indexes")

    for file in ["metadata.json", "plan.json"]:
        config_file = f"data/xtr-warp/indexes/{index_name}/{file}"
        os.system(f"sed -i \"s#{PRE_INDEX_ROOT}#{POST_INDEX_ROOT}#g\" {config_file}")
        os.system(f"sed -i \"s#{PRE_EXPERIMENT_ROOT}#{POST_EXPERIMENT_ROOT}#g\" {config_file}")
        os.system(f"sed -i \"s#{PRE_BEIR_COLLECTION_PATH}#{POST_BEIR_COLLECTION_PATH}#g\" {config_file}")
        os.system(f"sed -i \"s#{PRE_LOTTE_COLLECTION_PATH}#{POST_LOTTE_COLLECTION_PATH}#g\" {config_file}")

def pull_colbert_index(collection, dataset, split):
    index_name = f"{dataset}.split={splits}.nbits=2"

def pull_xtr_eval_index(collection, dataset, split, index):
    collection_name = "BEIR" if collection == "beir" else "LoTTE"
    dataset_name = f"{dataset.upper()}.search" if collection == "lotte" else dataset.upper()
    index_type = "BRUTE_FORCE" if index == "bruteforce" else index.upper()
    index_name = f"{collection_name}.{dataset_name}.split={split}.XTRIndexType.{index_type}"

    if not os.path.exists("data/xtr-eval/indexes"):
        os.makedirs("data/xtr-eval/indexes")

    if os.path.exists(f"data/xtr-eval/indexes/{index_name}"):
        print(f"#> xtr-eval index located at 'data/xtr-eval/indexes/{index_name}'")
        return

    print("#> Index does not exist. Pulling...")
    os.system(f"gsutil cp gs://xtr_baseline_indices/{index_name}.tar.gz data/")
    os.system(f"tar -xvzf 'data/{index_name}.tar.gz' -C data/xtr-eval/indexes")

    # Apply changes to the configurations files
    # [Sic] this will just fail for non ScaNN indexes...
    # Apply changes to the configuration files
    config_file = f"data/xtr-eval/indexes/{index_name}/scann/scann_assets.pbtxt"
    os.system(f"sed -i \"s#{PRE_XTR_OPT_INDEX_ROOT}#{POST_XTR_OPT_INDEX_ROOT}#g\" {config_file}")

def main():
    parser = argparse.ArgumentParser(prog="index_pull.py")
    parser.add_argument("engine", choices=["xtr-warp", "colbert-eval", "xtr-eval"])
    parser.add_argument("-c", "--collection", choices=["beir", "lotte"], required=True)
    parser.add_argument("-d", "--dataset", choices=LOTTE_DATASETS + BEIR_DATASETS, required=True)
    parser.add_argument("-s", "--split", choices=["dev", "test"], required=True)

    # xtr-warp specific options
    parser.add_argument("-n", "--nbits", type=int, choices=[2, 4])

    # xtr-eval specific options
    parser.add_argument("-i", "--index", choices=["bruteforce", "faiss", "scann"])

    args = parser.parse_args()

    if args.collection == "beir":
        if args.dataset not in BEIR_DATASETS:
            parser.print_help()
            return
    elif args.collection == "lotte":
        if args.dataset not in LOTTE_DATASETS:
            parser.print_help()
            return
    else: raise AssertionError

    if args.engine == "xtr-warp":
        if args.nbits is None or args.index is not None:
            parser.print_help()
            return
    elif args.engine == "colbert-eval":
        if args.nbits is not None or args.index is not None:
            parser.print_help()
            return
    elif args.engine == "xtr-eval":
        if args.nbits is not None or args.index is None:
            parser.print_help()
            return
    else: raise AssertionError

    ensure_collection_exists(args.collection)

    if args.engine == "xtr-warp":
        pull_xtr_warp_index(args.collection, args.dataset, args.split, args.nbits)
    elif args.engine == "colbert-eval":
        pull_colbert_index(args.collection, args.dataset, args.split)
    elif args.engine == "xtr-eval":
        pull_xtr_eval_index(args.collection, args.dataset, args.split, args.index)
    else: raise AssertionError



if __name__ == "__main__":
    main()