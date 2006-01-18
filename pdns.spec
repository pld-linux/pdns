Summary:	PowerDNS is a Versatile Database Driven Nameserver
Summary(pl):	PowerDNS to wielofunkcyjny serwer nazw korzystaj±cy z relacyjnych baz danych
Name:		pdns
Version:	2.9.19
Release:	4
License:	GPL
Group:		Networking/Daemons
Source0:	http://downloads.powerdns.com/releases/%{name}-%{version}.tar.gz
# Source0-md5:	30c96878b56845329cca5b8a351277b4
Source1:	http://downloads.powerdns.com/documentation/%{name}.pdf
# Source1-md5:	f183b5bec39e40f8c55c19afc3a3f933
Source2:	http://downloads.powerdns.com/documentation/%{name}.txt
Source3:	%{name}.init
Source4:	%{name}.conf
Source5:	%{name}.sysconfig
Patch0:		%{name}-configure.patch
Patch1:		%{name}-int16.patch
Patch2:		%{name}-openldap-2.3.patch
URL:		http://www.powerdns.com/
BuildRequires:	bison
BuildRequires:	boost-devel
BuildRequires:	boost-ref-devel
BuildRequires:	flex
BuildRequires:	libstdc++-devel
BuildRequires:	libpq++-devel
BuildRequires:	mysql-devel
BuildRequires:	openldap-devel >= 2.3.0
BuildRequires:	rpmbuild(macros) >= 1.202
BuildRequires:	zlib-devel
PreReq:		rc-scripts
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Provides:	group(djbdns)
Provides:	nameserver
Provides:	user(pdns)
Obsoletes:	powerdns

%description
PowerDNS is a versatile nameserver which supports a large number of
different backends ranging from simple zonefiles to relational
databases and load balancing/failover algorithms.

%description -l pl
PowerDNS to wielofunkcyjny serwer nazw posiadaj±cy du¿± liczbê wtyczek
od prostych stref (a'la BIND) pocz±wszy, a na relacyjnych bazach
danych skoñczywszy oraz zawieraj±cy algorytmy zrównowa¿enia obci±¿enia
i prze³±czania w wypadku awarii.

%package backend-pipe
Summary:	PowerDNS support for custom pipe backend
Summary(pl):	Wsparcie PowerDNS dla w³asnego mechanizmu przechowywania stref
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description backend-pipe
This package allows creation of own backend using simple STDIN/STDOUT
API. Example backend script in Perl is provided in package
documentation.

%description backend-pipe -l pl
Ten pakiet pozwala na utworzenie w³asnego mechanizmu przechowywania
stref za pomoc± prostego interfejsu STDIN/STDOUT. Przyk³adowy skrypt w
Perlu zosta³ do³±czony do dokumentacji pakietu.

%package backend-gpgsql
Summary:	PowerDNS support for PostgreSQL
Summary(pl):	Wsparcie PowerDNS dla baz PostgresQL
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description backend-gpgsql
This package allows zone storage in PostgreSQL relational db tables.

%description backend-gpgsql -l pl
Ten pakiet pozwala na przechowywanie danych o strefach w tabelach
relacyjnej bazy danych PostgreSQL.

%package backend-gmysql
Summary:	PowerDNS support for MySQL
Summary(pl):	Wsparcie PowerDNS dla baz MySQL
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description backend-gmysql
This package allows zone storage in MySQL relational db tables.

%description backend-gmysql -l pl
Ten pakiet pozwala na przechowywanie danych o strefach w tabelach
relacyjnej bazy danych MySQL.

%package backend-ldap
Summary:	PowerDNS support for LDAP
Summary(pl):	Wsparcie PowerDNS dla baz LDAP
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description backend-ldap
This package allows zone storage in LDAP directory.

%description backend-ldap -l pl
Ten pakiet pozwala na przechowywanie danych o strefach w katalogu
LDAP.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
cp %{SOURCE1} .
cp %{SOURCE2} .

%build
CPPFLAGS="-DHAVE_NAMESPACE_STD -DHAVE_CXX_STRING_HEADER -DDLLIMPORT=\"\""
%configure \
	--libdir=%{_libdir}/%{name} \
	--sysconfdir=%{_sysconfdir}/%{name} \
	--with-socketdir=/var/run \
	--with-dynmodules="gmysql gpgsql pipe ldap" \
	--with-modules="" \
	--enable-mysql \
	--enable-pgsql \
	--with-pgsql-lib=%{_libdir} \
	--with-pgsql-includes=%{_includedir} \
	--with-mysql-lib=%{_libdir} \
	--with-mysql-includes=%{_includedir} \
	--enable-ldap \
	--disable-static

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_initrddir},%{_sysconfdir}/%{name},/etc/sysconfig}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE3} $RPM_BUILD_ROOT%{_initrddir}/%{name}
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
TMP=`mktemp /tmp/pdns.install-tmp.XXXXXX`
sed 's/^ *//' /etc/pdns/pdns.conf > $TMP
cp /etc/pdns/pdns.conf /etc/pdns/pdns.conf.rpmsave
mv $TMP /etc/pdns/pdns.conf

/sbin/chkconfig --add pdns
if [ -f /var/lock/subsys/pdns ]; then
	/etc/rc.d/init.d/pdns restart >&2
else
	echo "Run \"/etc/rc.d/init.d/pdns start\" to start pdns." >&2
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/pdns ]; then
		/etc/rc.d/init.d/pdns stop
	fi
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
%attr(754,root,root) %{_initrddir}/%{name}
%dir %{_sysconfdir}/%{name}
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/pdns
%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_bindir}/*
%{_mandir}/man8/*

%files backend-gmysql
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/%{name}/*mysql*.so*

%files backend-gpgsql
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/%{name}/*pgsql*.so*

%files backend-pipe
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/%{name}/*pipe*.so*

%files backend-ldap
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/%{name}/*ldap*.so*
