import json
from argparse import Namespace
import os
import subprocess


def setup_folders(args):
    output_dir = args.output_dir
    version = f"v{args.version}"

    os.makedirs(os.path.join(output_dir, version), exist_ok=True)

    manifest_path = os.path.join(output_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        manifest = {
            "all": [],
        }
    else:
        with open(manifest_path) as f:
            manifest = json.load(f)

    if version not in manifest["all"]:
        manifest["all"].append(version)
    manifest["last"] = version

    with open(manifest_path, "w") as f:
        json.dump(manifest, f)


def modify_js_config(args):
    js_config_path = args.js_config_path

    dataUrl = args.api_prefix + "/"
    apiUrl = args.api_prefix + "/predict"

    with open(js_config_path, "w") as f:
        f.write("export default {\n")
        f.write(f"    dataUrl: '{dataUrl}', \n")
        f.write(f"    apiUrl: '{apiUrl}',\n")
        f.write(f"    target_name: '{args.target_name}', \n")
        f.write(f"    strong_column_names: {args.strong_column_names}, \n")
        f.write(f"    description: '{args.description}', \n")
        f.write(f"    name: '{args.name}', \n")
        f.write("};")


def setup_layout_generation(args):
    layout = args.layout_dir
    output = subprocess.run(
        f"cd {layout}; rm -rf build; mkdir build; cd build; cmake ..; make -j3",
        shell=True,
        capture_output=True
    )
    print(output.stdout.decode())
    print(output.stderr.decode())


def layout_generation(args):
    output_dir = args.output_dir
    layout_dir = args.layout_dir
    version = version = f"v{args.version}"

    output = subprocess.run(
        f"cd {layout_dir}/build; ./layout {output_dir}/{version}/links.bin {output_dir}/{version}",
        shell=True,
        capture_output=True
    )
    print(output.stdout.decode())
    print(output.stderr.decode())


def build_npm(args):
    galaxy_dir = args.galaxy_dir
    output = subprocess.run(
        f"cd {galaxy_dir}; npm install; npm ci; npm run build",
        shell=True,
        capture_output=True
    )
    print(output.stdout.decode())
    print(output.stderr.decode())


def generate_graphs(config_path):
    from generate_graph import generate_graph_from_config
    generate_graph_from_config(config_path=config_path)


if __name__ == "__main__":
    config_path = os.environ["CONFIG_PATH"]
    with open(config_path, "r") as f:
        config_data = json.load(f)
        args = Namespace(**config_data)

    setup_folders(args)
    print("finished setting up folders")
    generate_graphs(config_path=config_path)
    print("finished setting up graphs")
    setup_layout_generation(args)
    print("finished setting up layout")
    layout_generation(args)
    print("finished computing layouts")
    modify_js_config(args)
    print("finished setting up js config")
    build_npm(args)
    print("finished setting up npm")
