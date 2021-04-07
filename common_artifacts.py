from gem5art.artifact.artifact import Artifact

# Infomation about this tests repo
experiments_repo = Artifact.registerArtifact(
    command = 'git clone https://to-be-finalized',
    typ = 'git repo',
    name = 'gem5art-tests',
    path =  './',
    cwd = '../',
    documentation = 'main experiments repo to run all full system tests with gem5'
)
# ---

# gem5 artifacts
gem5_repo = Artifact.registerArtifact(
    command = '''git clone https://gem5.googlesource.com/public/gem5
                 cd gem5;
                 git checkout v21.0.0.0''',
    typ = 'git repo',
    name = 'gem5',
    path =  'gem5/',
    cwd = './',
    documentation = '''Cloned gem5 from googlesource, checked out the v21.0.0.0 tag.
                       The HEAD commit is: ea7d012c00e5555857ef999b88a8ec2bde801a1f'''
)

m5_binary = Artifact.registerArtifact(
    command = 'scons build/x86/out/m5',
    typ = 'binary',
    name = 'm5',
    path =  'gem5/util/m5/build/x86/out/m5',
    cwd = 'gem5/util/m5',
    inputs = [gem5_repo,],
    documentation = 'm5 utility'
)


ruby_mem_types = ['MI_example', 'MESI_Two_Level', 'MOESI_CMP_directory']
gem5_binaries = {
        mem: Artifact.registerArtifact(
                command = f'''cd gem5;
                scons build/X86_{mem}/gem5.opt --default=X86 PROTOCOL={mem} -j48
                ''',
                typ = 'gem5 binary',
                name = f'gem5-{mem}',
                cwd = 'gem5/',
                path =  f'gem5/build/X86_{mem}/gem5.opt',
                inputs = [gem5_repo,],
                documentation = f'gem5 {mem} binary based on '
                    'gem5 v21.0.0.0'
                    'The HEAD commit is: ea7d012c00e5555857ef999b88a8ec2bde801a1f'
                )
        for mem in ruby_mem_types
}

gem5_binaries['classic'] = Artifact.registerArtifact(
    command = f'''cd gem5;
    scons build/X86/gem5.opt -j48
    ''',
    typ = 'gem5 binary',
    name = f'gem5-classic',
    cwd = 'gem5/',
    path =  f'gem5/build/X86/gem5.opt',
    inputs = [gem5_repo],
    documentation = 'gem5 binary based on gem5 v21.0.0.0'
    'The HEAD commit is: ea7d012c00e5555857ef999b88a8ec2bde801a1f'
)
# ---

# Linux kernels
linux_versions = ['5.4.49', '4.19.83', '4.14.134', '4.9.186', '4.4.186']
linux_binaries = {
    version: Artifact.registerArtifact(
                name = f'vmlinux-{version}',
                typ = 'kernel',
                path = f'linux-kernels/vmlinux-{version}',
                cwd = 'linux-kernels/',
                command = f'''wget http://dist.gem5.org/dist/v21-0/kernels/x86/static/vmlinux-{version}''',
                inputs = [experiments_repo],
                documentation = f"Kernel binary for {version} with simple "
                                 "config file",
            )
    for version in linux_versions
}
# ---


# manually compiled Linux kernels
#linux_versions = ['5.4.51', '4.15.18']
#linux_git_artifact = {}
#linux_git_artifact['5.4.51'] = Artifact.registerArtifact(
#    name = f"linux kernel version 5.4.51 git repo",
#    typ = "git repo",
#    path = "linux-kernels/linux-5.4.51",
#    cwd = "./linux-kernels",
#    command = """
#        git clone --branch v5.4.51 --depth 1 https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/ linux-5.4.51;
#    """,
#    documentation = f"linux kernel version 5.4.51 source code"
#)
#
#linux_binaries['5.4.51'] = Artifact.registerArtifact(
#    name = f'vmlinux-5.4.51',
#    typ = 'kernel',
#    path = f'linux-kernels/vmlinux-5.4.51',
#    cwd = 'linux-kernels',
#    command = '''
#    cd linux-5.4.51;
#    cp ../../gem5-resources/src/linux-kernel/linux-configs/config.5.4.51 .config;
#    yes '' | make oldconfig;
#    make -j 32;
#    cp vmlinux ../vmlinux-5.4.51;
#    ''',
#    inputs = [experiments_repo, linux_git_artifact['5.4.51']],
#    documentation = f"Kernel binary for 5.4.51 with a simple config file"
#)
#
#linux_git_artifact['4.15.18'] = Artifact.registerArtifact(
#    name = f"linux kernel version 4.15.18 git repo",
#    typ = "git repo",
#    path = "linux-kernels/linux-4.15.18",
#    cwd = "./linux-kernels",
#    command = """
#        git clone --branch v4.15.18 --depth 1 https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/ linux-4.15.18;
#    """,
#    documentation = f"linux kernel version 4.15.18 source code"
#)
#
#linux_binaries['4.15.18'] = Artifact.registerArtifact(
#    name = f'vmlinux-4.15.18',
#    typ = 'kernel',
#    path = f'linux-kernels/vmlinux-4.15.18',
#    cwd = 'linux-kernels',
#    command = '''
#    cd linux-4.15.18;
#    cp ../../gem5-resources/src/linux-kernel/linux-configs/config.4.9.186 .config;
#    yes '' | make oldconfig;
#    make -j 32;
#    cp vmlinux ../vmlinux-4.15.18
#    ''',
#    inputs = [experiments_repo, linux_git_artifact['4.15.18']],
#    documentation = f"Kernel binary for 4.15.18 with a simple config file"
#)

