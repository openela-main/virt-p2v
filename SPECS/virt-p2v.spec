# Verify tarball signature with GPGv2.
%global verify_tarball_signature 1

# So far there are no ELF binaries in this package, so the list
# of files in the debuginfo package will be empty, triggering
# an RPM failure.
%global debug_package %{nil}

Summary:       Convert a physical machine to run on KVM
Name:          virt-p2v
Epoch:         1
Version:       1.42.0
Release:       5%{?dist}
License:       GPLv2+

# virt-p2v works only on x86_64 at the moment.  It requires porting
# to properly detect the hardware on other architectures, and furthermore
# virt-v2v requires porting too.
ExclusiveArch: x86_64

# Source and patches.
URL:           http://libguestfs.org/
Source0:       http://download.libguestfs.org/%{name}/%{name}-%{version}.tar.gz
%if 0%{verify_tarball_signature}
Source1:       http://download.libguestfs.org/%{name}/%{name}-%{version}.tar.gz.sig
%endif

# Keyring used to verify tarball signature.
%if 0%{verify_tarball_signature}
Source2:       libguestfs.keyring
%endif

# Basic build requirements.
BuildRequires: gcc
BuildRequires: perl(Pod::Simple)
BuildRequires: perl(Pod::Man)
BuildRequires: perl(List::MoreUtils)
BuildRequires: /usr/bin/pod2text
BuildRequires: libxml2-devel
BuildRequires: pcre-devel
BuildRequires: bash-completion
BuildRequires: xz
BuildRequires: gtk3-devel
BuildRequires: dbus-devel
BuildRequires: m4
%if 0%{verify_tarball_signature}
BuildRequires: gnupg2
%endif

# Test suite requirements.
BuildRequires: /usr/bin/qemu-nbd

%description
Virt-p2v converts (virtualizes) physical machines so they can be run
as virtual machines under KVM.

This package contains the tools needed to make a virt-p2v boot CD or
USB key which is booted on the physical machine to perform the
conversion.  You also need virt-v2v installed somewhere else to
complete the conversion.

To convert virtual machines from other hypervisors, see virt-v2v.


%package maker
Summary:       Convert a physical machine to run on KVM

# https://fedoraproject.org/wiki/Packaging:No_Bundled_Libraries#Packages_granted_exceptions
Provides:      bundled(gnulib)


Requires:      gawk
Requires:      gzip
Requires:      xz

# virt-p2v-make-disk runs virt-builder:
Requires:      libguestfs-tools-c

# virt-p2v-make-kickstart runs strip:
Requires:      binutils


# The bash completion for p2v were shipped with the others of libguestfs:
Obsoletes: libguestfs-bash-completion < 1:1.38.4-15


%description maker
Virt-p2v converts (virtualizes) physical machines so they can be run
as virtual machines under KVM.

This package contains the tools needed to make a virt-p2v boot CD or
USB key which is booted on the physical machine to perform the
conversion.  You also need virt-v2v installed somewhere else to
complete the conversion.

To convert virtual machines from other hypervisors, see virt-v2v.


%prep
%if 0%{verify_tarball_signature}
tmphome="$(mktemp -d)"
gpgv2 --homedir "$tmphome" --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%endif
%setup -q
%autopatch -p1


%build
%configure \
  --with-extra="rhel=%{rhel},release=%{release}" \
  --disable-gnulib-tests

make V=1 %{?_smp_mflags}


%check

if ! make check; then
    cat test-suite.log
    exit 1
fi


%install
make DESTDIR=$RPM_BUILD_ROOT install

# Delete the development man pages.
rm $RPM_BUILD_ROOT%{_mandir}/man1/p2v-building.1*
rm $RPM_BUILD_ROOT%{_mandir}/man1/p2v-hacking.1*
rm $RPM_BUILD_ROOT%{_mandir}/man1/p2v-release-notes.1*

# Delete kiwi tools.
rm $RPM_BUILD_ROOT%{_bindir}/virt-p2v-make-kiwi
rm $RPM_BUILD_ROOT%{_mandir}/man1/virt-p2v-make-kiwi.1*
rm $RPM_BUILD_ROOT%{_datadir}/bash-completion/completions/virt-p2v-make-kiwi

%files maker
%doc README
%license COPYING
%{_bindir}/virt-p2v-make-disk
%{_bindir}/virt-p2v-make-kickstart
%{_datadir}/bash-completion/completions/virt-*
%{_datadir}/virt-p2v
%{_libdir}/virt-p2v
%{_mandir}/man1/virt-p2v-make-disk.1*
%{_mandir}/man1/virt-p2v-make-kickstart.1*
%{_mandir}/man1/virt-p2v.1*


%changelog
* Fri Mar 06 2020 Pino Toscano <ptoscano@redhat.com> - 1:1.42.0-5
- Remove virt-p2v-make-kiwi, as it is not supported, and was not
  shipped already.

* Fri Feb 21 2020 Pino Toscano <ptoscano@redhat.com> - 1:1.42.0-4
- Copy %description also for the source, so tools are less confused
  about it.
- Fix the "extra" addition to the version to refer to rhel.

* Wed Dec 11 2019 Pino Toscano <ptoscano@redhat.com> - 1:1.42.0-3
- Explicitly require xz, as it is used by all the tools to unpack the
  virt-p2v binary.

* Thu Dec 05 2019 Pino Toscano <ptoscano@redhat.com> - 1:1.42.0-2
- Adjust the version of libguestfs-bash-completion that drops the bash
  completion scripts

* Thu Nov 28 2019 Pino Toscano <ptoscano@redhat.com> - 1:1.42.0-1
- Initial build, split off src:libguestfs.
