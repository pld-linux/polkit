#
# Conditional build:
%bcond_without	apidocs		# build without apidocs
%bcond_without	consolekit	# ConsoleKit fallback
%bcond_without	systemd		# use systemd-login for session tracking (fallback to ConsoleKit on runtime)
%bcond_without	tests		# test suite
%bcond_with	elogind		# use elogind instead of systemd-login

%if %{with elogind}
%undefine	with_systemd
%endif
Summary:	A framework for defining policy for system-wide components
Summary(pl.UTF-8):	Szkielet do definiowania polityki dla komponentów systemowych
Name:		polkit
Version:	127
Release:	2
License:	LGPL v2+
Group:		Libraries
Source0:	https://github.com/polkit-org/polkit/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	2cc95f1b02fc1de6c9e52db986642ec4
Patch0:		systemd-fallback.patch
Patch1:		CVE-2026-4897.patch
Patch2:		CVE-2026-85498.patch
Patch3:		polkit-agent-session-use-after-free.patch
URL:		https://github.com/polkit-org/polkit
BuildRequires:	dbus-devel
BuildRequires:	docbook-dtd412-xml
BuildRequires:	docbook-style-xsl
BuildRequires:	duktape-devel >= 2.2.0
%{?with_elogind:BuildRequires:	elogind-devel}
BuildRequires:	expat-devel >= 1:1.95.8
BuildRequires:	gettext-tools
BuildRequires:	glib2-devel >= 1:2.44.0
%if %(locale -a | grep -q '^C\.utf8$'; echo $?)
BuildRequires:	glibc-localedb-all
%endif
BuildRequires:	gobject-introspection-devel >= 0.6.2
%{?with_apidocs:BuildRequires:	gtk-doc >= 1.3}
BuildRequires:	libxslt-progs
BuildRequires:	meson >= 1.4.0
BuildRequires:	ninja
BuildRequires:	pam-devel >= 0.80
BuildRequires:	pkgconfig
%if %{with tests}
BuildRequires:	/bin/mount
BuildRequires:	python3-dbus
BuildRequires:	python3-dbusmock
%endif
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 2.042
%{?with_systemd:BuildRequires:	systemd-devel}
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/lib/rpm/user_group.sh
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(pre):	/usr/sbin/usermod
Requires:	%{name}-libs = %{version}-%{release}
%if %{without systemd} && %{without elogind}
Requires:	ConsoleKit >= 0.4.1
%endif
Requires:	dbus >= 1.1.2-5
Requires:	duktape >= 2.2.0
%if %{with systemd}
Requires:	systemd-units >= 38
%else
Provides:	user(polkitd)
Provides:	group(polkitd)
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
Requires:	glib2 >= 1:2.44.0
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
Requires:	glib2-devel >= 1:2.44.0
Obsoletes:	PolicyKit-devel < 1
Obsoletes:	polkit-static < 121

%description devel
Header files for PolicyKit.

%description devel -l pl.UTF-8
Pliki nagłówkowe PolicyKit.

%prep
%setup -q
%if %{with consolekit} && (%{with systemd} || %{with elogind})
%patch -P0 -p1
%endif
%patch -P1 -p1
%patch -P2 -p1
%patch -P3 -p1

%build
%meson \
	-Dgtk_doc=%{__true_false apidocs} \
	-Dtests=%{__true_false tests} \
	-Dsession_tracking=%{?with_systemd:logind}%{?with_elogind:elogind} \
	-Dpam_include=system-auth \
	-Dpam_module_dir=/%{_lib}/security \
	-Dpolkitd_user=polkitd \
	-Dpolkitd_uid=283 \
	-Dexamples=true \
	-Dman=true \
	-Dgettext=true

%meson_build

%if %{with tests}
%meson_test
%endif

%install
rm -rf $RPM_BUILD_ROOT

%meson_install

%find_lang polkit-1

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 283 polkitd
%useradd -u 283 -s /bin/false -c "polkitd pseudo user" -g polkitd polkitd
%addusertogroup polkitd proc

%preun
# The socket-activated helper needs SO_PEERPIDFD (kernel >= 6.5) and PolkitAgentSession
# falls back to the setuid helper only when the connect fails, so on older kernels an
# enabled socket breaks authentication outright; the socket is therefore never enabled
# on install, only deregistered here. https://github.com/polkit-org/polkit/issues/639
%{?with_systemd:%systemd_preun polkit-agent-helper.socket}

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
%{_prefix}/lib/pam.d/polkit-1
%dir %{_datadir}/polkit-1
%{_datadir}/polkit-1/policyconfig-1.dtd
%{_datadir}/polkit-1/polkitd.conf
%{_datadir}/polkit-1/actions
%attr(700,polkitd,root) %dir %{_datadir}/polkit-1/rules.d
%{_datadir}/polkit-1/rules.d/50-default.rules
%{_datadir}/dbus-1/system-services/org.freedesktop.PolicyKit1.service
%{_datadir}/dbus-1/system.d/org.freedesktop.PolicyKit1.conf
%if %{with systemd}
%{_prefix}/lib/sysusers.d/polkit.conf
%{systemdunitdir}/polkit-agent-helper.socket
%{systemdunitdir}/polkit-agent-helper@.service
%{systemdunitdir}/polkit.service
%{systemdtmpfilesdir}/polkit-tmpfiles.conf
%endif
%{_mandir}/man1/pkaction.1*
%{_mandir}/man1/pkcheck.1*
%{_mandir}/man1/pkexec.1*
%{_mandir}/man1/pkttyagent.1*
%{_mandir}/man5/polkitd.conf.5*
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
