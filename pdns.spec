# TODO
# - warning: Installed (but unpackaged) file(s) found:
#   /etc/pdns/pdns.conf-dist
# - do not use 'djbdns' group!
Summary:	PowerDNS - a Versatile Database Driven Nameserver
Summary(pl.UTF-8):	PowerDNS - wielofunkcyjny serwer nazw korzystający z relacyjnych baz danych
Name:		pdns
Version:	4.3.2
Release:	10
License:	GPL v2
Group:		Networking/Daemons
Source0:	https://downloads.powerdns.com/releases/%{name}-%{version}.tar.bz2
# Source0-md5:	ad4eee6cb66b94b2d23b7a7b0f4cc824
Source1:	https://downloads.powerdns.com/documentation/%{name}.pdf
# Source1-md5:	15bdde9d84af6ef1485dc2f5fa3f81df
Source2:	https://downloads.powerdns.com/documentation/%{name}.txt
Source3:	%{name}.init
Source4:	%{name}.conf
Source5:	%{name}.sysconfig
Patch0:		%{name}-boost.patch
Patch1:		%{name}-openldap-2.3.patch
Patch2:		gcc11.patch
URL:		https://www.powerdns.com/
BuildRequires:	autoconf >= 2.61
BuildRequires:	automake >= 1:1.11
BuildRequires:	bison
BuildRequires:	boost-devel >= 1.35.0
BuildRequires:	flex
BuildRequires:	libpq++-devel
BuildRequires:	libstdc++-devel >= 6:4.7
BuildRequires:	libtool >= 2:2.2.2
BuildRequires:	lua-devel >= 5.1
BuildRequires:	mysql-devel
BuildRequires:	openldap-devel >= 2.4.6
BuildRequires:	openssl-devel
BuildRequires:	pkgconfig
BuildRequires:	polarssl-devel >= 1.1
BuildRequires:	postgresql-devel
BuildRequires:	protobuf-devel
BuildRequires:	rpmbuild(macros) >= 1.647
BuildRequires:	sed >= 4.0
BuildRequires:	sqlite3-devel >= 3
BuildRequires:	zlib-devel
Requires(post,preun,postun):	systemd-units >= 38
Requires(post):	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	rc-scripts
Requires:	systemd-units >= 0.38
Provides:	group(djbdns)
Provides:	nameserver
Provides:	user(pdns)
Obsoletes:	powerdns < 2.9.4
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
%patch -P0 -p1
%patch -P1 -p1
%patch -P2 -p1
cp -p %{SOURCE1} .
cp -p %{SOURCE2} .
cp -p %{SOURCE4} .

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
	--sysconfdir=%{_sysconfdir}/%{name} \
	--disable-silent-rules \
	--disable-static \
	--enable-tools \
	--with-dynmodules="gsqlite3 gmysql gpgsql pipe ldap" \
	--with-lua \
	--with-modules="" \
	--with-mysql-includes=%{_includedir} \
	--with-mysql-lib=%{_libdir} \
	--with-pgsql-includes=%{_includedir} \
	--with-pgsql-lib=%{_libdir} \
	--with-socketdir=/var/run \
	--with-system-polarssl \
	--with-systemd=%{systemdunitdir}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir}/%{name},/etc/sysconfig}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

cp -p %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
cp -p %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/%{name}.conf
cp -p %{SOURCE5} $RPM_BUILD_ROOT/etc/sysconfig/pdns

# useless - modules are dlopened by *.so
%{__rm} -f $RPM_BUILD_ROOT%{_libdir}/%{name}/*.la

# we put that in using %doc
%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 32 djbdns
%useradd -u 30 -d /var/lib/pdns -s /bin/false -c "pdns User" -g djbdns pdns

%post
%systemd_post %{name}.service
# dirty hack so the config file is processed correctly, and server does not respawn
sed -i -e 's/^ *//' /etc/pdns/pdns.conf

/sbin/chkconfig --add pdns
%service pdns restart

%preun
if [ "$1" = "0" ]; then
	%service pdns stop
	/sbin/chkconfig --del pdns
fi
%systemd_preun %{name}.service

%postun
if [ "$1" = "0" ]; then
	%userremove pdns
	%groupremove djbdns
fi
%systemd_reload

%files
%defattr(644,root,root,755)
%doc INSTALL README pdns.pdf pdns.txt
%attr(754,root,root) /etc/rc.d/init.d/pdns
%dir %{_sysconfdir}/%{name}
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/pdns
%{systemdunitdir}/pdns.service
%{systemdunitdir}/pdns@.service
%attr(755,root,root) %{_sbindir}/pdns_server
%attr(755,root,root) %{_bindir}/calidns
%attr(755,root,root) %{_bindir}/dnsbulktest
%attr(755,root,root) %{_bindir}/dnsgram
%attr(755,root,root) %{_bindir}/dnspcap2calidns
%attr(755,root,root) %{_bindir}/dnspcap2protobuf
%attr(755,root,root) %{_bindir}/dnsreplay
%attr(755,root,root) %{_bindir}/dnsscan
%attr(755,root,root) %{_bindir}/dnsscope
%attr(755,root,root) %{_bindir}/dnstcpbench
%attr(755,root,root) %{_bindir}/dnswasher
%attr(755,root,root) %{_bindir}/dumresp
%attr(755,root,root) %{_bindir}/ixplore
%attr(755,root,root) %{_bindir}/nproxy
%attr(755,root,root) %{_bindir}/nsec3dig
%attr(755,root,root) %{_bindir}/pdns_control
%attr(755,root,root) %{_bindir}/pdns_notify
%attr(755,root,root) %{_bindir}/pdnsutil
%attr(755,root,root) %{_bindir}/saxfr
%attr(755,root,root) %{_bindir}/sdig
%attr(755,root,root) %{_bindir}/stubquery
%attr(755,root,root) %{_bindir}/zone2json
%attr(755,root,root) %{_bindir}/zone2ldap
%attr(755,root,root) %{_bindir}/zone2sql
%dir %{_libdir}/%{name}
%{_mandir}/man1/calidns.1*
%{_mandir}/man1/dnsbulktest.1*
%{_mandir}/man1/dnsgram.1*
%{_mandir}/man1/dnspcap2calidns.1*
%{_mandir}/man1/dnspcap2protobuf.1*
%{_mandir}/man1/dnsreplay.1*
%{_mandir}/man1/dnsscan.1*
%{_mandir}/man1/dnsscope.1*
%{_mandir}/man1/dnstcpbench.1*
%{_mandir}/man1/dnswasher.1*
%{_mandir}/man1/dumresp.1*
%{_mandir}/man1/ixplore.1*
%{_mandir}/man1/nproxy.1*
%{_mandir}/man1/nsec3dig.1*
%{_mandir}/man1/pdns_control.1*
%{_mandir}/man1/pdns_notify.1*
%{_mandir}/man1/pdns_server.1*
%{_mandir}/man1/pdnsutil.1*
%{_mandir}/man1/saxfr.1*
%{_mandir}/man1/sdig.1*
%{_mandir}/man1/zone2json.1*
%{_mandir}/man1/zone2ldap.1*
%{_mandir}/man1/zone2sql.1*

%files backend-gmysql
%defattr(644,root,root,755)
%doc modules/gmysqlbackend/*schema.mysql.sql
%attr(755,root,root) %{_libdir}/%{name}/*mysql*.so*

%files backend-gpgsql
%defattr(644,root,root,755)
%doc modules/gpgsqlbackend/*schema.pgsql.sql
%attr(755,root,root) %{_libdir}/%{name}/*pgsql*.so*

%files backend-gsqlite3
%defattr(644,root,root,755)
%doc modules/gsqlite3backend/*schema.sqlite3.sql
%attr(755,root,root) %{_libdir}/%{name}/*sqlite3*.so*

%files backend-pipe
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/%{name}/*pipe*.so*

%files backend-ldap
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/%{name}/*ldap*.so*
