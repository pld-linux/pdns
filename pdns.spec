%define name		pdns
%define version		2.9.4
%define release		0.1

Summary:	PowerDNS is a Versatile Database Driven Nameserver
Summary(pl):	PowerDNS to wielofunkcyjny serwer nazw korzystaj±cy z relacyjnych baz danych
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	GPL
Group:		Networking/Daemons
URL:		http://www.powerdns.com/
Source0:	http://downloads.powerdns.com/releases/%{name}-%{version}.tar.gz
Source1:	http://downloads.powerdns.com/documentation/%{name}.pdf
Source2:	%{name}.init
Source3:	%{name}.conf

BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	mysql-devel
BuildRequires:	postgresql-c++-devel
BuildRequires:	libstdc++-devel
BuildRequires:	zlib-devel
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/useradd
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/bin/id
Requires(postun):	/usr/sbin/userdel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Provides:	nameserver pdns powerdns
Obsoletes:	nameserver pdns powerdns

%description
PowerDNS is a versatile nameserver which supports a large number of
different backends ranging from simple zonefiles to relational
databases and load balancing/failover algorithms.

%description -l pl
PowerDNS to wielofunkcyjny serwer nazw posiadaj±cy du¿± liczbê wtyczek
od prostych stref (a'la BIND) pocz±wszy, a na relacyjnych bazach danych
skoñczywszy oraz zawieraj±cy algorytmy zrównowa¿enia obci±¿enia i 
prze³±czania w wypadku awarii.

%package devel
Summary:	PowerDNS developement libraries
Summary(pl):	Biblioteki PowerDNS
Group:		Development/Libraries

%description devel 
Developement libraries for PowerDNS.

%description devel -l pl
Pliki bibliotek dla PowerDNS.

%package static
Summary:	PowerDNS static libs
Summary(pl):	Biblioteki statyczne PowerDNS
Group:		Development/Libraries

%description static
Static PowerDNS libraries.

%description static -l pl
Statyczne biblioteki PowerDNS.

%prep

%setup -q 

%build

%configure \
    --libexecdir=%{_libexecdir} \
    --libdir=%{_libdir}/%{name} \
    --bindir=%{_sbindir} \
    --sbindir=%{_sbindir} \
    --sysconfdir=%{_sysconfdir}/%{name} \
    --with-socketdir=/var/run \
    --with-dynmodules="gmysql gpgsql pipe" \
    --with-modules="" \
    --with-pgsql-includes=/usr/include \
    --enable-mysql \
    --enable-pgsql 

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR="%{buildroot}" 

install -d %{buildroot}/%{_initrddir}
install -d %{buildroot}/%{_sysconfdir}/%{name}
install -m644 %{SOURCE1} %{buildroot}/%{name}.pdf
install -m754 %{SOURCE2} %{buildroot}/%{_initrddir}/%{name}
install -m600 %{SOURCE3} %{buildroot}/%{_sysconfdir}/%{name}/%{name}.conf

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

%preun
/sbin/chkconfig --del pdns

%postun
if [ "$1" = "0" ]; then
	/usr/sbin/userdel pdns
fi

%clean
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}

%files
%defattr(644,root,root,755)
%doc ChangeLog HACKING INSTALL README TODO WARNING %{name}.pdf
%config(noreplace) %attr(0600,root,root) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %attr(0754,root,root) %{_initrddir}/%{name}
%dir %{_sysconfdir}%{name}
%attr(755,root,root) %{_sbindir}/*
%{_libdir}%{name}/*
%{_mandir}/man8/*

%files devel
%attr(755,root,root) %{_libdir}/%{name}/*.so
%attr(644,root,root) %{_libdir}/%{name}/*.la

%files static
%attr(644,root,root) %{_libdir}/%{name}/*.a
