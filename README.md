# gem5-resources-launch
This repo contains a set of scripts to set up and launch/test all full system
resources. The scripts are capable of filtering out runs of specific
characteristics (e.g. only run with kvm, etc.)

## Set up the repo
```sh
./setup.sh
```
**Note**: In the `setup.sh` script, `SPEC2006_ISO_PATH` and `SPEC2017_ISO_PATH`
variables specify the paths to SPEC 2006 ISO file and SPEC 2017 ISO file
respectively. Those ISO files are required build the SPEC disk images for gem5.
Those variables should be before running `setup.sh`.

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
