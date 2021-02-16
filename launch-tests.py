from itertools import product as cross_product
import multiprocessing as mp
import os

from common_artifacts import *
from tests_artifacts import *
from filter_logic import *
import input_space

from gem5art.artifact.artifact import Artifact
from gem5art.run import gem5Run

OUTPUT_FOLDER = "/projects/gem5/gem5-resources-20.1/"

def lists_to_dict(keys, vals):
    return dict(zip(keys, vals))

def get_boot_tests_jobs_iterator():
    name = 'boot-tests'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.mem_sys, params.num_cpus, params.boot_types):
        kwargs = lists_to_dict(['kernel', 'cpu', 'mem_sys', 'num_cpu', 'boot_type'], p)
        if workload_filter(name, kwargs):
            yield kwargs

def get_npb_tests_jobs_iterator():
    name = 'npb-tests'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.mem_sys, params.num_cpus, params.workloads):
        kwargs = lists_to_dict(['kernel', 'cpu', 'mem_sys', 'num_cpu', 'workload'], p)
        if workload_filter(name, kwargs):
            yield kwargs

def get_gapbs_tests_jobs_iterator():
    name = 'gapbs-tests'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.num_cpus, params.mem_sys, params.workloads, params.synthetic):
        kwargs = lists_to_dict(['kernel', 'cpu', 'num_cpu', 'mem_sys', 'workload', 'synthetic'], p)
        if workload_filter(name, kwargs):
            yield kwargs

def get_parsec_tests_jobs_iterator():
    name = 'parsec-tests'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.mem_sys, params.num_cpus, params.workloads, params.sizes):
        kwargs = lists_to_dict(['kernel', 'cpu', 'mem_sys', 'num_cpu', 'workload', 'size'], p)
        if workload_filter(name, kwargs):
            yield kwargs

def get_spec2006_tests_jobs_iterator():
    name = 'spec2006-tests'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.workloads, params.sizes):
        kwargs = lists_to_dict(['kernel', 'cpu', 'workload', 'size'], p)
        if workload_filter(name, kwargs):
            yield kwargs

def get_spec2017_tests_jobs_iterator():
    name = 'spec2017-tests'
    params = input_space.name_params_map[name]
    for p in cross_product(params.kernels, params.cpu_types, params.workloads, params.sizes):
        kwargs = lists_to_dict(['kernel', 'cpu', 'workload', 'size'], p)
        if workload_filter(name, kwargs):
            yield kwargs

def get_jobs_iterator():
    iterators = [get_boot_tests_jobs_iterator(),
                 get_npb_tests_jobs_iterator(),
                 get_gapbs_tests_jobs_iterator(),
                 get_parsec_tests_jobs_iterator(),
                 get_spec2006_tests_jobs_iterator(),
                 get_spec2017_tests_jobs_iterator()]
    names = ['boot-tests', 'npb-tests', 'gapbs-tests', 'parsec-tests', 'spec2006-tests', 'spec2017-tests']
    for name, iterator in zip(names, iterators):
        while True:
            try:
                kwargs = next(iterator)
                yield (name, kwargs)
            except StopIteration:
                break

def get_gem5_binary_path(mem_sys):
    if mem_sys == "classic":
        return "/scr/hn/gem5-resources-launch/gem5/build/X86/gem5.opt"
    else:
        return "/scr/hn/gem5-resources-launch/gem5/build/X86_{}/gem5.opt".format(mem_sys)

# https://github.com/darchr/gem5art-experiments/blob/master/launch-scripts/launch_boot_tests_gem5_20.py#L128
def create_boot_tests_fs_run(params):
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
        'boot-exit;launched:02/16/2021;gem5art-status;v20.1.0.3', # name
        get_gem5_binary_path(mem_sys), # gem5_binary
        '/scr/hn/gem5-resources-launch/gem5-resources/src/boot-exit/configs/run_exit.py', # run_script
        os.path.join(OUTPUT_FODLER, 'boot-exit/{}/{}/{}/{}/{}/'. format(kernel, cpu, num_cpu, mem_sys, boot_type)), # outdir
        gem5_binaries[mem_sys], # gem5_artifact
        gem5_repo, # gem5_git_artifact
        experiments_repo, # run_script_git_artifact
        os.path.join('/scr/hn/gem5-resources-launch/linux-kernels', 'vmlinux'+'-'+kernel), # linux_binary
        '/scr/hn/gem5-resources-launch/disk-images/boot-exit.img', # disk_image
        linux_binaries[kernel], # linux_binary_artifact
        boot_tests_artifacts.disk_image, # disk_image_artifact
        cpu, mem_sys, num_cpu, boot_type, # params
        timeout = timeout
    )
    return gem5run

def create_npb_tests_fs_run(params):
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
            'npb;launch:02/16/2021;gem5art-status;v20.1.0.3', # name
            get_gem5_binary_path(mem_sys), # gem5_binary
            '/scr/hn/gem5-resources-launch/gem5-resources/src/npb/configs/run_npb.py', # run_script
            os.path.join(OUTPUT_FOLDER, 'npb/{}/{}/{}/{}/{}/'. format(kernel, cpu, num_cpu, mem_sys, workload)), # outdir
            gem5_binaries[mem_sys], # gem5_artifact
            gem5_repo, # gem5_git_artifact
            experiments_repo, # run_script_git_artifact
            os.path.join('/scr/hn/gem5-resources-launch/linux-kernels', 'vmlinux'+'-'+kernel), # linux_binary
            '/scr/hn/gem5-resources-launch/disk-images/npb.img', # disk_image
            linux_binaries[kernel], # linux_binary_artifact
            npb_tests_artifacts.disk_image, # disk_image_artifact
            cpu, mem_sys, workload, num_cpu, # params
            timeout = timeout
    )
    return gem5run

def create_gapbs_tests_fs_run(params):
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
        'gapbs;launch:02/16/2021;gem5art-status;v20.1.0.3', # name
        get_gem5_binary_path(mem_sys), # gem5_binary
        '/scr/hn/gem5-resources-launch/gem5-resources/src/gapbs/configs/run_gapbs.py', # run_script
        os.path.join(OUTPUT_FOLDER, 'gapbs/{}/{}/{}/{}/{}/{}/{}/'. format(kernel, cpu, num_cpu, mem_sys, workload, synthetic, graph)), # outdir
        gem5_binaries[mem_sys], # gem5_artifact
        gem5_repo, # gem5_git_artifact
        experiments_repo, # run_script_git_artifact
        os.path.join('/scr/hn/gem5-resources-launch/linux-kernels', 'vmlinux'+'-'+kernel), # linux_binary
        '/scr/hn/gem5-resources-launch/disk-images/gapbs.img', # disk_image
        linux_binaries[kernel], # linux_binary_artifact
        gapbs_tests_artifacts.disk_image, # disk_image_artifact
        cpu, num_cpu, mem_sys, workload, synthetic, graph, # params
        timeout = timeout
    )
    return gem5run

def create_parsec_tests_fs_run(params):
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
        run_script = "/scr/hn/gem5-resources-launch/gem5-resources/src/parsec/configs/run_parsec.py"
    else:
        run_script = "/scr/hn/gem5-resources-launch/gem5-resources/src/parsec/configs-mesi-two-level/run_parsec_mesi_two_level.py"

    gem5run = gem5Run.createFSRun(
        'parsec;launch:02/16/2021;gem5art-status;v20.1.0.3', # name
        get_gem5_binary_path(mem_sys), # gem5_binary
        run_script, # run_script
        os.path.join(OUTPUT_FOLDER, 'parsec/{}/{}/{}/{}/{}/{}/'. format(kernel, cpu, num_cpu, mem_sys, workload, size)), # outdir
        gem5_binaries[mem_sys], # gem5_artifact
        gem5_repo, # gem5_git_artifact
        experiments_repo, # run_script_git_artifact
        os.path.join('/scr/hn/gem5-resources-launch/linux-kernels', 'vmlinux'+'-'+kernel), # linux_binary
        '/scr/hn/gem5-resources-launch/disk-images/parsec.img', # disk_image
        linux_binaries[kernel], # linux_binary_artifact
        parsec_tests_artifacts.disk_image, # disk_image_artifact
        cpu, workload, size, num_cpu, # params
        timeout = timeout
    )
    return gem5run    

def create_spec2006_tests_fs_run(params):
    kernel = params['kernel']
    cpu = params['cpu']
    workload = params['workload']
    size = params['size']
    if cpu == "kvm":
        timeout = 24*60*60 # 1 day
    else:
        timeout = 10*24*60*60 # 10 days
    gem5run = gem5Run.createFSRun(
        'spec-2006;launch:02/16/2021;gem5art-status;v20.1.0.3', # name
        get_gem5_binary_path('classic'), # gem5 binary
        '/scr/hn/gem5-resources-launch/gem5-resources/src/spec-2006/configs/run_spec.py', # run_script
        os.path.join(OUTPUT_FOLDER, 'spec-2006/{}/{}/{}/{}/'. format(kernel, cpu, workload, size)), # outdir
        gem5_binaries['classic'], # gem5_artifact
        gem5_repo, # gem5_git_artifact
        experiments_repo, # run_script_git_artifact
        os.path.join('/scr/hn/gem5-resources-launch/linux-kernels', 'vmlinux'+'-'+kernel), # linux_binary
        '/scr/hn/gem5-resources-launch/disk-images/spec-2006', # disk_image
        linux_binaries[kernel], # linux_binary_artifact
        spec2006_tests_artifacts.disk_image, # disk_image_artifact
        cpu, workload, size, # params
        timeout = timeout
    )
    return gem5run

def create_spec2017_tests_fs_run(params):
    kernel = params['kernel']
    cpu = params['cpu']
    workload = params['workload']
    size = params['size']
    if cpu == "kvm":
        timeout = 24*60*60 # 1 day
    else:
        timeout = 10*24*60*60 # 10 days
    gem5run = gem5Run.createFSRun(
        'spec-2017;launch:02/16/2021;gem5art-status;v20.1.0.3', # name
        get_gem5_binary_path('classic'), # gem5_binary
        '/scr/hn/gem5-resources-launch/gem5-resources/src/spec-2017/configs/run_spec.py', # run_script
        os.path.join(OUTPUT_FOLDER, 'spec-2017/{}/{}/{}/{}/'. format(kernel, cpu, workload, size)), # outdir
        gem5_binaries['classic'], # gem5_artifact
        gem5_repo, # gem5_git_artifact
        experiments_repo, # run_script_git_artifact
        os.path.join('/scr/hn/gem5-resources-launch/linux-kernels', 'vmlinux'+'-'+kernel), # linux_binary
        '/scr/hn/gem5-resources-launch/disk-images/spec-2017', # disk_image
        linux_binaries[kernel], # linux_binary_artifact
        spec2017_tests_artifacts.disk_image, # disk_image_artifact
        cpu, workload, size, '-z', # params
        timeout = timeout
    )
    return gem5run

name_create_fs_run_map = {
    'boot-tests': create_boot_tests_fs_run,
    'npb-tests': create_npb_tests_fs_run,
    'gapbs-tests': create_gapbs_tests_fs_run,
    'parsec-tests': create_parsec_tests_fs_run,
    'spec2006-tests': create_spec2006_tests_fs_run,
    'spec2017-tests': create_spec2017_tests_fs_run
}

create_fs_run = lambda name, params: name_create_fs_run_map[name](params)

def worker(job):
    name, params = job
    run = create_fs_run(name, params)
    print("Starting running", params)
    run.run()

if __name__ == "__main__":
    jobs = get_jobs_iterator()
    with open('jobs', 'w') as f:
        for job in jobs:
            f.write(str(job))
            f.write("\n")
    jobs = get_jobs_iterator()
    with mp.Pool(mp.cpu_count() // 3 * 2) as pool:
        pool.map(worker, jobs)
