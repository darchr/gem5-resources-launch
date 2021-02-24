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


ABS_PATH = pathlib.Path(__file__).parent.absolute()

OUTPUT_FOLDER = "/projects/gem5/gem5-resources-20.1/"
ERR_FOLDER = os.join.path(ABS_PATH, "error_logs/")
GEM5_FOLDER = os.join.path(ABS_PATH, "gem5/")
GEM5_RESOURCES_FOLDER = os.join.path(ABS_PATH, "gem5-resources/")
DISK_IMAGES_FOLDER = os.join.path(ABS_PATH, "disk-images/")
LINUX_KERNELS_FOLDER = os.join.path(ABS_PATH, "linux-kernels/")
RUN_NAME_SUFFIX = "launched:02/23/2021;gem5art-status;v20.1.0.4;kvm;lavandula-angustifolia"

def lists_to_dict(keys, vals):
    return dict(zip(keys, vals))

def to_abs_path(path): # return the absoblute path of a relative path, assuming the relative path to be relative to the folder containing this script
    return os.path.join(ABS_PATH, path)

def get_boot_exit_jobs_iterator():
    name = 'boot-exit'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.mem_sys, params.num_cpus, params.boot_types):
        kwargs = lists_to_dict(['kernel', 'cpu', 'mem_sys', 'num_cpu', 'boot_type'], p)
        if workload_filter(name, kwargs):
            yield kwargs

def get_npb_jobs_iterator():
    name = 'npb'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.mem_sys, params.num_cpus, params.workloads):
        kwargs = lists_to_dict(['kernel', 'cpu', 'mem_sys', 'num_cpu', 'workload'], p)
        if workload_filter(name, kwargs):
            yield kwargs

def get_gapbs_jobs_iterator():
    name = 'gapbs'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.num_cpus, params.mem_sys, params.workloads, params.synthetic):
        kwargs = lists_to_dict(['kernel', 'cpu', 'num_cpu', 'mem_sys', 'workload', 'synthetic'], p)
        if workload_filter(name, kwargs):
            yield kwargs

def get_parsec_jobs_iterator():
    name = 'parsec'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.mem_sys, params.num_cpus, params.workloads, params.sizes):
        kwargs = lists_to_dict(['kernel', 'cpu', 'mem_sys', 'num_cpu', 'workload', 'size'], p)
        if workload_filter(name, kwargs):
            yield kwargs

def get_spec_2006_jobs_iterator():
    name = 'spec-2006'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.mem_sys, params.workloads, params.sizes):
        kwargs = lists_to_dict(['kernel', 'cpu', 'mem_sys', 'workload', 'size'], p)
        if workload_filter(name, kwargs):
            yield kwargs

def get_spec_2017_jobs_iterator():
    name = 'spec-2017'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.workloads, params.sizes):
        kwargs = lists_to_dict(['kernel', 'cpu', 'workload', 'size'], p)
        if workload_filter(name, kwargs):
            yield kwargs

def get_jobs_iterator():
    iterators = [get_boot_exit_jobs_iterator(),
                 get_npb_jobs_iterator(),
                 get_gapbs_jobs_iterator(),
                 get_parsec_jobs_iterator(),
                 get_spec_2006_jobs_iterator(),
                 get_spec_2017_jobs_iterator()]
    names = ['boot-exit', 'npb', 'gapbs', 'parsec', 'spec-2006', 'spec-2017']
    for name, iterator in zip(names, iterators):
        while True:
            try:
                kwargs = next(iterator)
                yield (name, kwargs)
            except StopIteration:
                break

def get_gem5_binary_path(mem_sys):
    if mem_sys == "classic":
        return os.path.join(GEM5_FOLDER, "build/X86/gem5.opt")
    else:
        return os.path.join(GEM5_FOLDER, "build/X86_{}/gem5.opt".format(mem_sys))

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
        timeout = 24*60*60 # 1 day
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
        timeout = timeout
    )
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
            timeout = timeout
    )
    return gem5run

def create_gapbs_fs_run(params):
    kernel = params['kernel']
    cpu = params['cpu']
    num_cpu = params['num_cpu']
    mem_sys = params['mem_sys']
    workload = params['workload']
    synthetic = params['synthetic']
    graph = workload
    if cpu == "kvm":
        timeout = 24*60*60 # 1 day
    else:
        timeout = 10*24*60*60 # 10 days
    gem5run = gem5Run.createFSRun(
        'gapbs;'+RUN_NAME_SUFFIX, # name
        get_gem5_binary_path(mem_sys), # gem5_binary
        os.path.join(GEM5_RESOURCES_FOLDER, 'src/gapbs/configs/run_gapbs.py'), # run_script
        os.path.join(OUTPUT_FOLDER, 'gapbs/{}/{}/{}/{}/{}/{}/{}/'. format(kernel, cpu, num_cpu, mem_sys, workload, synthetic, graph)), # outdir
        gem5_binaries[mem_sys], # gem5_artifact
        gem5_repo, # gem5_git_artifact
        experiments_repo, # run_script_git_artifact
        os.path.join(LINUX_KERNELS_FOLDER, 'vmlinux'+'-'+kernel), # linux_binary
        os.path.join(DISK_IMAGES_FOLDER, 'gapbs.img'), # disk_image
        linux_binaries[kernel], # linux_binary_artifact
        gapbs_artifacts.disk_image, # disk_image_artifact
        cpu, num_cpu, mem_sys, workload, synthetic, graph, # params
        timeout = timeout
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
        timeout = timeout
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
        timeout = 10*24*60*60 # 10 days
    gem5run = gem5Run.createFSRun(
        'spec-2006;'+RUN_NAME_SUFFIX, # name
        get_gem5_binary_path('classic'), # gem5 binary
        os.path.join(GEM5_RESOURCES_FOLDER, 'src/spec-2006/configs/run_spec.py'), # run_script
        os.path.join(OUTPUT_FOLDER, 'spec-2006/{}/{}/{}/{}/{}/'. format(kernel, cpu, mem_sys, workload, size)), # outdir
        gem5_binaries['classic'], # gem5_artifact
        gem5_repo, # gem5_git_artifact
        experiments_repo, # run_script_git_artifact
        os.path.join(LINUX_KERNELS_FOLDER, 'vmlinux'+'-'+kernel), # linux_binary
        os.path.join(DISK_IMAGES_FOLDER, 'spec-2006'), # disk_image
        linux_binaries[kernel], # linux_binary_artifact
        spec_2006_artifacts.disk_image, # disk_image_artifact
        cpu, mem_sys, workload, size, # params
        timeout = timeout
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
        timeout = 10*24*60*60 # 10 days
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
        spec_2017_tests_artifacts.disk_image, # disk_image_artifact
        cpu, workload, size, # params
        timeout = timeout
    )
    return gem5run

name_create_fs_run_map = {
    'boot-exit': create_boot_exit_fs_run,
    'npb': create_npb_fs_run,
    'gapbs': create_gapbs_fs_run,
    'parsec': create_parsec_fs_run,
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
        filepath = os.path.join(ERR_FOLDER, "/".join(list(params.values())))
        filepath = os.path.join(filepath, 'err.txt')
        traceback.print_exc(file=open(filepath, "w"))

if __name__ == "__main__":
    jobs = get_jobs_iterator()
    with open('jobs', 'w') as f:
        for job in jobs:
            f.write(str(job))
            f.write("\n")
    jobs = get_jobs_iterator()
    with mp.Pool(mp.cpu_count() // 3 * 2) as pool:
        pool.map(worker, jobs)

