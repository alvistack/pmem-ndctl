%global debug_package %{nil}

%global source_date_epoch_from_changelog 0

%if 0%{?suse_version}
%global DAX_DNAME libdaxctl-devel
%global CXL_DNAME libcxl-devel
%global DNAME libndctl-devel
%global DAX_LNAME libdaxctl
%global CXL_LNAME libcxl
%global LNAME libndctl
%endif
%if !(0%{?suse_version})
%global DAX_DNAME daxctl-devel
%global CXL_DNAME cxl-devel
%global DNAME ndctl-devel
%global DAX_LNAME daxctl-libs
%global CXL_LNAME cxl-libs
%global LNAME ndctl-libs
%endif

Name:		ndctl
Epoch:      100
Version:	79
Release:	1%{?dist}
Summary:	Manage "libnvdimm" subsystem devices (Non-volatile Memory)
License:	GPLv2
Url:		https://github.com/pmem/ndctl/tags
Source0:	%{name}_%{version}.orig.tar.gz
Source99:   %{name}.rpmlintrc

Requires:	%{LNAME}%{?_isa} = %{epoch}:%{version}-%{release}
Requires:	%{DAX_LNAME}%{?_isa} = %{epoch}:%{version}-%{release}
Requires:	%{CXL_LNAME}%{?_isa} = %{epoch}:%{version}-%{release}
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
BuildRequires:	pkgconfig(udev)
BuildRequires:	keyutils-libs-devel
BuildRequires:	systemd-rpm-macros
BuildRequires:	iniparser-devel
BuildRequires:	meson
BuildRequires:	cmake

%description
Utility library for managing the "libnvdimm" subsystem.  The "libnvdimm"
subsystem defines a kernel device model and control message interface for
platform NVDIMM resources like those defined by the ACPI 6+ NFIT (NVDIMM
Firmware Interface Table).

%if 0%{?flatpak}
%global _udevrulesdir %{_prefix}/lib/udev/rules.d
%endif

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

%package -n cxl-cli
Summary:	Manage CXL devices
License:	GPLv2
Requires:	%{CXL_LNAME}%{?_isa} = %{epoch}:%{version}-%{release}

%description -n cxl-cli
The cxl utility provides enumeration and provisioning commands for
the Linux kernel CXL devices.

%package -n %{CXL_DNAME}
Summary:	Development files for libcxl
License:	LGPLv2
Requires:	%{CXL_LNAME}%{?_isa} = %{epoch}:%{version}-%{release}

%description -n %{CXL_DNAME}
This package contains libraries and header files for developing applications
that use libcxl, a library for enumerating and communicating with CXL devices.

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

%package -n %{CXL_LNAME}
Summary:	Management library for CXL devices
License:	LGPLv2

%description -n %{CXL_LNAME}
libcxl is a library for enumerating and communicating with CXL devices.


%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%build
%meson \
    -Dasciidoctor=disabled \
    -Ddocs=disabled \
    -Dlibtracefs=disabled \
    -Dsystemd=disabled \
    -Dtest=disabled
%meson_build

%install
%meson_install

%check

%ldconfig_scriptlets -n %{LNAME}

%ldconfig_scriptlets -n %{DAX_LNAME}

%ldconfig_scriptlets -n %{CXL_LNAME}

%define bashcompdir %(pkg-config --variable=completionsdir bash-completion)

%pre
if [ -f %{_sysconfdir}/ndctl/monitor.conf ] ; then
  if ! [ -f %{_sysconfdir}/ndctl.conf.d/monitor.conf ] ; then
    cp -a %{_sysconfdir}/ndctl/monitor.conf /var/run/ndctl-monitor.conf-migration
  fi
fi

%post
if [ -f /var/run/ndctl-monitor.conf-migration ] ; then
  config_found=false
  while read line ; do
    [ -n "$line" ] || continue
    case "$line" in
      \#*) continue ;;
    esac
    config_found=true
    break
  done < /var/run/ndctl-monitor.conf-migration
  if $config_found ; then
    echo "[monitor]" > %{_sysconfdir}/ndctl.conf.d/monitor.conf
    cat /var/run/ndctl-monitor.conf-migration >> %{_sysconfdir}/ndctl.conf.d/monitor.conf
  fi
  rm /var/run/ndctl-monitor.conf-migration
fi

%files
%defattr(-,root,root)
%license LICENSES/preferred/GPL-2.0 LICENSES/other/MIT LICENSES/other/CC0-1.0
%{_bindir}/ndctl
%{bashcompdir}/ndctl

%dir %{_sysconfdir}/ndctl
%dir %{_sysconfdir}/ndctl/keys
%{_sysconfdir}/ndctl/keys/keys.readme

%{_sysconfdir}/modprobe.d/nvdimm-security.conf

%dir %{_sysconfdir}/ndctl.conf.d
%config(noreplace) %{_sysconfdir}/ndctl.conf.d/monitor.conf
%config(noreplace) %{_sysconfdir}/ndctl.conf.d/ndctl.conf

%files -n daxctl
%defattr(-,root,root)
%license LICENSES/preferred/GPL-2.0 LICENSES/other/MIT LICENSES/other/CC0-1.0
%{_bindir}/daxctl
%{_datadir}/daxctl
%{bashcompdir}/daxctl
%dir %{_sysconfdir}/daxctl.conf.d/
%config(noreplace) %{_sysconfdir}/daxctl.conf.d/daxctl.example.conf

%files -n cxl-cli
%defattr(-,root,root)
%license LICENSES/preferred/GPL-2.0 LICENSES/other/MIT LICENSES/other/CC0-1.0
%{_bindir}/cxl
%{bashcompdir}/cxl

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

%files -n %{CXL_LNAME}
%defattr(-,root,root)
%doc README.md
%license LICENSES/preferred/LGPL-2.1 LICENSES/other/MIT LICENSES/other/CC0-1.0
%{_libdir}/libcxl.so.*

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

%files -n %{CXL_DNAME}
%defattr(-,root,root)
%license LICENSES/preferred/LGPL-2.1
%{_includedir}/cxl/
%{_libdir}/libcxl.so
%{_libdir}/pkgconfig/libcxl.pc


%changelog
