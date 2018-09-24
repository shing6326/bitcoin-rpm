## Bitcoin

The rpm source for bitcoin daemon.
For more details of bitcoin, please visit https://github.com/bitcoin/bitcoin

## Building the source rpm

Install rpmspectool to download the source files inside rpm spec
```bash
yum install rpmspectool
```

Install mock environment to build the rpm
https://github.com/rpm-software-management/mock/wiki

Copy the spec file from repository
```bash
cd ~
mkdir rpmbuild/SPECS
cp SPECS/bitcoin.spec rpmbuild/SPECS/
```

Download the source file and build source rpm
```bash
spectool -g -R rpmbuild/SPECS/bitcoin.spec
```

Build the source rpm using mock
```bash
mock --resultdir=$HOME --buildsrpm --spec rpmbuild/SPECS/bitcoin.spec --sources rpmbuild/SOURCES -v
```

Compile
```bash
mock -v bitcoin-0.16.3-1.el7.src.rpm
```
