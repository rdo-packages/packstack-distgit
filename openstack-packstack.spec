%global with_doc %{!?_without_doc:1}%{?_without_doc:0}
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

# openstack-packstack ----------------------------------------------------------

Name:           openstack-packstack
Version:        9.0.0
Release:        1%{?dist}
Summary:        Openstack Install Utility

Group:          Applications/System
License:        ASL 2.0 and GPLv2
URL:            https://github.com/openstack/packstack
Source0:        https://tarballs.openstack.org/packstack/packstack-%{upstream_version}.tar.gz

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-pbr
BuildRequires:  git

Requires:       openssh-clients
Requires:       python-netaddr
Requires:       openstack-packstack-puppet == %{version}-%{release}
Obsoletes:      packstack-modules-puppet
Requires:       python-setuptools
Requires:       PyYAML
Requires:       python-docutils
Requires:       pyOpenSSL
Requires:       python-pbr

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
Requires: puppet-mongodb
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

%description puppet
Puppet module used by Packstack to install OpenStack


# openstack-packstack-doc ------------------------------------------------------

%if 0%{?with_doc}
%package doc
Summary:          Documentation for Packstack
Group:            Documentation

%if 0%{?rhel} == 6
BuildRequires:  python-sphinx10
%else
BuildRequires:  python-sphinx
%endif

%description doc
This package contains documentation files for Packstack.
%endif


# prep -------------------------------------------------------------------------

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


# build ------------------------------------------------------------------------

%build
%{__python} setup.py build

%if 0%{?with_doc}
cd docs
%if 0%{?rhel} == 6
make man SPHINXBUILD=sphinx-1.0-build
%else
make man
%endif
%endif


# install ----------------------------------------------------------------------

%install
%{__python} setup.py install --skip-build --root %{buildroot}

# Delete tests
rm -fr %{buildroot}%{python_sitelib}/tests

# Install Puppet module
mkdir -p %{buildroot}/%{_datadir}/openstack-puppet/modules
cp -r %{_builddir}/puppet/modules/packstack  %{buildroot}/%{_datadir}/openstack-puppet/modules/

# Move packstack documentation
mkdir -p %{buildroot}/%{_datadir}/packstack
install -p -D -m 644 docs/packstack.rst %{buildroot}/%{_datadir}/packstack

# Move Puppet manifest templates back to original place
mkdir -p %{buildroot}/%{python_sitelib}/packstack/puppet
mv %{_builddir}/puppet/templates %{buildroot}/%{python_sitelib}/packstack/puppet/

%if 0%{?with_doc}
mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 docs/_build/man/*.1 %{buildroot}%{_mandir}/man1/
%endif

# Remove docs directory
rm -fr %{buildroot}%{python_sitelib}/docs

# files ------------------------------------------------------------------------

%files
%doc LICENSE
%{_bindir}/packstack
%{_datadir}/packstack
%{python_sitelib}/packstack
%{python_sitelib}/packstack-*.egg-info

%files puppet
%defattr(644,root,root,755)
%{_datadir}/openstack-puppet/modules/packstack

%if 0%{?with_doc}
%files doc
%{_mandir}/man1/packstack.1.gz
%endif


# changelog --------------------------------------------------------------------

%changelog
* Fri Oct 21 2016 Alan Pevec <alan.pevec@redhat.com> 9.0.0-1
- Update to 9.0.0

* Tue Oct 18 2016 Alan Pevec <alan.pevec@redhat.com> 9.0.0-0.4.0rc4
- Update to 9.0.0.0rc4

* Fri Oct 07 2016 Alan Pevec <alan.pevec@redhat.com> 9.0.0-0.3.0rc3
- Update to 9.0.0.0rc3

* Mon Oct 03 2016 Alan Pevec <alan.pevec@redhat.com> 9.0.0-0.2.0rc2
- Update to 9.0.0.0rc2

* Thu Sep 22 2016 Alfredo Moralejo <amoralej@redhat.com> 9.0.0-0.1.0rc1
- Update to 9.0.0.0rc1

