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
                 git checkout v20.1.0.3
                 git fetch https://gem5.googlesource.com/public/gem5 refs/changes/94/41594/3 && git cherry-pick FETCH_HEAD''',
    typ = 'git repo',
    name = 'gem5',
    path =  'gem5/',
    cwd = './',
    documentation = '''Cloned gem5 from googlesource, checked out the v20.1.0.3 tag and cherry-picked the scons 4 hotfix.
                       Note that at the time of running this experiment, the scons 4 hotfix has not been merged, thus the cherry-picking change.
                       The HEAD commit is: eab8ae6eafa6caa730d714aa72741e1dabf99fb6
                       Change-Id: I3817f39ebc3021fb6fc89bcd09a96999f8ca2841'''
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
                scons build/X86_{mem}/gem5.opt --default=X86 PROTOCOL={mem} -j256
                ''',
                typ = 'gem5 binary',
                name = f'gem5-{mem}',
                cwd = 'gem5/',
                path =  f'gem5/build/X86_{mem}/gem5.opt',
                inputs = [gem5_repo,],
                documentation = f'gem5 {mem} binary based on '
                    'gem5 v20.1.0.3 and cherry-picked scons 4 hotfix'
                    'The HEAD commit is: eab8ae6eafa6caa730d714aa72741e1dabf99fb6'
                    'Change-Id: I3817f39ebc3021fb6fc89bcd09a96999f8ca2841'
                )
        for mem in ruby_mem_types
}

gem5_binaries['classic'] = Artifact.registerArtifact(
    command = f'''cd gem5;
    scons build/X86/gem5.opt -j256
    ''',
    typ = 'gem5 binary',
    name = f'gem5-classic',
    cwd = 'gem5/',
    path =  f'gem5/build/X86/gem5.opt',
    inputs = [gem5_repo],
    documentation = 'gem5 binary based on gem5 v20.1.0.3 and cherry-picked scons 4 hotfix'
    'The HEAD commit is: eab8ae6eafa6caa730d714aa72741e1dabf99fb6'
    'Change-Id: eab8ae6eafa6caa730d714aa72741e1dabf99fb6'
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
                command = f'''wget http://dist.gem5.org/dist/v20-1/kernels/x86/static/vmlinux-{version}''',
                inputs = [experiments_repo],
                documentation = f"Kernel binary for {version} with simple "
                                 "config file",
            )
    for version in linux_versions
}
# ---
