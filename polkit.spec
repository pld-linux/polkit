#
# Conditional build:
%bcond_without	apidocs		# build without apidocs
%bcond_without	systemd		# use systemd for session tracking instead of ConsoleKit (fallback to ConsoleKit on runtime)

Summary:	A framework for defining policy for system-wide components
Summary(pl.UTF-8):	Szkielet do definiowania polityki dla komponentów systemowych
Name:		polkit
Version:	0.107
Release:	1
License:	LGPL v2+
Group:		Libraries
Source0:	http://www.freedesktop.org/software/polkit/releases/%{name}-%{version}.tar.gz
# Source0-md5:	0e4f9c53f43fd1b25ac3f0d2e09b2ae1
Patch0:		systemd-fallback.patch
URL:		http://www.freedesktop.org/wiki/Software/polkit
BuildRequires:	autoconf >= 2.60
BuildRequires:	automake >= 1:1.7
BuildRequires:	docbook-dtd412-xml
BuildRequires:	docbook-style-xsl
BuildRequires:	expat-devel >= 1:1.95.8
BuildRequires:	gettext-devel
BuildRequires:	glib2-devel >= 1:2.32.0
BuildRequires:	glibc-misc
BuildRequires:	gobject-introspection-devel >= 0.6.2
%{?with_apidocs:BuildRequires:	gtk-doc >= 1.3}
BuildRequires:	gtk-doc-automake >= 1.3
BuildRequires:	intltool >= 0.40.0
BuildRequires:	js185-devel
BuildRequires:	libtool
BuildRequires:	libxslt-progs
BuildRequires:	pam-devel >= 0.80
BuildRequires:	pkgconfig
BuildRequires:	python-modules
BuildRequires:	rpmbuild(macros) >= 1.647
%{?with_systemd:BuildRequires:	systemd-devel}
Requires:	%{name}-libs = %{version}-%{release}
%if %{without systemd}
Requires:	ConsoleKit >= 0.4.1
%else
Requires:	systemd-units >= 38
Suggests:	ConsoleKit >= 0.4.1
%endif
Requires:	dbus >= 1.1.2-5
Obsoletes:	PolicyKit
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
Obsoletes:	PolicyKit-apidocs

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
Obsoletes:	PolicyKit-libs

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
Obsoletes:	PolicyKit-devel

%description devel
Header files for PolicyKit.

%description devel -l pl.UTF-8
Pliki nagłówkowe PolicyKit.

%package static
Summary:	Static PolicyKit libraries
Summary(pl.UTF-8):	Statyczne biblioteki PolicyKit
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}
Obsoletes:	PolicyKit-static

%description static
Static PolicyKit libraries.

%description static -l pl.UTF-8
Statyczne biblioteki PolicyKit.

%prep
%setup -q
%{?with_systemd:%patch0 -p1}

%build
%{?with_apidocs:%{__gtkdocize}}
%{__intltoolize}
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	%{__enable_disable apidocs gtk-doc} \
	--disable-silent-rules \
	%{__enable_disable systemd systemd} \
	--with-html-dir=%{_gtkdocdir} \
	--with-pam-include=system-auth \
	--with-pam-module-dir=/%{_lib}/security \
	--with-polkitd-user=polkitd
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%{__rm} $RPM_BUILD_ROOT%{_libdir}/*.la

%find_lang polkit-1

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 283 polkitd
%useradd -u 283 -s /bin/false -c "polkitd pseudo user" -g polkitd polkitd

%post
%{?with_systemd:%systemd_post polkit.service}

%preun
%{?with_systemd:%systemd_preun polkit.service}

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
%doc AUTHORS NEWS README
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
/etc/dbus-1/system.d/org.freedesktop.PolicyKit1.conf
/etc/pam.d/polkit-1
%dir %{_datadir}/polkit-1
%{_datadir}/polkit-1/actions
%attr(700,polkitd,root) %dir %{_datadir}/polkit-1/rules.d
%{_datadir}/dbus-1/system-services/org.freedesktop.PolicyKit1.service
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

%files static
%defattr(644,root,root,755)
%{_libdir}/libpolkit-agent-1.a
%{_libdir}/libpolkit-gobject-1.a
