# for those combinations that are not being supported
def universal_filter(params):
    if 'cpu' in params and 'mem_sys' in params and params['cpu'] == "atomic" and not params['mem_sys'] == "classic":
        return False
    #if 'cpu' in params and 'num_cpu' in params and params['cpu'] == "o3" and not params['num_cpu'] == "1" and 'mem_sys' in params and params['mem_sys'] == 'classic':
    if 'cpu' in params and params['cpu'] == 'o3':
        if 'mem_sys' in params and params['mem_sys'] == 'classic':
            if 'num_cpu' in params and not params['num_cpu'] == '1':
                return False
    return True

# https://www.gem5.org/documentation/benchmark_status/#boot-tests
def boot_filter(params):
    return True

def npb_filter(params):
    if params['cpu'] == "timing" and not params['num_cpu'] in ["1", "8"]:
        return False
    return True

# https://www.gem5.org/documentation/benchmark_status/#gapbs-tests
def gapbs_filter(params):
    if params['cpu'] == "atomic" and not params['mem_sys'] == "classic":
        return False
    return True

"""
KVM + Classic : All Sizes + 1 cpu
KVM + MESI_Two_Level: All Sizes + [1, 2, 8] cpu
Timing + Classic: simsmall + 1 cpu
Timing + MESI_Two_Level: simsmall + [1, 2] cpu
"""
def parsec_filter(params):
    if params['cpu'] == "kvm" and params['mem_sys'] == "classic":
        if params['num_cpu'] == "1":
            return True
    elif params['cpu'] == "kvm" and params['mem_sys'] == "MESI_Two_Level":
        return True
    elif params['cpu'] == "timing" and params['mem_sys'] == "classic":
        if params['size'] == "simsmall" and params['num_cpu'] == "1":
            return True
    elif params['cpu'] == "timing" and params['mem_sys'] == "MESI_Two_Level":
        if params['size'] == "simsmall" and params['num_cpu'] in ["1", "2"]:
            return True
        if params['size'] == "simmedium":
            return True
    return False

def spec2006_filter(params):
    if params['size'] == "ref" and not params['cpu'] == "kvm":
        return False
    return True

def spec2017_filter(params):
    if params['size'] == "ref" and not params['cpu'] == "kvm":
        return False
    return True

tests_filters_map = {
    'boot-exit': boot_filter,
    'npb': npb_filter,
    'gapbs': gapbs_filter,
    'parsec': parsec_filter,
    'parsec-20.04': parsec_filter,
    'spec-2006': spec2006_filter,
    'spec-2017': spec2017_filter
}

def workload_filter(name, params, custom_filter):
    return custom_filter(name, params) and tests_filters_map[name](params) and universal_filter(params)
