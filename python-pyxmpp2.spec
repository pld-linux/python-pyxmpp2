# Conditional build:
%bcond_without	doc	# Sphinx documentation
%bcond_with	tests	# unit tests
%bcond_without	python2 # CPython 2.x module
%bcond_without	python3 # CPython 3.x module

%define		module		pyxmpp2
%define		egg_name	pyxmpp2
%define		pypi_name	pyxmpp2
Summary:	XMPP implementation for Python
Name:		python-%{pypi_name}
Version:	2.0.1
Release:	12
License:	LGPL v2.1+
Group:		Libraries/Python
#Source0:	https://github.com/Jajcus/pyxmpp2/releases/download/2.0.1/pyxmpp2-2.0.1.tar.gz
Source0:	https://github.com/Jajcus/pyxmpp2/archive/%{version}.tar.gz
# Source0-md5:	add2c546f4473385c7222b623175e6ba
Patch0:		py.patch
Patch1:		tls.patch
Patch2:		newer-setuptools.patch
URL:		https://github.com/Jajcus/pyxmpp2
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.714
%if %{with python2}
BuildRequires:	python-modules
BuildRequires:	python-setuptools
%if %{with tests}
BuildRequires:	python-pyasn1
%endif
%endif
%if %{with python3}
BuildRequires:	python3-2to3
BuildRequires:	python3-modules
BuildRequires:	python3-setuptools
%if %{with tests}
BuildRequires:	python3-pyasn1
%endif
%endif
%if %{with doc}
BuildRequires:	epydoc
%endif
Requires:	python-dns >= 1.16.0
Requires:	python-modules
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
XMPP implementation for Python.

%package -n python3-%{pypi_name}
Summary:	XMPP implementation for Python
Group:		Libraries/Python
Requires:	python3-dns >= 1.16.0
Requires:	python3-modules

%description -n python3-%{pypi_name}
XMPP implementation for Python.

%package apidocs
Summary:	API documentation for Python %{module} module
Summary(pl.UTF-8):	Dokumentacja API modułu Pythona %{module}
Group:		Documentation

%description apidocs
API documentation for Python %{module} module.

%description apidocs -l pl.UTF-8
Dokumentacja API modułu Pythona %{module}.

%prep
%setup -q -n %{pypi_name}-%{version}
%patch -P 0 -p1
%patch -P 1 -p1
%patch -P 2 -p1

find . -type f -exec sed -i 's|^#![[:space:]]*/usr/bin/python\(\S*\)|#!/usr/bin/python2\1|' "{}" ";"

install -d orgsrc
mv !(orgsrc) orgsrc
%if %{with python2}
cp -a orgsrc python2-src
%endif

%if %{with python3}
cp -a orgsrc python3-src
2to3-%{py3_ver} -w --no-diffs python3-src
sed -i -e 's#def __unicode__(#def __str__(#g' \
    python3-src/pyxmpp2/*.py \
    python3-src/auxtools/make_conformance_table.py \
    python3-src/pyxmpp2/ext/vcard.py \
    python3-src/pyxmpp2/test/resolver.py \
    python3-src/pyxmpp2/mainloop/interfaces.py
%endif

%build
%if %{with python2}
cd python2-src
%py_build %{?with_tests:test}
cd ..
%endif

%if %{with python3}
cd python3-src
%py3_build %{?with_tests:test}
cd ..
%endif

%if %{with doc}
cd orgsrc/doc
%{__make} PYTHON="%{__python}"
cd ..
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with python2}
cd python2-src
%py_install

# when files are installed in other way that standard 'setup.py
# they need to be (re-)compiled
# change %{py_sitedir} to %{py_sitescriptdir} for 'noarch' packages!
%py_ocomp $RPM_BUILD_ROOT%{py_sitedir}
%py_comp $RPM_BUILD_ROOT%{py_sitedir}

%py_postclean
cd ..
%endif

%if %{with python3}
cd python3-src
%py3_install
cd ..
%endif

# in case there are examples provided
%if %{with python2}
cd python2-src
install -d $RPM_BUILD_ROOT%{_examplesdir}/python-%{pypi_name}-%{version}
cp -a examples/*.py $RPM_BUILD_ROOT%{_examplesdir}/python-%{pypi_name}-%{version}
find $RPM_BUILD_ROOT%{_examplesdir}/python-%{pypi_name}-%{version} -name '*.py' \
	| xargs sed -i '1s|^#!.*python\b|#!%{__python}|'
cd ..
%endif
%if %{with python3}
cd python3-src
install -d $RPM_BUILD_ROOT%{_examplesdir}/python3-%{pypi_name}-%{version}
cp -a examples/*.py $RPM_BUILD_ROOT%{_examplesdir}/python3-%{pypi_name}-%{version}
find $RPM_BUILD_ROOT%{_examplesdir}/python3-%{pypi_name}-%{version} -name '*.py' \
	| xargs sed -i '1s|^#!.*python\b|#!%{__python3}|'
cd ..
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{with python2}
%files
%defattr(644,root,root,755)
%doc orgsrc/{README.rst,TODO}
%{py_sitescriptdir}/%{module}
%{py_sitescriptdir}/%{egg_name}-%{version}-py*.egg-info
%{_examplesdir}/python-%{pypi_name}-%{version}
%endif

%if %{with python3}
%files -n python3-%{pypi_name}
%defattr(644,root,root,755)
%doc orgsrc/{README.rst,TODO}
%{py3_sitescriptdir}/%{module}
%{py3_sitescriptdir}/%{egg_name}-%{version}-py*.egg-info
%{_examplesdir}/python3-%{pypi_name}-%{version}
%endif

%if %{with doc}
%files apidocs
%defattr(644,root,root,755)
%doc orgsrc/doc/www/api/*
%endif
