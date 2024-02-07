%global debug_package %{nil}

%global source_date_epoch_from_changelog 0

%if 0%{?suse_version}
%global DAX_DNAME libdaxctl-devel
%global DNAME libndctl-devel
%global DAX_LNAME libdaxctl
%global LNAME libndctl
%endif
%if !(0%{?suse_version})
%global DAX_DNAME daxctl-devel
%global DNAME ndctl-devel
%global DAX_LNAME daxctl-libs
%global LNAME ndctl-libs
%endif

Name:       ndctl
Epoch:      100
Version:	71.1
Release:	1%{?dist}
Summary:	Manage "libnvdimm" subsystem devices (Non-volatile Memory)
License:	GPLv2
Url:		https://github.com/pmem/ndctl/tags
Source0:	%{name}_%{version}.orig.tar.gz
Source1:    %{name}.rpmlintrc

Requires:	%{LNAME}%{?_isa} = %{epoch}:%{version}-%{release}
Requires:	%{DAX_LNAME}%{?_isa} = %{epoch}:%{version}-%{release}
BuildRequires:	autoconf
BuildRequires:	xmlto
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	pkgconfig
BuildRequires:	pkgconfig(libkmod)
BuildRequires:	pkgconfig(libudev)
BuildRequires:	pkgconfig(uuid)
BuildRequires:	pkgconfig(json-c)
BuildRequires:	pkgconfig(bash-completion)
BuildRequires:	pkgconfig(systemd)
BuildRequires:  pkgconfig(udev)
BuildRequires:	keyutils-libs-devel

%description
Utility library for managing the "libnvdimm" subsystem.  The "libnvdimm"
subsystem defines a kernel device model and control message interface for
platform NVDIMM resources like those defined by the ACPI 6+ NFIT (NVDIMM
Firmware Interface Table).


%package -n %{DNAME}
Summary:	Development files for libndctl
License:	LGPLv2
Requires:	%{LNAME}%{?_isa} = %{epoch}:%{version}-%{release}

%description -n %{DNAME}
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package -n daxctl
Summary:	Manage Device-DAX instances
License:	GPLv2
Requires:	%{DAX_LNAME}%{?_isa} = %{epoch}:%{version}-%{release}

%description -n daxctl
The daxctl utility provides enumeration and provisioning commands for
the Linux kernel Device-DAX facility. This facility enables DAX mappings
of performance / feature differentiated memory without need of a
filesystem.

%package -n %{DAX_DNAME}
Summary:	Development files for libdaxctl
License:	LGPLv2
Requires:	%{DAX_LNAME}%{?_isa} = %{epoch}:%{version}-%{release}

%description -n %{DAX_DNAME}
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}, a library for enumerating
"Device DAX" devices.  Device DAX is a facility for establishing DAX
mappings of performance / feature-differentiated memory.


%package -n %{LNAME}
Summary:	Management library for "libnvdimm" subsystem devices (Non-volatile Memory)
License:	LGPLv2
Requires:	%{DAX_LNAME}%{?_isa} = %{epoch}:%{version}-%{release}


%description -n %{LNAME}
Libraries for %{name}.

%package -n %{DAX_LNAME}
Summary:	Management library for "Device DAX" devices
License:	LGPLv2

%description -n %{DAX_LNAME}
Device DAX is a facility for establishing DAX mappings of performance /
feature-differentiated memory. %{DAX_LNAME} provides an enumeration /
control API for these devices.


%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%build
echo %{version} > version
./autogen.sh
%configure \
    --disable-asciidoctor \
    --disable-docs \
    --disable-silent-rules \
    --disable-static \
    --disable-test \
    --without-systemd
make %{?_smp_mflags}

%install
%make_install
find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'

%check

%ldconfig_scriptlets -n %{LNAME}

%ldconfig_scriptlets -n %{DAX_LNAME}

%define bashcompdir %(pkg-config --variable=completionsdir bash-completion)

%files
%dir %{_sysconfdir}/ndctl
%dir %{_sysconfdir}/ndctl/keys
%defattr(-,root,root)
%license LICENSES/preferred/GPL-2.0 LICENSES/other/MIT LICENSES/other/CC0-1.0
%{_bindir}/ndctl
%{bashcompdir}/
%{_sysconfdir}/ndctl/keys/keys.readme
%{_sysconfdir}/modprobe.d/nvdimm-security.conf

%config(noreplace) %{_sysconfdir}/ndctl/monitor.conf

%files -n daxctl
%dir %{_datadir}/daxctl
%defattr(-,root,root)
%license LICENSES/preferred/GPL-2.0 LICENSES/other/MIT LICENSES/other/CC0-1.0
%{_bindir}/daxctl
%{_datadir}/daxctl/daxctl.conf

%files -n %{LNAME}
%defattr(-,root,root)
%doc README.md
%license LICENSES/preferred/LGPL-2.1 LICENSES/other/MIT LICENSES/other/CC0-1.0
%{_libdir}/libndctl.so.*

%files -n %{DAX_LNAME}
%defattr(-,root,root)
%doc README.md
%license LICENSES/preferred/LGPL-2.1 LICENSES/other/MIT LICENSES/other/CC0-1.0
%{_libdir}/libdaxctl.so.*

%files -n %{DNAME}
%defattr(-,root,root)
%license LICENSES/preferred/LGPL-2.1
%{_includedir}/ndctl/
%{_libdir}/libndctl.so
%{_libdir}/pkgconfig/libndctl.pc

%files -n %{DAX_DNAME}
%defattr(-,root,root)
%license LICENSES/preferred/LGPL-2.1
%{_includedir}/daxctl/
%{_libdir}/libdaxctl.so
%{_libdir}/pkgconfig/libdaxctl.pc


%changelog
