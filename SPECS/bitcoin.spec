%if 0%{?_no_wallet}
%define walletargs --disable-wallet
%define _buildqt 0
%define guiargs --with-gui=no
%else
%if 0%{?_no_gui}
%define _buildqt 0
%define guiargs --with-gui=no
%else
%define _buildqt 1
%define guiargs --with-qrencode --with-gui=qt5
%endif
%endif

Name:    bitcoin
Version: 0.17.0
Release: 1%{?dist}
Summary: Peer to Peer Cryptographic Currency
Group:   Applications/System
License: MIT
URL:     https://bitcoincore.org/
Source0: https://github.com/bitcoin/%{name}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1: https://raw.githubusercontent.com/bitcoin-core/packaging/3b394e8044cf67cd76aa47b84487aa2f3f3eed81/debian/bitcoin-qt.desktop
Source2: https://raw.githubusercontent.com/bitcoin-core/packaging/3b394e8044cf67cd76aa47b84487aa2f3f3eed81/debian/examples/bitcoin.conf

BuildRequires: gcc-c++
BuildRequires: libtool
BuildRequires: make
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: openssl-devel
BuildRequires: libevent-devel
BuildRequires: boost-devel
BuildRequires: miniupnpc-devel
BuildRequires: python34

%description
Bitcoin is a digital cryptographic currency that uses peer-to-peer technology to
operate with no central authority or banks; managing transactions and the
issuing of bitcoins is carried out collectively by the network.

%if %{_buildqt}
%package qt
Summary:        Peer to Peer Cryptographic Currency
Group:          Applications/System
Obsoletes:      %{name} < %{version}-%{release}
Provides:       %{name} = %{version}-%{release}
BuildRequires: libdb4-devel
BuildRequires: libdb4-cxx-devel
BuildRequires: qt5-qttools-devel
BuildRequires: qt5-qtbase-devel
BuildRequires: protobuf-devel
BuildRequires: qrencode-devel
BuildRequires: desktop-file-utils

%description qt
Bitcoin is a digital cryptographic currency that uses peer-to-peer technology to
operate with no central authority or banks; managing transactions and the
issuing of bitcoins is carried out collectively by the network.

This package contains the Qt based graphical client and node. If you are looking
to run a Bitcoin wallet, this is probably the package you want.

%endif

%package libs
Summary:        Bitcoin shared libraries
Group:          System Environment/Libraries

%description libs
This package provides the bitcoinconsensus shared libraries. These libraries
may be used by third party software to provide consensus verification
functionality.

Unless you know need this package, you probably do not.

%package devel
Summary:        Development files for bitcoin
Group:          Development/Libraries
Requires:       %{name}-libs = %{version}-%{release}

%description devel
This package contains the header files and static library for the
bitcoinconsensus shared library. If you are developing or compiling software
that wants to link against that library, then you need this package installed.

Most people do not need this package installed.

%package -n bitcoin-cli
Summary:        CLI utils for bitcoin
Group:          Applications/System
Requires:       bash-completion

%description -n bitcoin-cli
This package installs command line programs like bitcoin-cli and bitcoin-tx that
can be used to interact with the bitcoin daemon.

%package -n bitcoind
Summary:        The bitcoin daemon
Group:          System Environment/Daemons
BuildRequires:  systemd
Requires:       bitcoin-cli = %{version}-%{release}
Requires:       bash-completion

%description -n bitcoind
This package provides a stand-alone bitcoin daemon. For most users, this package
is only needed if they need a full-node without the graphical client.

Some third party wallet software will want this package to provide the actual
bitcoin node they use to connect to the network.

If you use the graphical bitcoin client then you almost certainly do not
need this package.

%prep
%autosetup -n %{name}-%{version}

%build
./autogen.sh
%configure --disable-bench %{?walletargs} %{?guiargs}
%make_build

%check
make check

%install
make install DESTDIR=%{buildroot}

# no need to generate debuginfo data for the test executables
rm -f %{buildroot}%{_bindir}/test_bitcoin*

%if %{_buildqt}
# qt icons
install -D -p share/pixmaps/bitcoin.ico %{buildroot}%{_datadir}/pixmaps/bitcoin.ico

mkdir -p %{buildroot}%{_datadir}/bitcoin
install -p share/rpcauth/rpcauth.py %{buildroot}/%{_datadir}/bitcoin/rpcauth.py

mkdir -p %{buildroot}%{_sharedstatedir}/bitcoin

mkdir -p %{buildroot}%{_sysconfdir}
install -p %{SOURCE2} %{buildroot}%{_sysconfdir}/bitcoin.conf

mkdir -p %{buildroot}%{_unitdir}
install -p contrib/init/bitcoind.service %{buildroot}%{_unitdir}/bitcoind.service
sed -i -e 's|-conf=/etc/bitcoin/bitcoin\.conf|-conf=/etc/bitcoin.conf -datadir=/var/lib/bitcoin|g' %{buildroot}%{_unitdir}/bitcoind.service

mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install %{SOURCE1} %{buildroot}%{_datadir}/applications/bitcoin-qt.desktop
%endif

mkdir -p %{buildroot}%{_sysconfdir}/bash_completion.d
install -p contrib/*.bash-completion %{buildroot}%{_sysconfdir}/bash_completion.d/

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%pre -n bitcoind
getent group bitcoin >/dev/null || groupadd -r bitcoin
getent passwd bitcoin >/dev/null ||\
  useradd -r -g bitcoin -d %{_sharedstatedir}/bitcoin -s /sbin/nologin \
  -c "Bitcoin wallet server" bitcoin

%post -n bitcoind
%systemd_post bitcoind.service

%posttrans -n bitcoind
%{_bindir}/systemd-tmpfiles --create

%preun -n bitcoind
%systemd_preun bitcoind.service

%postun -n bitcoind
%systemd_postun_with_restart bitcoind.service

%clean
rm -rf %{buildroot}

%if %{_buildqt}
%files qt
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/bips.md doc/files.md doc/reduce-traffic.md doc/release-notes.md doc/tor.md
%attr(0755,root,root) %{_bindir}/bitcoin-qt
%attr(0644,root,root) %{_datadir}/applications/bitcoin-qt.desktop
%attr(0644,root,root) %{_datadir}/pixmaps/*.ico
%attr(0644,root,root) %{_mandir}/man1/bitcoin-qt.1*
%endif

%files libs
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/shared-libraries.md
%{_libdir}/lib*.so.*

%files devel
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/developer-notes.md doc/shared-libraries.md
%attr(0644,root,root) %{_includedir}/*.h
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/*.la
%attr(0644,root,root) %{_libdir}/pkgconfig/*.pc

%files -n bitcoin-cli
%defattr(-,root,root,-)
%license COPYING
%attr(0644,root,root) %{_mandir}/man1/bitcoin-cli.1*
%attr(0644,root,root) %{_mandir}/man1/bitcoin-tx.1*
%attr(0755,root,root) %{_bindir}/bitcoin-cli
%attr(0755,root,root) %{_bindir}/bitcoin-tx
%attr(0644,root,root) %{_sysconfdir}/bash_completion.d/bitcoin-cli.bash-completion
%attr(0644,root,root) %{_sysconfdir}/bash_completion.d/bitcoin-tx.bash-completion

%files -n bitcoind
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/REST-interface.md doc/bips.md doc/dnsseed-policy.md doc/files.md doc/reduce-traffic.md doc/release-notes.md doc/tor.md
%attr(0644,root,root) %{_mandir}/man1/bitcoind.1*
%attr(0644,root,root) %{_unitdir}/bitcoind.service
%attr(0644,root,root) %{_sysconfdir}/bitcoin.conf
%attr(0700,bitcoin,bitcoin) %{_sharedstatedir}/bitcoin
%attr(0755,root,root) %{_bindir}/bitcoind
%attr(0644,root,root) %{_datadir}/bitcoin/rpcauth.py
%config(noreplace) %{_sysconfdir}/bitcoin.conf
%exclude %{_datadir}/bitcoin/*.pyc
%exclude %{_datadir}/bitcoin/*.pyo
%attr(0644,root,root) %{_sysconfdir}/bash_completion.d/bitcoind.bash-completion

%changelog
* Wed Oct 03 2018 Billy Chan <billy@mona.co> - 0.17.0-1
- bump release

* Sat Sep 22 2018 Billy Chan <billy@mona.co> - 0.16.3-1
- bump release

* Tue Sep 04 2018 Billy Chan <billy@mona.co> - 0.16.2-1
- bump release

* Mon Feb 26 2018 Evan Klitzke <evan@eklitzke.org> - 0.16.0-3
- split out bitcoin-cli package

* Fri Feb 23 2018 Evan Klitzke <evan@eklitzke.org> - 0.16.0-2
- Add BuildRequires: systemd for F28/Rawhide

* Fri Feb 23 2018 Evan Klitzke <evan@eklitzke.org> - 0.16.0-1
- Bump for official 0.16.0 release

* Fri Feb 16 2018 Evan Klitzke <evan@eklitzke.org> - 0.16.0rc4-1
- rebuild for rc4

* Sat Feb 10 2018 Evan Klitzke <evan@eklitzke.org> - 0.16.0rc3-2
- Fix for GitHub tarballs (not created with "make dist")

* Sat Feb 10 2018 Evan Klitzke <evan@eklitzke.org> - 0.16.0rc3-1
- rebuilt for rc3

* Mon Feb 05 2018 Evan Klitzke <evan@eklitzke.org> - 0.16.0rc2-2
- rebuilt

* Wed Jan 31 2018 Evan Klitzke <evan@eklitzke.org> - 0.16.0rc1-1
- rebuilt for 0.16

* Wed Dec 13 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-13
- Configure systemd to use bitcoin-cli stop to shutdown bitcoind

* Wed Nov 29 2017 Evan Klitzke <evan@eklitzke.org>
- Add .desktop file for bitcoin-qt testnet

* Mon Nov 20 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-11
- Mark /etc/bitcoin.conf as a (noreplace) config file

* Sun Nov 19 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-10
- Just use /etc/bitcoin.conf, a whole new dir seems unnecessary

* Sun Nov 19 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-9
- Remove bitcoin-cli package (move those to bitcoind)
- Set up a real system service for bitcoind

* Wed Nov 15 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-8
- Remove bench_bitcoin from the bitcoin-cli package.

* Wed Nov 15 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-7
- bitcoin-daemon -> bitcoind, bitcoin-utils -> bitcoin-cli

* Wed Nov 15 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-6
- Fix the desktop file.

* Wed Nov 15 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-5
- Don't depend on SELinux stuff, rename the .desktop file

* Wed Nov 15 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-4
- Split into subpackages.

* Wed Nov 15 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-3
- Fix test_bitcoin logic, allow building without wallet.

* Wed Nov 15 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-2
- Remove test_bitcoin executable from bindir.

* Tue Nov 14 2017 Evan Klitzke <evan@eklitzke.org> - 0.15.1-1
- Initial build.
