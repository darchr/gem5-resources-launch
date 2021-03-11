# gem5-resources-launch
This repo contains a set of scripts to set up and launch/test all full system
resources. The scripts are capable of filtering out runs of specific
characteristics (e.g. only run with kvm, etc.).

## Cloning the repo
This repo contains a submodule, so the repo should be cloned recursively.

```sh
git clone https://github.com/darchr/gem5-resources-launch --recursive
```

## Set up the repo
```sh
./setup.sh
```
**Note**: In the `setup.sh` script, `SPEC2006_ISO_PATH` and `SPEC2017_ISO_PATH`
variables specify the paths to SPEC 2006 ISO file and SPEC 2017 ISO file
respectively. Those ISO files are required build the SPEC disk images for gem5.
Those variables should be before running `setup.sh`.

## Set up the run script
In the `launch_test.py` file, there are global variables should be set,
| Variable name | Meaning |
| - | - |
| `OUTPUT_FOLDER` | path to the folder containing the outputs of the gem5 runs |
| `ERR_FOLDER`    | path to the folder containing the error caused by gem5art if a full system run runs into such an error |
| `GEM5_FOLDER`   | path to the gem5 folder |
| `GEM5_RESOURCES_FOLDER`| path to the gem5-resources folder |
| `DISK_IMAGES_FOLDER` | path to the folder containing disk images |
| `LINUX_KERNELS_FOLDER` | path to the folder containing Linux kernels |
| `RUN_NAME_SUFFIX` | unique name for the experiment, this makes querying for the result of those runs easier |

## Setting up the gem5art in a virtual Python environment
```sh
virtualenv -p python3 gem5art-env
source gem5art-env/bin/activate
pip install gem5art-artifact gem5art-run gem5art-tasks
```

## Running the experiments
```sh
python3 ./launch_test.py
```

## Exiting the virtual Python environment
```sh
deactivate
```
