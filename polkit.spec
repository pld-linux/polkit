
# Conditional build:
%bcond_without	apidocs			# build without apidocs

Summary:	A framework for defining policy for system-wide components
Summary(pl.UTF-8):	Szkielet do definiowania polityki dla komponentów systemowych
Name:		polkit
Version:	0.94
Release:	2
License:	LGPL v2+
Group:		Libraries
Source0:	http://hal.freedesktop.org/releases/%{name}-%{version}.tar.gz
# Source0-md5:	5abc9f858e7b614ef41161db36d53915
URL:		http://people.freedesktop.org/~david/polkit-spec.html
BuildRequires:	autoconf >= 2.60
BuildRequires:	automake >= 1:1.7
BuildRequires:	eggdbus-devel >= 0.5
BuildRequires:	expat-devel >= 1:1.95.8
BuildRequires:	gettext-devel
BuildRequires:	gir-repository-devel
BuildRequires:	glib2-devel >= 1:2.21.4
BuildRequires:	gobject-introspection-devel
%{?with_apidocs:BuildRequires:	gtk-doc >= 1.3}
BuildRequires:	intltool >= 0.40.0
BuildRequires:	libtool
BuildRequires:	pam-devel >= 0.80
BuildRequires:	pkgconfig
Requires:	%{name}-libs = %{version}-%{release}
Requires:	ConsoleKit >= 0.4.1
Requires:	dbus >= 1.1.2-5
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
PolicyKit is a framework for defining policy for system-wide
components and for desktop pieces to configure it. It is used by HAL.

%description -l pl.UTF-8
PolicyKit to szkielet do definiowania polityki dla komponentów
systemowych oraz składników pulpitu do konfigurowania ich. Jest
używany przez HAL-a.

%package apidocs
Summary:	PolicyKit API documentation
Summary(pl.UTF-8):	Dokumentacja API PolicyKit
Group:		Documentation
Requires:	gtk-doc-common

%description apidocs
PolicyKit API documentation.

%description apidocs -l pl.UTF-8
Dokumentacja API PolicyKit.

%package libs
Summary:	PolicyKit libraries
Summary(pl.UTF-8):	Biblioteki PolicyKit
Group:		Libraries
Requires:	dbus-libs >= 1.1.2-5
Requires:	glib2 >= 1:2.18.0
Conflicts:	PolicyKit < 0.1-0.20061203.6

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
Requires:	glib2-devel >= 1:2.18.0

%description devel
Header files for PolicyKit.

%description devel -l pl.UTF-8
Pliki nagłówkowe PolicyKit.

%package static
Summary:	Static PolicyKit libraries
Summary(pl.UTF-8):	Statyczne biblioteki PolicyKit
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static PolicyKit libraries.

%description static -l pl.UTF-8
Statyczne biblioteki PolicyKit.

%prep
%setup -q

%build
%{__intltoolize}
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--%{!?with_apidocs:dis}%{?with_apidocs:en}able-gtk-doc \
	--with-html-dir=%{_gtkdocdir} \
	--with-pam-include=system-auth \
	--with-pam-module-dir=/%{_lib}/security
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

rm -f $RPM_BUILD_ROOT%{_libdir}/polkit-1/extensions/*.{la,a}

%find_lang polkit-1

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files -f polkit-1.lang
%defattr(644,root,root,755)
%doc AUTHORS README
%attr(755,root,root) %{_bindir}/pkaction
%attr(755,root,root) %{_bindir}/pkcheck
%attr(4755,root,root) %{_bindir}/pkexec
%attr(4755,root,root) %{_libexecdir}/polkit-agent-helper-1
%attr(755,root,root) %{_libexecdir}/polkitd
%dir %{_libdir}/polkit-1
%dir %{_libdir}/polkit-1/extensions
%attr(755,root,root) %{_libdir}/polkit-1/extensions/libnullbackend.so
%attr(755,root,root) %{_libdir}/polkit-1/extensions/libpkexec-action-lookup.so
%dir %{_sysconfdir}/polkit-1
%dir %{_sysconfdir}/polkit-1/localauthority.conf.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/polkit-1/localauthority.conf.d/*.conf
%dir %{_sysconfdir}/polkit-1/nullbackend.conf.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/polkit-1/nullbackend.conf.d/*.conf
/etc/dbus-1/system.d/org.freedesktop.PolicyKit1.conf
/etc/pam.d/polkit-1
%{_datadir}/polkit-1
%{_datadir}/dbus-1/system-services/org.freedesktop.PolicyKit1.service
%attr(700,root,root) %dir /var/lib/polkit-1
%{_mandir}/man1/pkaction.1*
%{_mandir}/man1/pkcheck.1*
%{_mandir}/man1/pkexec.1*
%{_mandir}/man8/pklocalauthority.8*
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
%attr(755,root,root) %{_libdir}/libpolkit-backend-1.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libpolkit-backend-1.so.0
%attr(755,root,root) %{_libdir}/libpolkit-gobject-1.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libpolkit-gobject-1.so.0
%{_libdir}/girepository-1.0/*.typelib

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/pk-example-frobnicate
%attr(755,root,root) %{_libdir}/libpolkit-agent-1.so
%attr(755,root,root) %{_libdir}/libpolkit-backend-1.so
%attr(755,root,root) %{_libdir}/libpolkit-gobject-1.so
%{_libdir}/libpolkit-agent-1.la
%{_libdir}/libpolkit-backend-1.la
%{_libdir}/libpolkit-gobject-1.la
%{_includedir}/polkit-1
%{_pkgconfigdir}/polkit-agent-1.pc
%{_pkgconfigdir}/polkit-backend-1.pc
%{_pkgconfigdir}/polkit-gobject-1.pc
%{_datadir}/gir-1.0/*.gir

%files static
%defattr(644,root,root,755)
%{_libdir}/libpolkit-agent-1.a
%{_libdir}/libpolkit-backend-1.a
%{_libdir}/libpolkit-gobject-1.a
