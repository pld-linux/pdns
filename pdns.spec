Summary:	PowerDNS is a Versatile Database Driven Nameserver
Summary(pl):	PowerDNS to wielofunkcyjny serwer nazw korzystaj�cy z relacyjnych baz danych
Name:		pdns
Version:	2.9.10
Release:	1
License:	GPL
Group:		Networking/Daemons
Source0:	http://downloads.powerdns.com/releases/%{name}-%{version}.tar.gz
# Source0-md5:	a91f15c90f6551fb817cb708e29d5a37
Source1:	http://downloads.powerdns.com/documentation/%{name}.pdf
# Source1-md5:	e82b91120cf66f146283ca138025c9d3
Source2:	http://downloads.powerdns.com/documentation/%{name}.txt
Source3:	%{name}.init
Source4:	%{name}.conf
Source5:	%{name}.sysconfig
URL:		http://www.powerdns.com/
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	libpq++-devel
BuildRequires:	libstdc++-devel
BuildRequires:	mysql-devel
BuildRequires:	zlib-devel
PreReq:		rc-scripts
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/useradd
Requires(pre):	/usr/sbin/groupadd
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/userdel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Provides:	nameserver
Provides:	powerdns
Obsoletes:	nameserver
Obsoletes:	powerdns

%description
PowerDNS is a versatile nameserver which supports a large number of
different backends ranging from simple zonefiles to relational
databases and load balancing/failover algorithms.

%description -l pl
PowerDNS to wielofunkcyjny serwer nazw posiadaj�cy du�� liczb� wtyczek
od prostych stref (a'la BIND) pocz�wszy, a na relacyjnych bazach danych
sko�czywszy oraz zawieraj�cy algorytmy zr�wnowa�enia obci��enia i 
prze��czania w wypadku awarii.

%package backend-pipe
Summary:	PowerDNS support for custom pipe backend
Summary(pl):	Wsparcie PowerDNS dla w�asnego mechanizmu przechowywania stref
Group:		Development/Libraries

%description backend-pipe
This package allows creation of own backend using simple STDIN/STDOUT
API. Example backend script in perl is provided in package documentation.

%description backend-pipe -l pl
Ten pakiet pozwala na utworzenie w�asnego mechanizmu przechowywania stref
za pomoc� prostego interfejsu STDIN/STDOUT. Przyk�adowy skrypt w perlu zosta�
do��czony do dokumentacji pakietu.

%package backend-pgsql
Summary:	PowerDNS support for PostgreSQL
Summary(pl):	Wsparcie PowerDNS dla baz PostgresQL
Group:		Development/Libraries
Requires:	postgresql

%description backend-pgsql
This package allows zone storage in PostgreSQL relational db tables.

%description backend-pgsql -l pl
Ten pakiet pozwala na przechowywanie danych o strefach w tabelach 
relacyjnej bazy danych PostgreSQL.

%package backend-mysql
Summary:	PowerDNS support for MySQL
Summary(pl):	Wsparcie PowerDNS dla baz MySQL
Group:		Development/Libraries
Requires:	mysql

%description backend-mysql
This package allows zone storage in MySQL relational db tables.

%description backend-mysql -l pl
Ten pakiet pozwala na przechowywanie danych o strefach w tabelach 
relacyjnej bazy danych MySQL.

%prep
%setup -q
cp %{SOURCE1} .
cp %{SOURCE2} .

%build
%configure \
	--libdir=%{_libdir}/%{name} \
	--sysconfdir=%{_sysconfdir}/%{name} \
	--with-socketdir=/var/run \
	--with-dynmodules="gmysql gpgsql pipe" \
	--with-modules="" \
	--with-pgsql-includes=/usr/include \
	--enable-mysql \
	--enable-pgsql \
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
if [ -n "`getgid djbdns`" ]; then
	if [ "`getgid djbdns`" != "32" ]; then
		echo "Error: group djbdns doesn't have gid=32. Correct this before installing pdns." 1>&2
		exit 1
	fi
else
	/usr/sbin/groupadd -g 32 -r -f djbdns
fi
if [ -n "`id -u pdns 2>/dev/null`" ]; then
	if [ "`id -u pdns`" != "30" ]; then
		echo "Error: user pdns doesn't have uid=30. Correct this before installing pdns." 1>&2
		exit 1
	fi
else
	/usr/sbin/useradd -u 30 -r -d /dev/null -s /bin/false -c "pdns User" -g djbdns pdns 1>&2
fi

%post
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
	/usr/sbin/userdel pdns
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog HACKING INSTALL README TODO WARNING pdns.pdf pdns.txt
%config(noreplace) %attr(0600,root,root) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %attr(0754,root,root) %{_initrddir}/%{name}
%attr(640,root,root)  %config(noreplace) %verify(not size mtime md5) /etc/sysconfig/pdns
%dir %{_sysconfdir}/%{name}
%attr(755,root,root) %{_sbindir}/*
%{_mandir}/man8/*

%files backend-mysql
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/%{name}/*mysql*.so*

%files backend-pgsql
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/%{name}/*pgsql*.so*

%files backend-pipe
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/%{name}/*pipe*.so*
