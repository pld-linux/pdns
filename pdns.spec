Summary:	PowerDNS is a Versatile Database Driven Nameserver
Summary(pl):	PowerDNS to wielofunkcyjny serwer nazw korzystaj±cy z relacyjnych baz danych
Name:		pdns
Version:	2.9.16
Release:	2
License:	GPL
Group:		Networking/Daemons
Source0:	http://downloads.powerdns.com/releases/%{name}-%{version}.tar.gz
# Source0-md5:	7e9a859a5a21996dbf7b31cd61731dbc
Source1:	http://downloads.powerdns.com/documentation/%{name}.pdf
# Source1-md5:	72cce8fb180c3a70437187ff0912c2a3
Source2:	http://downloads.powerdns.com/documentation/%{name}.txt
Source3:	%{name}.init
Source4:	%{name}.conf
Source5:	%{name}.sysconfig
Patch0:		%{name}-configure.patch
URL:		http://www.powerdns.com/
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	libstdc++-devel
BuildRequires:	libpq++-devel
BuildRequires:	mysql-devel
BuildRequires:	openldap-devel
BuildRequires:	rpmbuild(macros) >= 1.159
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

%description backend-pipe
This package allows creation of own backend using simple STDIN/STDOUT
API. Example backend script in perl is provided in package
documentation.

%description backend-pipe -l pl
Ten pakiet pozwala na utworzenie w³asnego mechanizmu przechowywania
stref za pomoc¹ prostego interfejsu STDIN/STDOUT. Przyk³adowy skrypt w
perlu zosta³ do³±czony do dokumentacji pakietu.

%package backend-gpgsql
Summary:	PowerDNS support for PostgreSQL
Summary(pl):	Wsparcie PowerDNS dla baz PostgresQL
Group:		Development/Libraries
Requires:	postgresql

%description backend-gpgsql
This package allows zone storage in PostgreSQL relational db tables.

%description backend-gpgsql -l pl
Ten pakiet pozwala na przechowywanie danych o strefach w tabelach
relacyjnej bazy danych PostgreSQL.

%package backend-gmysql
Summary:	PowerDNS support for MySQL
Summary(pl):	Wsparcie PowerDNS dla baz MySQL
Group:		Development/Libraries
Requires:	mysql

%description backend-gmysql
This package allows zone storage in MySQL relational db tables.

%description backend-gmysql -l pl
Ten pakiet pozwala na przechowywanie danych o strefach w tabelach
relacyjnej bazy danych MySQL.

%package backend-ldap
Summary:	PowerDNS support for LDAP
Summary(pl):	Wsparcie PowerDNS dla baz LDAP
Group:		Development/Libraries
Requires:	openldap

%description backend-ldap
This package allows zone storage in LDAP directory.

%description backend-ldap -l pl
Ten pakiet pozwala na przechowywanie danych o strefach w katalogu LDAP.

%prep
%setup -q
%patch0 -p1
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
if [ -n "`/usr/bin/getgid djbdns`" ]; then
	if [ "`/usr/bin/getgid djbdns`" != "32" ]; then
		echo "Error: group djbdns doesn't have gid=32. Correct this before installing pdns." 1>&2
		exit 1
	fi
else
	/usr/sbin/groupadd -g 32 djbdns
fi
if [ -n "`/bin/id -u pdns 2>/dev/null`" ]; then
	if [ "`/bin/id -u pdns`" != "30" ]; then
		echo "Error: user pdns doesn't have uid=30. Correct this before installing pdns." 1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -u 30 -d /var/lib/pdns -s /bin/false -c "pdns User" -g djbdns pdns 1>&2
fi

%post
# dirty hack so the config file is processed correctly, and server does not respawn
TMP=`mktemp /tmp/pdns.install-tmp.XXXXXX`
sed 's/^ *//g' /etc/pdns/pdns.conf > $TMP
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
%doc ChangeLog HACKING INSTALL README TODO WARNING pdns.pdf pdns.txt
%config(noreplace) %attr(0600,root,root) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %attr(0754,root,root) %{_initrddir}/%{name}
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/sysconfig/pdns
%dir %{_sysconfdir}/%{name}
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
