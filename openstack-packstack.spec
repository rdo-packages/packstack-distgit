%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
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
Source0:        https://tarballs.opendev.org/x/packstack/packstack-%{upstream_version}.tar.gz
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        https://tarballs.opendev.org/x/packstack/packstack-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif

BuildArch:      noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
BuildRequires:  openstack-macros
%endif

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-pbr
BuildRequires:  git-core

Requires:       openssh-clients
Requires:       python3-distro
Requires:       python3-netaddr
Requires:       openstack-packstack-puppet == %{epoch}:%{version}-%{release}
Obsoletes:      packstack-modules-puppet
Requires:       python3-pyOpenSSL >= 16.2.0
Requires:       python3-pbr
Requires:       python3-setuptools
Requires:       /usr/bin/yum

Requires:       python3-netifaces
Requires:       python3-PyYAML
Requires:       python3-docutils

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
Requires: puppet-placement
Requires: puppet-swift
Requires: puppet-tempest
Requires: puppet-vswitch
Requires: puppet-apache
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
Requires: puppet-sahara
Requires: puppet-trove
%endif

%description puppet
Puppet module used by Packstack to install OpenStack


# openstack-packstack-doc ------------------------------------------------------

%if 0%{?with_doc}
%package doc
Summary:          Documentation for Packstack
Group:            Documentation
BuildRequires:    python3-sphinx
BuildRequires:    python3-netaddr
BuildRequires:    python3-pyOpenSSL

BuildRequires:    python3-netifaces
BuildRequires:    python3-PyYAML

%description doc
This package contains documentation files for Packstack.
%endif


%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
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
%{py3_build}

%if 0%{?with_doc}
%{__python3} setup.py build_sphinx -b man
%endif

%install
%{py3_install}

# Delete tests
rm -fr %{buildroot}%{python3_sitelib}/tests

# Install Puppet module
mkdir -p %{buildroot}/%{_datadir}/openstack-puppet/modules
cp -r %{_builddir}/puppet/modules/packstack  %{buildroot}/%{_datadir}/openstack-puppet/modules/

# Move packstack documentation
mkdir -p %{buildroot}/%{_datadir}/packstack
install -p -D -m 644 docs/packstack.rst %{buildroot}/%{_datadir}/packstack

# Move Puppet manifest templates back to original place
mkdir -p %{buildroot}/%{python3_sitelib}/packstack/puppet
mv %{_builddir}/puppet/templates %{buildroot}/%{python3_sitelib}/packstack/puppet/

%if 0%{?with_doc}
mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 docs/build/man/*.1 %{buildroot}%{_mandir}/man1/
%endif

# Remove docs directory
rm -fr %{buildroot}%{python3_sitelib}/docs

%files
%doc LICENSE
%{_bindir}/packstack
%{_datadir}/packstack
%{python3_sitelib}/packstack
%{python3_sitelib}/packstack-*.egg-info

%files puppet
%defattr(644,root,root,755)
%{_datadir}/openstack-puppet/modules/packstack

%if 0%{?with_doc}
%files doc
%{_mandir}/man1/packstack.1.gz
%endif

%changelog

