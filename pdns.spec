Summary:	PowerDNS is a Versatile Database Driven Nameserver
Summary(pl.UTF-8):	PowerDNS to wielofunkcyjny serwer nazw korzystający z relacyjnych baz danych
Name:		pdns
Version:	3.1
Release:	2
License:	GPL
Group:		Networking/Daemons
Source0:	http://downloads.powerdns.com/releases/%{name}-%{version}.tar.gz
# Source0-md5:	7dedae65403b31a795b2d53a512947fd
Source1:	http://downloads.powerdns.com/documentation/%{name}.pdf
# Source1-md5:	cb69cd9655e4cb319c66adb2c733314d
Source2:	http://downloads.powerdns.com/documentation/%{name}.txt
Source3:	%{name}.init
Source4:	%{name}.conf
Source5:	%{name}.sysconfig
Patch0:		configure.ac.patch
Patch1:		%{name}-int16.patch
Patch2:		%{name}-openldap-2.3.patch
Patch3:		gcc4.patch
URL:		http://www.powerdns.com/
BuildRequires:	autoconf >= 2.52
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	boost-devel >= 1.35.0
BuildRequires:	flex
BuildRequires:	libpq++-devel
BuildRequires:	libstdc++-devel
BuildRequires:	libtool
BuildRequires:	lua51-devel
BuildRequires:	mysql-devel
BuildRequires:	openldap-devel >= 2.4.6
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	sed >= 4.0
BuildRequires:	sqlite3-devel
BuildRequires:	zlib-devel
Requires(post):	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	rc-scripts
Provides:	group(djbdns)
Provides:	nameserver
Provides:	user(pdns)
Obsoletes:	powerdns
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
PowerDNS is a versatile nameserver which supports a large number of
different backends ranging from simple zonefiles to relational
databases and load balancing/failover algorithms.

%description -l pl.UTF-8
PowerDNS to wielofunkcyjny serwer nazw posiadający dużą liczbę wtyczek
od prostych stref (a'la BIND) począwszy, a na relacyjnych bazach
danych skończywszy oraz zawierający algorytmy zrównoważenia obciążenia
i przełączania w wypadku awarii.

%package backend-pipe
Summary:	PowerDNS support for custom pipe backend
Summary(pl.UTF-8):	Obsługa własnego mechanizmu przechowywania stref dla PowerDNS-a
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description backend-pipe
This package allows creation of own backend using simple STDIN/STDOUT
API. Example backend script in Perl is provided in package
documentation.

%description backend-pipe -l pl.UTF-8
Ten pakiet pozwala na utworzenie własnego mechanizmu przechowywania
stref za pomocą prostego interfejsu STDIN/STDOUT. Przykładowy skrypt w
Perlu został dołączony do dokumentacji pakietu.

%package backend-gpgsql
Summary:	PowerDNS support for PostgreSQL
Summary(pl.UTF-8):	Obsługa baz PostgreSQL dla PowerDNS-a
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description backend-gpgsql
This package allows zone storage in PostgreSQL relational db tables.

%description backend-gpgsql -l pl.UTF-8
Ten pakiet pozwala na przechowywanie danych o strefach w tabelach
relacyjnej bazy danych PostgreSQL.

%package backend-gmysql
Summary:	PowerDNS support for MySQL
Summary(pl.UTF-8):	Obsługa baz MySQL dla PowerDNS-a
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description backend-gmysql
This package allows zone storage in MySQL relational db tables.

%description backend-gmysql -l pl.UTF-8
Ten pakiet pozwala na przechowywanie danych o strefach w tabelach
relacyjnej bazy danych MySQL.

%package backend-gsqlite3
Summary:	PowerDNS support for SQLite 3
Summary(pl.UTF-8):	Obsługa baz SQLite 3 dla PowerDNS-a
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description backend-gsqlite3
This package allows zone storage in SQLite 3 relational db tables.

%description backend-gsqlite3 -l pl.UTF-8
Ten pakiet pozwala na przechowywanie danych o strefach w tabelach
relacyjnej bazy danych SQLite 3.

%package backend-ldap
Summary:	PowerDNS support for LDAP
Summary(pl.UTF-8):	Obsługa LDAP dla PowerDNS-a
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description backend-ldap
This package allows zone storage in LDAP directory.

%description backend-ldap -l pl.UTF-8
Ten pakiet pozwala na przechowywanie danych o strefach w katalogu
LDAP.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
cp %{SOURCE1} .
cp %{SOURCE2} .
cp %{SOURCE4} .

%if "%{_lib}" != "lib"
%{__sed} -i -e 's/module-dir=\/usr\/lib\/pdns/module-dir=\/usr\/%{_lib}\/pdns/' pdns.conf
%endif

%build
CPPFLAGS="-DHAVE_NAMESPACE_STD -DHAVE_CXX_STRING_HEADER -DDLLIMPORT=\"\""
%{__libtoolize}
%{__aclocal} -I .
%{__autoconf}
%{__automake}
%configure \
	--libdir=%{_libdir}/%{name} \
	--sysconfdir=%{_sysconfdir}/%{name} \
	--disable-static \
	--with-lua \
	--with-pgsql-includes=%{_includedir} \
	--with-pgsql-lib=%{_libdir} \
	--with-mysql-includes=%{_includedir} \
	--with-mysql-lib=%{_libdir} \
	--with-dynmodules="gsqlite3 gmysql gpgsql pipe ldap" \
	--with-modules="" \
	--with-socketdir=/var/run

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir}/%{name},/etc/sysconfig}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/%{name}.conf
install %{SOURCE5} $RPM_BUILD_ROOT/etc/sysconfig/pdns

# useless - modules are dlopened by *.so
rm -f $RPM_BUILD_ROOT%{_libdir}/%{name}/*.la

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 32 djbdns
%useradd -u 30 -d /var/lib/pdns -s /bin/false -c "pdns User" -g djbdns pdns

%post
# dirty hack so the config file is processed correctly, and server does not respawn
sed -i -e 's/^ *//' /etc/pdns/pdns.conf

/sbin/chkconfig --add pdns
%service pdns restart

%preun
if [ "$1" = "0" ]; then
	%service pdns stop
	/sbin/chkconfig --del pdns
fi

%postun
if [ "$1" = "0" ]; then
	%userremove pdns
	%groupremove djbdns
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog HACKING INSTALL README TODO pdns.pdf pdns.txt
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%dir %{_sysconfdir}/%{name}
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/pdns
%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_bindir}/*
%dir %{_libdir}/%{name}
%{_mandir}/man8/*

%files backend-gmysql
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/%{name}/*mysql*.so*

%files backend-gpgsql
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/%{name}/*pgsql*.so*

%files backend-gsqlite3
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/%{name}/*sqlite3*.so*

%files backend-pipe
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/%{name}/*pipe*.so*

%files backend-ldap
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/%{name}/*ldap*.so*
