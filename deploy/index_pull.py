import os
import argparse
import json
import getpass

USERNAME = getpass.getuser()

BEIR_DATASETS = ["nfcorpus", "scifact", "scidocs", "fiqa", "webis-touche2020", "quora"]
LOTTE_DATASETS = ["lifestyle", "writing", "recreation", "technology", "science", "pooled"]

BEIR_COLLECTION_PATH = "datasets/gcp/datasets/beir/datasets"
LOTTE_COLLECTION_PATH = "datasets/gcp/datasets/lotte/lotte"

# Used to update existing indexes to the new configuration values.
PRE_BEIR_COLLECTION_PATH="\\/lfs\\/1\\/scheerer\\/datasets\\/beir\\/datasets"
PRE_LOTTE_COLLECTION_PATH="\\/lfs\\/1\\/scheerer\\/datasets\\/lotte\\/lotte"
PRE_XTR_OPT_INDEX_ROOT="/future/u/scheerer/home/data/xtr-eval/indexes"

POST_BEIR_COLLECTION_PATH=f"\\/home\\/{USERNAME}\\/datasets\\/gcp\\/datasets\\/beir\\/datasets"
POST_LOTTE_COLLECTION_PATH=f"\\/home\\/{USERNAME}\\/datasets\\/gcp\\/datasets\\/lotte\\/lotte"
POST_XTR_OPT_INDEX_ROOT=f"/home/{USERNAME}/data/xtr-eval/indexes"

def ensure_collection_exists(collection):
    if not os.path.exists("datasets"):
        os.makedirs("datasets")
    if collection == "beir":
        if os.path.exists(BEIR_COLLECTION_PATH):
            print(f"#> BEIR collection located at './{BEIR_COLLECTION_PATH}'")
            return
        print("#> BEIR collection does not exist. Pulling collection...")
        os.makedirs(f"/home/{USERNAME}/datasets/gcp/datasets", exist_ok=True)
        os.system("gsutil cp gs://xtr_warp_datasets/beir.tar.gz datasets/gcp/datasets")
        os.system("tar -xvzf datasets/gcp/datasets/beir.tar.gz -C datasets/gcp/datasets")
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
    os.system(f"rm data/{index_name}.tar.gz")

    PRE_INDEX_ROOT="/future/u/scheerer/home/data/xtr-warp/indexes"
    POST_INDEX_ROOT=f"/home/{USERNAME}/data/xtr-warp/indexes"

    PRE_EXPERIMENT_ROOT="/future/u/scheerer/home/development/xtr-warp/experiments"
    POST_EXPERIMENT_ROOT=f"/home/{USERNAME}/data/xtr-warp/experiments"

    PRE_BEIR_COLLECTION_PATH="/lfs/1/scheerer/datasets/beir/datasets"
    PRE_LOTTE_COLLECTION_PATH="/lfs/1/scheerer/datasets/lotte/lotte"

    for meta_file in ["metadata.json", "plan.json"]:
        config_file = f"data/xtr-warp/indexes/{index_name}/{meta_file}"
        with open(config_file, "r") as file:
            meta = json.loads(file.read())
        meta["config"]["index_path"] = meta["config"]["index_path"].replace(
            PRE_INDEX_ROOT, POST_INDEX_ROOT
        )
        meta["config"]["root"] = meta["config"]["root"].replace(
            PRE_EXPERIMENT_ROOT, POST_EXPERIMENT_ROOT
        )
        meta["config"]["collection"] = meta["config"]["collection"].replace(
            PRE_BEIR_COLLECTION_PATH, f"/home/{USERNAME}/{BEIR_COLLECTION_PATH}"
        ).replace(PRE_LOTTE_COLLECTION_PATH, f"/home/{USERNAME}/{LOTTE_COLLECTION_PATH}")
        with open(config_file, "w") as file:
            file.write(json.dumps(meta, indent=3))


def pull_colbert_index(collection, dataset, split):
    if not os.path.exists("models"):
        os.makedirs("models")
    if not os.path.exists("models/colbertv2.0"):
        print("#> colbertv2.0 checkpoint does not exist. Pulling...")
        os.system(f"gsutil cp gs://xtr-warp-models/colbertv2.0.tar.gz models/")
        os.system(f"tar -xvzf 'models/colbertv2.0.tar.gz' -C models/")
        os.system(f"rm models/colbertv2.0.tar.gz")

    index_name = f"{dataset}.split={split}.nbits=2"
    if not os.path.exists("colbert-eval/experiments/eval/indexes"):
        os.makedirs("colbert-eval/experiments/eval/indexes")
    if os.path.exists(f"colbert-eval/experiments/eval/indexes/{index_name}"):
        print(f"#> colbert-eval index located at 'colbert-eval/experiments/eval/indexes/{index_name}'")
        return

    print("#> Index does not exist. Pulling...")
    os.system(f"gsutil cp gs://colbert_plaid_indices/{index_name}.tar.gz colbert-eval/experiments/eval/indexes")
    os.system(f"tar -xvzf 'colbert-eval/experiments/eval/indexes/{index_name}.tar.gz' -C colbert-eval/experiments/eval/indexes")
    os.system(f"rm colbert-eval/experiments/eval/indexes/{index_name}.tar.gz")

    PRE_BEIR_COLLECTION_PATH="/lfs/1/scheerer/datasets/beir/datasets"
    PRE_LOTTE_COLLECTION_PATH="/lfs/1/scheerer/datasets/lotte/lotte"

    POST_INDEX_ROOT=f"\\/home\\/{USERNAME}\\/colbert-eval\\/experiments"
    POST_CHECKPOINT=f"/home/{USERNAME}/models/colbertv2.0"

    for meta_file in ["metadata.json", "plan.json"]:
        config_file = f"colbert-eval/experiments/eval/indexes/{index_name}/{meta_file}"
        with open(config_file, "r") as file:
            meta = json.loads(file.read())
        meta["config"]["root"] = POST_INDEX_ROOT
        meta["config"]["checkpoint"] = POST_CHECKPOINT
        meta["config"]["collection"] = meta["config"]["collection"].replace(
            PRE_BEIR_COLLECTION_PATH, f"/home/{USERNAME}/{BEIR_COLLECTION_PATH}"
        ).replace(PRE_LOTTE_COLLECTION_PATH, f"/home/{USERNAME}/{LOTTE_COLLECTION_PATH}")
        with open(config_file, "w") as file:
            file.write(json.dumps(meta, indent=3))

def pull_xtr_eval_index(collection, dataset, split, index):
    collection_name = "BEIR" if collection == "beir" else "LoTTE"
    if dataset == "fiqa":
        dataset = "fiqa_2018"
    elif dataset == "webis-touche2020":
        dataset = "touche_2020"
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
    os.system(f"rm data/{index_name}.tar.gz")

    if index == "scann":
        config_file = f"data/xtr-eval/indexes/{index_name}/scann/scann_assets.pbtxt"
        os.system(f"sed -i \"s#{PRE_XTR_OPT_INDEX_ROOT}#{POST_XTR_OPT_INDEX_ROOT}#g\" {config_file}")

def pull_index(parser, engine, collection, dataset, split, nbits, index):
    if collection == "beir":
        if dataset not in BEIR_DATASETS:
            parser.print_help()
            return
    elif collection == "lotte":
        if dataset not in LOTTE_DATASETS:
            parser.print_help()
            return
    else: raise AssertionError

    if engine == "xtr-warp":
        pull_xtr_warp_index(collection, dataset, split, nbits)
    elif engine == "colbert-eval":
        pull_colbert_index(collection, dataset, split)
    elif engine == "xtr-eval":
        pull_xtr_eval_index(collection, dataset, split, index)
    else: raise AssertionError

def main():
    parser = argparse.ArgumentParser(prog="index_pull.py")
    parser.add_argument("engine", choices=["xtr-warp", "colbert-eval", "xtr-eval"])
    parser.add_argument("-c", "--collection", choices=["beir", "lotte"], required=True)
    parser.add_argument("-d", "--dataset", choices=LOTTE_DATASETS + BEIR_DATASETS)
    parser.add_argument("-s", "--split", choices=["dev", "test"], required=True)

    # xtr-warp specific options
    parser.add_argument("-n", "--nbits", type=int, choices=[2, 4])

    # xtr-eval specific options
    parser.add_argument("-i", "--index", choices=["bruteforce", "faiss", "scann"])

    args = parser.parse_args()

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

    if args.dataset is not None:
        return pull_index(parser, args.engine, args.collection, args.dataset, args.split, args.nbits, args.index)

    print(f"#> Attempting to pull all indexes matching engine='{args.engine}', collection='{args.collection}', split='{args.split}', nbits='{args.nbits}', index='{args.index}'")
    confirmation = input("confirm [Y]/n: ").strip().lower()
    if len(confirmation) != 0 and confirmation != "y":
        return

    DATASETS = BEIR_DATASETS if args.collection == "beir" else LOTTE_DATASETS
    for dataset in DATASETS:
        print(f"#> pulling {args.engine} index {args.collection}.{dataset}...")
        pull_index(parser, args.engine, args.collection, dataset, args.split, args.nbits, args.index)

if __name__ == "__main__":
    main()