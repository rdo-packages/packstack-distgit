# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%global with_doc %{!?_without_doc:1}%{?_without_doc:0}
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

# Guard for rhosp for packages not supported in OSP
%global rhosp 0

# openstack-packstack ----------------------------------------------------------

Name:           openstack-packstack
Epoch:          1
Version:        XXX
Release:        XXX
Summary:        Openstack Install Utility

Group:          Applications/System
License:        ASL 2.0 and GPLv2
URL:            https://github.com/openstack/packstack
Source0:        https://tarballs.openstack.org/packstack/packstack-%{upstream_version}.tar.gz

BuildArch:      noarch

BuildRequires:  python%{pyver}-devel
BuildRequires:  python%{pyver}-setuptools
BuildRequires:  python%{pyver}-pbr
BuildRequires:  git

Requires:       openssh-clients
Requires:       python%{pyver}-netaddr
Requires:       openstack-packstack-puppet == %{epoch}:%{version}-%{release}
Obsoletes:      packstack-modules-puppet
Requires:       python%{pyver}-pyOpenSSL >= 16.2.0
Requires:       python%{pyver}-pbr
Requires:       python%{pyver}-setuptools
Requires:       /usr/bin/yum

# Handle python2 exception
%if %{pyver} == 2
Requires:       python-netifaces
Requires:       PyYAML
Requires:       python-docutils
%else
Requires:       python%{pyver}-netifaces
Requires:       python%{pyver}-PyYAML
Requires:       python%{pyver}-docutils
%endif

%description
Packstack is a utility that uses Puppet modules to install OpenStack. Packstack
can be used to deploy various parts of OpenStack on multiple pre installed
servers over ssh.


# openstack-packstack-puppet ---------------------------------------------------

%package puppet
Summary:        Packstack Puppet module
Group:          Development/Libraries

# generated from packstack/Puppetfile:
# awk -F\' '/^mod / {print "Requires: puppet-" $2}' Puppetfile

Requires: puppet-aodh
Requires: puppet-ceilometer
Requires: puppet-cinder
Requires: puppet-glance
Requires: puppet-gnocchi
Requires: puppet-heat
Requires: puppet-horizon
Requires: puppet-ironic
Requires: puppet-keystone
Requires: puppet-manila
Requires: puppet-neutron
Requires: puppet-nova
Requires: puppet-openstack_extras
Requires: puppet-openstacklib
Requires: puppet-oslo
Requires: puppet-ovn
Requires: puppet-panko
Requires: puppet-sahara
Requires: puppet-swift
Requires: puppet-tempest
Requires: puppet-trove
Requires: puppet-vswitch
Requires: puppet-apache
Requires: puppet-certmonger
Requires: puppet-concat
Requires: puppet-firewall
Requires: puppet-inifile
Requires: puppet-memcached
Requires: puppet-mysql
Requires: puppet-nssdb
Requires: puppet-rabbitmq
Requires: puppet-redis
Requires: puppet-remote
Requires: puppet-rsync
Requires: puppet-ssh
Requires: puppet-stdlib
Requires: puppet-sysctl
Requires: puppet-vcsrepo
Requires: puppet-xinetd

%if 0%{rhosp} == 0
Requires: puppet-magnum
%endif

%description puppet
Puppet module used by Packstack to install OpenStack


# openstack-packstack-doc ------------------------------------------------------

%if 0%{?with_doc}
%package doc
Summary:          Documentation for Packstack
Group:            Documentation
BuildRequires:    python%{pyver}-sphinx
BuildRequires:    python%{pyver}-netaddr
BuildRequires:    python%{pyver}-pyOpenSSL

# Handle python2 exception
%if %{pyver} == 2
BuildRequires:    python-netifaces
BuildRequires:    PyYAML
%else
BuildRequires:    python%{pyver}-netifaces
BuildRequires:    python%{pyver}-PyYAML
%endif

%description doc
This package contains documentation files for Packstack.
%endif


%prep
%autosetup -n packstack-%{upstream_version} -S git

# Sanitizing a lot of the files in the puppet modules
find packstack/puppet/modules \( -name .fixtures.yml -o -name .gemfile -o -name ".travis.yml" -o -name .rspec \) -exec rm {} +
find packstack/puppet/modules \( -name "*.py" -o -name "*.rb" -o -name "*.pl" \) -exec sed -i '/^#!/{d;q}' {} + -exec chmod -x {} +
find packstack/puppet/modules \( -name "*.sh" \) -exec sed -i 's/^#!.*/#!\/bin\/bash/g' {} + -exec chmod +x {} +
find packstack/puppet/modules -name site.pp -size 0 -exec rm {} +
find packstack/puppet/modules \( -name spec -o -name ext \) | xargs rm -rf

# Moving this data directory out temporarily as it causes setup.py to throw errors
rm -rf %{_builddir}/puppet
mv packstack/puppet %{_builddir}/puppet

%build
%{pyver_build}

%if 0%{?with_doc}
%{pyver_bin} setup.py build_sphinx -b man
%endif

%install
%{pyver_install}

# Delete tests
rm -fr %{buildroot}%{pyver_sitelib}/tests

# Install Puppet module
mkdir -p %{buildroot}/%{_datadir}/openstack-puppet/modules
cp -r %{_builddir}/puppet/modules/packstack  %{buildroot}/%{_datadir}/openstack-puppet/modules/

# Move packstack documentation
mkdir -p %{buildroot}/%{_datadir}/packstack
install -p -D -m 644 docs/packstack.rst %{buildroot}/%{_datadir}/packstack

# Move Puppet manifest templates back to original place
mkdir -p %{buildroot}/%{pyver_sitelib}/packstack/puppet
mv %{_builddir}/puppet/templates %{buildroot}/%{pyver_sitelib}/packstack/puppet/

%if 0%{?with_doc}
mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 docs/build/man/*.1 %{buildroot}%{_mandir}/man1/
%endif

# Remove docs directory
rm -fr %{buildroot}%{pyver_sitelib}/docs

%files
%doc LICENSE
%{_bindir}/packstack
%{_datadir}/packstack
%{pyver_sitelib}/packstack
%{pyver_sitelib}/packstack-*.egg-info

%files puppet
%defattr(644,root,root,755)
%{_datadir}/openstack-puppet/modules/packstack

%if 0%{?with_doc}
%files doc
%{_mandir}/man1/packstack.1.gz
%endif

%changelog
