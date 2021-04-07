from itertools import product as cross_product
import multiprocessing as mp
import os
import pathlib
import sys
import traceback

from common_artifacts import *
from tests_artifacts import *
from filter_logic import *
import input_space

from gem5art.artifact.artifact import Artifact
from gem5art.run import gem5Run

import argparse

ABS_PATH = pathlib.Path(__file__).parent.absolute()

OUTPUT_FOLDER = "/projects/gem5/gem5-resources-21.0/"
ERR_FOLDER = os.path.join(ABS_PATH, "error_logs/")
GEM5_FOLDER = os.path.join(ABS_PATH, "gem5/")
GEM5_RESOURCES_FOLDER = os.path.join(ABS_PATH, "gem5-resources/")
DISK_IMAGES_FOLDER = os.path.join(ABS_PATH, "disk-images/")
LINUX_KERNELS_FOLDER = os.path.join(ABS_PATH, "linux-kernels/")
RUN_NAME_SUFFIX = "launched:04/07/2021;gem5art-status;v21.0;lavandula-multifida;patch-0"

BOOTING_TIMEOUT = 10 * 60 # 10 minutes; booting Linux kernel w/ KVM is fast
GEM5RUN_CHECK_FAILURE_INTERVAL = 5 # 5 seconds

os.makedirs(ERR_FOLDER, exist_ok=True)

def lists_to_dict(keys, vals):
    return dict(zip(keys, vals))

def to_abs_path(path): # return the absoblute path of a relative path, assuming the relative path to be relative to the folder containing this script
    return os.path.join(ABS_PATH, path)

def get_boot_exit_jobs_iterator():
    name = 'boot-exit'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.mem_sys, params.num_cpus, params.boot_types):
        kwargs = lists_to_dict(['kernel', 'cpu', 'mem_sys', 'num_cpu', 'boot_type'], p)
        yield kwargs

def get_npb_jobs_iterator():
    name = 'npb'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.mem_sys, params.num_cpus, params.workloads):
        kwargs = lists_to_dict(['kernel', 'cpu', 'mem_sys', 'num_cpu', 'workload'], p)
        yield kwargs

def get_gapbs_jobs_iterator():
    name = 'gapbs'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.num_cpus, params.mem_sys, params.workloads, params.synthetic, params.n_nodes):
        kwargs = lists_to_dict(['kernel', 'cpu', 'num_cpu', 'mem_sys', 'workload', 'synthetic', 'n_nodes'], p)
        yield kwargs

def get_parsec_jobs_iterator():
    name = 'parsec'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.mem_sys, params.num_cpus, params.workloads, params.sizes):
        kwargs = lists_to_dict(['kernel', 'cpu', 'mem_sys', 'num_cpu', 'workload', 'size'], p)
        yield kwargs

def get_parsec_20_04_jobs_iterator():
    name = 'parsec-20.04'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.mem_sys, params.num_cpus, params.workloads, params.sizes):
        kwargs = lists_to_dict(['kernel', 'cpu', 'mem_sys', 'num_cpu', 'workload', 'size'], p)
        yield kwargs

def get_spec_2006_jobs_iterator():
    name = 'spec-2006'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.mem_sys, params.workloads, params.sizes):
        kwargs = lists_to_dict(['kernel', 'cpu', 'mem_sys', 'workload', 'size'], p)
        yield kwargs

def get_spec_2017_jobs_iterator():
    name = 'spec-2017'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.workloads, params.sizes):
        kwargs = lists_to_dict(['kernel', 'cpu', 'workload', 'size'], p)
        yield kwargs

def get_jobs_iterator(custom_filter = lambda name, params: True):
    iterators = [get_boot_exit_jobs_iterator(),
                 get_npb_jobs_iterator(),
                 get_gapbs_jobs_iterator(),
                 get_parsec_jobs_iterator(),
                 #get_parsec_20_04_jobs_iterator(),
                 get_spec_2006_jobs_iterator(),
                 get_spec_2017_jobs_iterator()]
    #names = ['boot-exit', 'npb', 'gapbs', 'parsec', 'parsec-20.04', 'spec-2006', 'spec-2017']
    names = ['boot-exit', 'npb', 'gapbs', 'parsec', 'spec-2006', 'spec-2017']
    for name, iterator in zip(names, iterators):
        while True:
            try:
                kwargs = next(iterator)
                if workload_filter(name, kwargs, custom_filter):
                    yield (name, kwargs)
            except StopIteration:
                break

def get_gem5_binary_path(mem_sys):
    if mem_sys == "classic":
        return os.path.join(GEM5_FOLDER, "build/X86/gem5.opt")
    else:
        return os.path.join(GEM5_FOLDER, "build/X86_{}/gem5.opt".format(mem_sys))

# This function is to check whether the simulation has failed to boot Linux kernel within a specified amount of time.
# This function will search for `checking_phrase` in the `simout` file of the simulation corresponding to gem5run_object.
# Because this function is expensive time-wise / resources-wise, the check will only perform checking for failure when time in this range [timeout, timeout + 5 * gem5art_check_failure_interval)
#
# gem5run_object: the gem5run to check.
# timeout: , in seconds.
# gem5art_check_failure_interval: how frequently gem5art calls this function.
# checking_phrase: if this phrase exists in simout, the simulation has done booted Linux kernel.
#
# return: True if `checking_phrase` does not appear in `simout` file if the runtime is within [timeout, timeout + 5 * gem5art_check_failure_interval)
#         False otherwise
def linux_booting_check_failure(gem5run_object, timeout = BOOTING_TIMEOUT, gem5art_check_failure_interval = GEM5RUN_CHECK_FAILURE_INTERVAL, checking_phrase = "Done booting Linux"):
    run_time = gem5run_object.current_time - gem5run_object.start_time
    if not (run_time >= timeout and run_time < timeout + 5 * gem5art_check_failure_interval):
        return False

    # now the simulation run time is within the interval for checking
    has_done_booting_linux = False
    with open(gem5run_object.outdir / "simout") as f:
        for line in f.readlines():
            line = line.strip()
            if checking_phrase in line:
                has_done_booting_linux = True
                break

    if has_done_booting_linux:
        return False
    return True


# https://github.com/darchr/gem5art-experiments/blob/master/launch-scripts/launch_boot_tests_gem5_20.py#L128
def create_boot_exit_fs_run(params):
    kernel = params['kernel']
    cpu = params['cpu']
    mem_sys = params['mem_sys']
    num_cpu = params['num_cpu']
    boot_type = params['boot_type']
    if cpu == "kvm":
        timeout = 12*60*60 # 12 hours
    else:
        timeout = 2*24*60*60 # 2 days
    assert(mem_sys in gem5_binaries)

    gem5run = gem5Run.createFSRun(
        'boot-exit;'+RUN_NAME_SUFFIX, # name
        get_gem5_binary_path(mem_sys), # gem5_binary
        os.path.join(GEM5_RESOURCES_FOLDER, 'src/boot-exit/configs/run_exit.py'), # run_script
        os.path.join(OUTPUT_FOLDER, 'boot-exit/{}/{}/{}/{}/{}/'. format(kernel, cpu, num_cpu, mem_sys, boot_type)), # outdir
        gem5_binaries[mem_sys], # gem5_artifact
        gem5_repo, # gem5_git_artifact
        experiments_repo, # run_script_git_artifact
        os.path.join(LINUX_KERNELS_FOLDER, 'vmlinux'+'-'+kernel), # linux_binary
        os.path.join(DISK_IMAGES_FOLDER, 'boot-exit.img'), # disk_image
        linux_binaries[kernel], # linux_binary_artifact
        boot_exit_artifacts.disk_image, # disk_image_artifact
        cpu, mem_sys, num_cpu, boot_type, # params
        timeout = timeout,
        check_failure = lambda run_obj: linux_booting_check_failure(run_obj)
    )
    output_folder = os.path.join(OUTPUT_FOLDER, 'boot-exit/{}/{}/{}/{}/{}/'. format(kernel, cpu, num_cpu, mem_sys, boot_type))
    #assert(os.path.exists(os.path.join(output_folder, "../")))
    #assert(not os.path.exists(os.path.join(output_folder, "simout")))
    return gem5run

def create_npb_fs_run(params):
    kernel = params['kernel']
    cpu = params['cpu']
    mem_sys = params['mem_sys']
    num_cpu = params['num_cpu']
    workload = params['workload']

    if cpu == "kvm":
        timeout = 24*60*60 # 1 day
    else:
        timeout = 10*24*60*60 # 10 days

    gem5run = gem5Run.createFSRun(
        'npb;'+RUN_NAME_SUFFIX, # name
        get_gem5_binary_path(mem_sys), # gem5_binary
        os.path.join(GEM5_RESOURCES_FOLDER, 'src/npb/configs/run_npb.py'), # run_script
        os.path.join(OUTPUT_FOLDER, 'npb/{}/{}/{}/{}/{}/'. format(kernel, cpu, num_cpu, mem_sys, workload)), # outdir
        gem5_binaries[mem_sys], # gem5_artifact
        gem5_repo, # gem5_git_artifact
        experiments_repo, # run_script_git_artifact
        os.path.join(LINUX_KERNELS_FOLDER, 'vmlinux'+'-'+kernel), # linux_binary
        os.path.join(DISK_IMAGES_FOLDER, 'npb.img'), # disk_image
        linux_binaries[kernel], # linux_binary_artifact
        npb_artifacts.disk_image, # disk_image_artifact
        cpu, mem_sys, workload, num_cpu, # params
        timeout = timeout,
        check_failure = lambda run_obj: linux_booting_check_failure(run_obj)
    )
    return gem5run

def create_gapbs_fs_run(params):
    kernel = params['kernel']
    cpu = params['cpu']
    num_cpu = params['num_cpu']
    mem_sys = params['mem_sys']
    workload = params['workload']
    synthetic = params['synthetic']
    n_nodes = params['n_nodes']
    if cpu == "kvm":
        timeout = 24*60*60 # 1 day
    else:
        timeout = 10*24*60*60 # 10 days

    gem5run = gem5Run.createFSRun(
        'gapbs;'+RUN_NAME_SUFFIX, # name
        get_gem5_binary_path(mem_sys), # gem5_binary
        os.path.join(GEM5_RESOURCES_FOLDER, 'src/gapbs/configs/run_gapbs.py'), # run_script
        os.path.join(OUTPUT_FOLDER, 'gapbs/{}/{}/{}/{}/{}/{}/{}/'. format(kernel, cpu, num_cpu, mem_sys, workload, synthetic, n_nodes)), # outdir
        gem5_binaries[mem_sys], # gem5_artifact
        gem5_repo, # gem5_git_artifact
        experiments_repo, # run_script_git_artifact
        os.path.join(LINUX_KERNELS_FOLDER, 'vmlinux'+'-'+kernel), # linux_binary
        os.path.join(DISK_IMAGES_FOLDER, 'gapbs.img'), # disk_image
        linux_binaries[kernel], # linux_binary_artifact
        gapbs_artifacts.disk_image, # disk_image_artifact
        cpu, num_cpu, mem_sys, workload, synthetic, n_nodes, # params
        timeout = timeout,
        check_failure = lambda run_obj: linux_booting_check_failure(run_obj)
    )
    return gem5run

def create_parsec_fs_run(params):
    kernel = params['kernel']
    cpu = params['cpu']
    num_cpu = params['num_cpu']
    mem_sys = params['mem_sys']
    workload = params['workload']
    size = params['size']

    if cpu == "kvm":
        timeout = 24*60*60 # 1 day
    else:
        timeout = 10*24*60*60 # 10 days

    if mem_sys == "classic":
        run_script = os.path.join(GEM5_RESOURCES_FOLDER, "src/parsec/configs/run_parsec.py")
    else:
        run_script = os.path.join(GEM5_RESOURCES_FOLDER, "src/parsec/configs-mesi-two-level/run_parsec_mesi_two_level.py")

    gem5run = gem5Run.createFSRun(
        'parsec;'+RUN_NAME_SUFFIX, # name
        get_gem5_binary_path(mem_sys), # gem5_binary
        run_script, # run_script
        os.path.join(OUTPUT_FOLDER, 'parsec/{}/{}/{}/{}/{}/{}/'. format(kernel, cpu, num_cpu, mem_sys, workload, size)), # outdir
        gem5_binaries[mem_sys], # gem5_artifact
        gem5_repo, # gem5_git_artifact
        experiments_repo, # run_script_git_artifact
        os.path.join(LINUX_KERNELS_FOLDER, 'vmlinux'+'-'+kernel), # linux_binary
        os.path.join(DISK_IMAGES_FOLDER, 'parsec.img'), # disk_image
        linux_binaries[kernel], # linux_binary_artifact
        parsec_artifacts.disk_image, # disk_image_artifact
        cpu, workload, size, num_cpu, # params
        timeout = timeout,
        check_failure = lambda run_obj: linux_booting_check_failure(run_obj)
    )
    return gem5run

def create_parsec_20_04_fs_run(params):
    kernel = params['kernel']
    cpu = params['cpu']
    num_cpu = params['num_cpu']
    mem_sys = params['mem_sys']
    workload = params['workload']
    size = params['size']

    if cpu == "kvm":
        timeout = 24*60*60 # 1 day
    else:
        timeout = 10*24*60*60 # 10 days

    if mem_sys == "classic":
        run_script = os.path.join(GEM5_RESOURCES_FOLDER, "src/parsec/configs/run_parsec.py")
    else:
        run_script = os.path.join(GEM5_RESOURCES_FOLDER, "src/parsec/configs-mesi-two-level/run_parsec_mesi_two_level.py")

    gem5run = gem5Run.createFSRun(
        'parsec-20.04;'+RUN_NAME_SUFFIX, # name
        get_gem5_binary_path(mem_sys), # gem5_binary
        run_script, # run_script
        os.path.join(OUTPUT_FOLDER, 'parsec-20.04/{}/{}/{}/{}/{}/{}/'. format(kernel, cpu, num_cpu, mem_sys, workload, size)), # outdir
        gem5_binaries[mem_sys], # gem5_artifact
        gem5_repo, # gem5_git_artifact
        experiments_repo, # run_script_git_artifact
        os.path.join(LINUX_KERNELS_FOLDER, 'vmlinux'+'-'+kernel), # linux_binary
        os.path.join(DISK_IMAGES_FOLDER, 'parsec-20.04'), # disk_image
        linux_binaries[kernel], # linux_binary_artifact
        parsec_20_04_artifacts.disk_image, # disk_image_artifact
        cpu, workload, size, num_cpu, # params
        timeout = timeout,
        check_failure = lambda run_obj: linux_booting_check_failure(run_obj)
    )
    return gem5run

def create_spec_2006_fs_run(params):
    kernel = params['kernel']
    cpu = params['cpu']
    mem_sys = params['mem_sys']
    workload = params['workload']
    size = params['size']
    if cpu == "kvm":
        timeout = 24*60*60 # 1 day
    else:
        timeout = 20*24*60*60 # 20 days

    gem5run = gem5Run.createFSRun(
        'spec-2006;'+RUN_NAME_SUFFIX, # name
        get_gem5_binary_path(mem_sys), # gem5 binary
        os.path.join(GEM5_RESOURCES_FOLDER, 'src/spec-2006/configs/run_spec.py'), # run_script
        os.path.join(OUTPUT_FOLDER, 'spec-2006/{}/{}/{}/{}/{}/'. format(kernel, cpu, mem_sys, workload, size)), # outdir
        gem5_binaries[mem_sys], # gem5_artifact
        gem5_repo, # gem5_git_artifact
        experiments_repo, # run_script_git_artifact
        os.path.join(LINUX_KERNELS_FOLDER, 'vmlinux'+'-'+kernel), # linux_binary
        os.path.join(DISK_IMAGES_FOLDER, 'spec-2006'), # disk_image
        linux_binaries[kernel], # linux_binary_artifact
        spec_2006_artifacts.disk_image, # disk_image_artifact
        cpu, mem_sys, workload, size, # params
        timeout = timeout,
        check_failure = lambda run_obj: linux_booting_check_failure(run_obj)
    )
    return gem5run

def create_spec_2017_fs_run(params):
    kernel = params['kernel']
    cpu = params['cpu']
    workload = params['workload']
    size = params['size']
    if cpu == "kvm":
        timeout = 24*60*60 # 1 day
    else:
        timeout = 20*24*60*60 # 20 days

    gem5run = gem5Run.createFSRun(
        'spec-2017;'+RUN_NAME_SUFFIX, # name
        get_gem5_binary_path('classic'), # gem5_binary
        os.path.join(GEM5_RESOURCES_FOLDER, 'src/spec-2017/configs/run_spec.py'), # run_script
        os.path.join(OUTPUT_FOLDER, 'spec-2017/{}/{}/{}/{}/'. format(kernel, cpu, workload, size)), # outdir
        gem5_binaries['classic'], # gem5_artifact
        gem5_repo, # gem5_git_artifact
        experiments_repo, # run_script_git_artifact
        os.path.join(LINUX_KERNELS_FOLDER, 'vmlinux'+'-'+kernel), # linux_binary
        os.path.join(DISK_IMAGES_FOLDER, 'spec-2017'), # disk_image
        linux_binaries[kernel], # linux_binary_artifact
        spec_2017_artifacts.disk_image, # disk_image_artifact
        cpu, workload, size, # params
        timeout = timeout,
        check_failure = lambda run_obj: linux_booting_check_failure(run_obj)
    )
    return gem5run

name_create_fs_run_map = {
    'boot-exit': create_boot_exit_fs_run,
    'npb': create_npb_fs_run,
    'gapbs': create_gapbs_fs_run,
    'parsec': create_parsec_fs_run,
#	'parsec-20.04': create_parsec_20_04_fs_run,
    'spec-2006': create_spec_2006_fs_run,
    'spec-2017': create_spec_2017_fs_run
}

create_fs_run = lambda name, params: name_create_fs_run_map[name](params)

def worker(job):
    name, params = job
    run = create_fs_run(name, params)
    print("Starting running", name, params)
    try:
        run.run()
    except Exception as err:
        filepath = os.path.join(ERR_FOLDER, "_".join(list(params.values())))
        traceback.print_exc(file=open(filepath, "w"))

if __name__ == "__main__":
    parser = parser = argparse.ArgumentParser(description='Launch gem5art experiment.')
    parser.add_argument('--test', action='store_true', default = False)
    args = parser.parse_args()

    #def boot_exit_filter(name, params):
    #    if not name == "boot-exit":
    #        return False
    #    return True

    def kvm_filter(name, params):
        if not params["cpu"] == "kvm":
            return False
        return True

    jobs = list(get_jobs_iterator(kvm_filter))

    with open('jobs', 'w') as f:
        for job in jobs:
            f.write(str(job))
            f.write("\n")


    if not args.test:
        run_names = {name for name, _ in jobs}

        # since disk image artifacts are huge, here we lazily import artifacts as needed
        # we should do this before spliting the jobs to multiple processes as we don't want to import those artifacts multiple times
        for name in run_names:
            print("Loading {} artifacts".format(name))
            if name == "boot-exit":
                boot_exit_artifacts = get_boot_exit_artifacts()
            elif name == "npb":
                npb_artifacts = get_npb_artifacts()
            elif name == "gapbs":
                gapbs_artifacts = get_gapbs_artifacts()
            elif name == "parsec":
                parsec_artifacts = get_parsec_artifacts()
            elif name == "parsec-20.04":
                parsec_20_04_artifacts = get_parsec_20_04_artifacts()
            elif name == "spec-2006":
                spec_2006_artifacts = get_spec_2006_artifacts()
            elif name == "spec-2017":
                spec_2017_artifacts = get_spec_2017_artifacts()
            else:
                raise Error("Unknown fs run name")

    if not args.test:
        with mp.Pool(mp.cpu_count() // 2) as pool:
            pool.map(worker, jobs)

