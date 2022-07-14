#
# Conditional build:
%bcond_without	apidocs		# build without apidocs
%bcond_without	consolekit	# ConsoleKit fallback
%bcond_with	mozjs		# build with mozjs as JS backend instead of duktape
%bcond_without	systemd		# use systemd-login for session tracking (fallback to ConsoleKit on runtime)
%bcond_with	elogind		# use elogind instead of systemd-login

%if %{with elogind}
%undefine	with_systemd
%endif
Summary:	A framework for defining policy for system-wide components
Summary(pl.UTF-8):	Szkielet do definiowania polityki dla komponentów systemowych
Name:		polkit
Version:	121
Release:	1
License:	LGPL v2+
Group:		Libraries
Source0:	https://www.freedesktop.org/software/polkit/releases/%{name}-%{version}.tar.gz
# Source0-md5:	255761abdc616805a6592bb5fffae178
Patch0:		systemd-fallback.patch
URL:		https://www.freedesktop.org/wiki/Software/polkit
BuildRequires:	dbus-devel
BuildRequires:	docbook-dtd412-xml
BuildRequires:	docbook-style-xsl
%{!?with_mozjs:BuildRequires:	duktape-devel >= 2.2.0}
%{?with_elogind:BuildRequires:	elogind-devel}
BuildRequires:	expat-devel >= 1:1.95.8
BuildRequires:	gettext-tools
BuildRequires:	glib2-devel >= 1:2.32.0
%if %(locale -a | grep -q '^C\.utf8$'; echo $?)
BuildRequires:	glibc-localedb-all
%endif
BuildRequires:	gobject-introspection-devel >= 0.6.2
BuildRequires:	gtk-doc >= 1.3
BuildRequires:	gtk-doc-automake >= 1.3
BuildRequires:	libstdc++-devel >= 6:7
BuildRequires:	libxslt-progs
BuildRequires:	meson >= 0.50.0
%{?with_mozjs:BuildRequires:	mozjs91-devel}
BuildRequires:	ninja
BuildRequires:	pam-devel >= 0.80
BuildRequires:	pkgconfig
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 1.736
%{?with_systemd:BuildRequires:	systemd-devel}
Requires:	%{name}-libs = %{version}-%{release}
%if %{without systemd} && %{without elogind}
Requires:	ConsoleKit >= 0.4.1
%endif
Requires:	dbus >= 1.1.2-5
%{!?with_mozjs:Requires:	duktape >= 2.2.0}
%if %{with systemd}
Requires:	systemd-units >= 38
%endif
Obsoletes:	PolicyKit < 1
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
PolicyKit is a framework for defining policy for system-wide
components and for desktop pieces to configure it.

%description -l pl.UTF-8
PolicyKit to szkielet do definiowania polityki dla komponentów
systemowych oraz składników pulpitu do konfigurowania ich.

%package apidocs
Summary:	PolicyKit API documentation
Summary(pl.UTF-8):	Dokumentacja API PolicyKit
Group:		Documentation
Requires:	gtk-doc-common
Obsoletes:	PolicyKit-apidocs < 1
BuildArch:	noarch

%description apidocs
PolicyKit API documentation.

%description apidocs -l pl.UTF-8
Dokumentacja API PolicyKit.

%package libs
Summary:	PolicyKit libraries
Summary(pl.UTF-8):	Biblioteki PolicyKit
Group:		Libraries
Requires:	dbus-libs >= 1.1.2-5
Requires:	glib2 >= 1:2.32.0
Requires:	gobject-introspection
Obsoletes:	PolicyKit-libs < 1

%description libs
PolicyKit libraries.

%description libs -l pl.UTF-8
Biblioteki PolicyKit.

%package devel
Summary:	Header files for PolicyKit
Summary(pl.UTF-8):	Pliki nagłówkowe PolicyKit
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
Requires:	expat-devel >= 1:1.95.8
Requires:	glib2-devel >= 1:2.32.0
Obsoletes:	PolicyKit-devel < 1
Obsoletes:	polkit-static < 121

%description devel
Header files for PolicyKit.

%description devel -l pl.UTF-8
Pliki nagłówkowe PolicyKit.

%prep
%setup -q -n %{name}-v.%{version}
%if %{with consolekit} && (%{with systemd} || %{with elogind})
%patch0 -p1
%endif

%build
%meson build \
	-Dgtk_doc=%{__true_false apidocs} \
	-Dtests=false \
	-Dsession_tracking=%{?with_systemd:libsystemd-login}%{?with_elogind:libelogind} \
	-Dpam_include=system-auth \
	-Dpam_module_dir=/%{_lib}/security \
	-Dpolkitd_user=polkitd \
	-Dexamples=true \
	-Djs_engine=%{!?with_mozjs:duktape}%{?with_mozjs:mozjs} \
	-Dman=true

%ninja_build -C build

%install
rm -rf $RPM_BUILD_ROOT

%ninja_install -C build

%find_lang polkit-1

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 283 polkitd
%useradd -u 283 -s /bin/false -c "polkitd pseudo user" -g polkitd polkitd
%addusertogroup polkitd proc

%postun
if [ "$1" = "0" ]; then
	%userremove polkitd
	%groupremove polkitd
fi

%{?with_systemd:%systemd_reload}

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files -f polkit-1.lang
%defattr(644,root,root,755)
%doc AUTHORS NEWS.md README.md
%attr(755,root,root) %{_bindir}/pkaction
%attr(755,root,root) %{_bindir}/pkcheck
%attr(4755,root,root) %{_bindir}/pkexec
%attr(755,root,root) %{_bindir}/pkttyagent
%attr(755,root,root) %{_bindir}/pk-example-frobnicate
%dir %{_prefix}/lib/polkit-1
%attr(4755,root,root) %{_prefix}/lib/polkit-1/polkit-agent-helper-1
%attr(755,root,root) %{_prefix}/lib/polkit-1/polkitd
%dir %{_sysconfdir}/polkit-1
%attr(700,polkitd,root) %dir %{_sysconfdir}/polkit-1/rules.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/polkit-1/rules.d/50-default.rules
/etc/pam.d/polkit-1
%dir %{_datadir}/polkit-1
%{_datadir}/polkit-1/policyconfig-1.dtd
%{_datadir}/polkit-1/actions
%attr(700,polkitd,root) %dir %{_datadir}/polkit-1/rules.d
%{_datadir}/dbus-1/system-services/org.freedesktop.PolicyKit1.service
%{_datadir}/dbus-1/system.d/org.freedesktop.PolicyKit1.conf
%{?with_systemd:%{systemdunitdir}/polkit.service}
%{_mandir}/man1/pkaction.1*
%{_mandir}/man1/pkcheck.1*
%{_mandir}/man1/pkexec.1*
%{_mandir}/man1/pkttyagent.1*
%{_mandir}/man8/polkit.8*
%{_mandir}/man8/polkitd.8*

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%{_gtkdocdir}/polkit-1
%endif

%files libs
%defattr(644,root,root,755)
# notes which license applies to which package part, AFL text (and GPL text copy)
%doc COPYING
%attr(755,root,root) %{_libdir}/libpolkit-agent-1.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libpolkit-agent-1.so.0
%attr(755,root,root) %{_libdir}/libpolkit-gobject-1.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libpolkit-gobject-1.so.0
%{_libdir}/girepository-1.0/Polkit-1.0.typelib
%{_libdir}/girepository-1.0/PolkitAgent-1.0.typelib

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libpolkit-agent-1.so
%attr(755,root,root) %{_libdir}/libpolkit-gobject-1.so
%{_includedir}/polkit-1
%{_pkgconfigdir}/polkit-agent-1.pc
%{_pkgconfigdir}/polkit-gobject-1.pc
%{_datadir}/gir-1.0/Polkit-1.0.gir
%{_datadir}/gir-1.0/PolkitAgent-1.0.gir
%{_datadir}/gettext/its/polkit.its
%{_datadir}/gettext/its/polkit.loc
