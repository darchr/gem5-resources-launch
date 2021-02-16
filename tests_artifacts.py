from types import SimpleNamespace

from common_artifacts import *

from gem5art.artifact.artifact import Artifact

tests = ['boot-tests',
         'npb-tests',
         'gapbs-tests',
         'parsec-tests',
         'spec2006-tests',
         'spec2017-tests']

packer_binaries = {
    test: Artifact.registerArtifact(
        command = '''wget https://releases.hashicorp.com/packer/1.6.5/packer_1.6.5_linux_amd64.zip;
        unzip packer_1.6.5_linux_amd64.zip;
        ''',
        typ = 'binary',
        name = 'packer',
        path =  test+'/disk-image/packer',
        cwd = test+'/disk-image',
        documentation = 'Program to build disk images'
    )
    for test in tests
}

# boot-tests
boot_tests_disk_image = Artifact.registerArtifact(
    command = '''wget http://dist.gem5.org/dist/v20-1/images/x86/ubuntu-18-04/boot-exit.img.gz;
                 gunzip boot-exit.img.gz''',
    typ = 'disk image',
    name = 'boot-exit-disk-image',
    cwd = 'disk-images/',
    path = 'disk-images/boot-exit.img',
    documentation = 'Ubuntu with m5 binary installed and root auto login'
) 
boot_tests_artifacts = SimpleNamespace(disk_image = boot_tests_disk_image)
# ---

# npb-tests
npb_tests_disk_image = Artifact.registerArtifact(
    command = '''wget http://dist.gem5.org/dist/v20-1/images/x86/ubuntu-18-04/npb.img.gz;
                 gunzip npb.img.gz''',
    typ = 'disk image',
    name = 'npb-disk-image',
    cwd = 'disk-images',
    path = 'disk-images/npb.img',
    documentation = 'Ubuntu with m5 binary and NPB (with ROI annotations: darchr/npb-hooks/gem5art-npb-tutorial) installed.'
)
npb_tests_artifacts = SimpleNamespace(disk_image = npb_tests_disk_image)
# ---

# gapbs-tests
gapbs_tests_disk_image = Artifact.registerArtifact(
    command = '''wget http://dist.gem5.org/dist/v20-1/images/x86/ubuntu-18-04/gapbs.img.gz;
                 gunzip gapbs.img.gz;''',
    typ = 'disk image',
    name = 'gapbs-disk-image',
    cwd = 'disk-images',
    path = 'disk-images/gapbs.img',
    documentation = 'Ubuntu with m5 binary installed and root auto login and gapbs installed'
)
gapbs_tests_artifacts = SimpleNamespace(disk_image = gapbs_tests_disk_image)
# ---

# parsec-tests
parsec_tests_disk_image = Artifact.registerArtifact(
    command = '''wget http://dist.gem5.org/dist/v20-1/images/x86/ubuntu-18-04/parsec.img.gz;
                 gunzip parsec.img.gz;''',
    typ = 'disk image',
    name = 'parsec-disk-image',
    cwd = 'disk-images',
    path = 'disk-images/parsec.img',
    documentation = 'Disk-image using Ubuntu 18.04 with m5 binary and PARSEC installed'
)
parsec_tests_artifacts = SimpleNamespace(disk_image = parsec_tests_disk_image)
# ---

# spec2006-tests
spec2006_tests_disk_image = Artifact.registerArtifact(
    command = '''./packer build spec-2006/spec-2006.json;
                 mv disk-image/spec-2006/spec-2006-image/spec-2006 ../../../disk-images/''',
    typ = 'disk image',
    name = 'spec-2006-disk-image',
    cwd = 'gem5-resources/src/spec-2006/disk-image',
    path = 'disk-images/spec-2006',
    inputs = [packer_binaries['spec2006-tests'], experiments_repo, m5_binary],
    documentation = 'Ubuntu Server with SPEC 2006 installed, m5 binary installed and root auto login'
)
spec2006_tests_artifacts = SimpleNamespace(disk_image = spec2006_tests_disk_image)
# ---

# spec2017-tests
spec2017_tests_disk_image = Artifact.registerArtifact(
    command = '''./packer build spec2017/spec2017.json;
                 mv disk-image/spec-2017/spec-2017-image/spec-2017 ../../../disk-images/''',
    typ = 'disk image',
    name = 'spec-2017-disk-image',
    cwd = 'gem5-resources/src/spec-2017/disk-image/',
    path = 'disk-images/spec20-17',
    inputs = [packer_binaries['spec2017-tests'], experiments_repo, m5_binary],
    documentation = 'Ubuntu Server with SPEC 2017 installed, m5 binary installed and root auto login'
)
spec2017_tests_artifacts = SimpleNamespace(disk_image = spec2017_tests_disk_image)
# ---

