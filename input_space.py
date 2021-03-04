from types import SimpleNamespace

boot_exit_params = SimpleNamespace(
    kernels = ['4.4.186', '4.9.186', '4.14.134', '4.19.83', '5.4.49'],
    cpu_types = ['kvm', 'atomic', 'simple', 'o3'],
    mem_sys = ['classic', 'MI_example', 'MESI_Two_Level', 'MOESI_CMP_directory'],
    num_cpus = ['1', '2', '4', '8'],
    boot_types = ['init', 'systemd']
)

npb_params = SimpleNamespace(
    kernels = ['4.19.83'],
    cpu_types = ['kvm', 'timing'],
    #mem_sys = ['classic', 'MI_example', 'MESI_Two_Level', 'MOESI_CMP_directory'],
    mem_sys = ['classic', 'MESI_Two_Level'],
    num_cpus = ['1', '8', '16', '32', '64'],
    workloads = ['is.A.x', 'ep.A.x', 'cg.A.x', 'mg.A.x','ft.A.x', 'bt.A.x', 'sp.A.x', 'lu.A.x']
)

gapbs_params = SimpleNamespace(
    kernels = ['5.4.49'],
    cpu_types = ['kvm', 'atomic', 'simple', 'o3'],
    num_cpus = ['1', '2', '4'],
    mem_sys = ['classic', 'MI_example', 'MESI_Two_Level'],
    workloads = ['cc', 'bc', 'bfs', 'tc', 'pr', 'sssp'],
    synthetic = ['1'],
    n_nodes = ['10'] # 2**10 nodes
    #graph = name of the workload
)

parsec_params = SimpleNamespace(
    kernels = ['4.19.83', '4.15.18'],
    cpu_types = ['kvm', 'timing'],
    mem_sys = ['classic', 'MESI_Two_Level'],
    num_cpus = ['1', '2', '8'],
    workloads = ['blackscholes', 'bodytrack', 'canneal', 'dedup', 'facesim', 'ferret',
                 'fluidanimate', 'freqmine', 'raytrace', 'streamcluster', 'swaptions',
                 'vips', 'x264'],
    sizes = ['simsmall', 'simmedium', 'simlarge', 'native'],
    notes = """KVM + Classic : All Sizes + 1 cpu
               KVM + MESI_Two_Level: All Sizes + [1, 2, 8] cpu
               Timing + Classic: simsmall + 1 cpu
               Timing + MESI_Two_Level: simsmall + [1, 2, 8] cpu"""
)

parsec_20_04_params = SimpleNamespace(
    kernels = ['5.4.51'],
    cpu_types = ['kvm', 'timing'],
    mem_sys = ['classic', 'MESI_Two_Level'],
    num_cpus = ['1', '2', '8'],
    workloads = ['blackscholes', 'bodytrack', 'canneal', 'dedup', 'facesim', 'ferret',
                 'fluidanimate', 'freqmine', 'raytrace', 'streamcluster', 'swaptions',
                 'vips', 'x264'],
    sizes = ['simsmall', 'simmedium', 'simlarge', 'native'],
    notes = """KVM + Classic : All Sizes + 1 cpu
               KVM + MESI_Two_Level: All Sizes + [1, 2, 8] cpu
               Timing + Classic: simsmall + 1 cpu
               Timing + MESI_Two_Level: simsmall + [1, 2] cpu"""
)

spec_2006_params = SimpleNamespace(
    kernels = ['4.19.83'],
    cpu_types = ['kvm', 'atomic', 'timing', 'o3'],
    mem_sys = ['classic', 'MI_example', 'MESI_Two_Level', 'MOESI_CMP_directory'],
    workloads = ['401.bzip2','403.gcc','410.bwaves','416.gamess','429.mcf',
                  '433.milc','434.zeusmp','435.gromacs','436.cactusADM',
                  '437.leslie3d','444.namd','445.gobmk','453.povray',
                  '454.calculix','456.hmmer','458.sjeng','459.GemsFDTD',
                  '462.libquantum','464.h264ref','465.tonto','470.lbm',
                  '471.omnetpp','473.astar','481.wrf','482.sphinx3',
                  '998.specrand','999.specrand'],
    sizes = ['test', 'ref'],
    notes = """ kvm: [test, ref] x the rest
                other cpus: [test] x the rest"""
)

spec_2017_params = SimpleNamespace(
    kernels = ['4.19.83'],
    cpu_types = ['kvm', 'atomic', 'timing', 'o3'],
    workloads = ["503.bwaves_r", "507.cactuBSSN_r", "508.namd_r", "510.parest_r", "511.povray_r", "519.lbm_r",
                  "521.wrf_r", "526.blender_r", "527.cam4_r", "538.imagick_r", "544.nab_r", "549.fotonik3d_r",
                  "554.roms_r", "997.specrand_fr", "603.bwaves_s", "607.cactuBSSN_s", "619.lbm_s", "621.wrf_s",
                  "627.cam4_s", "628.pop2_s", "638.imagick_s", "644.nab_s", "649.fotonik3d_s", "654.roms_s",
                  "996.specrand_fs", "500.perlbench_r", "502.gcc_r", "505.mcf_r", "520.omnetpp_r", "523.xalancbmk_r",
                  "525.x264_r", "531.deepsjeng_r", "541.leela_r", "548.exchange2_r", "557.xz_r", "999.specrand_ir",
                  "600.perlbench_s", "602.gcc_s", "605.mcf_s", "620.omnetpp_s", "623.xalancbmk_s", "625.x264_s",
                  "631.deepsjeng_s", "641.leela_s", "648.exchange2_s", "657.xz_s", "998.specrand_is"],
    sizes = ['test', 'ref'],
    notes = """ kvm: [test, ref] x the rest
                other cpus: [test] x the rest"""
)

name_params_map = {
    'boot-exit': boot_exit_params,
    'npb': npb_params,
    'gapbs': gapbs_params,
    'parsec': parsec_params,
    'parsec-20.04': parsec_20_04_params,
    'spec-2006': spec_2006_params,
    'spec-2017': spec_2017_params
}


