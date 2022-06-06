Summary: Text mode Mail Client
Name: neomutt
Version: 20220606
Release: 1%{?dist}
Epoch: 5
Url: https://neomutt.org/

# Source, docs and contrib: GPLv2+, except for:
# BSD: Autosetup build system, queue.h, neomutt-hcache-bench.sh
# MIT: Acutest unit test framework, some themes
# Unlicense: Keybase scripts
# Public Domain: pgpewrap.c, mbox.5, some themes
License: GPLv2+ and BSD and MIT and Unlicense and Public Domain

Source: https://github.com/neomutt/neomutt/archive/%{version}/%{name}-%{version}.tar.gz
# Use Fedora/RedHat SSL settings
Patch1: mutt-1.5.23-system_certs.patch
# Use Fedora System SSL settings
Patch2: mutt-1.5.23-ssl_ciphers.patch
# Allow RHEL7 to use an old verion of GPGME
Patch3: neomutt-2019-rhel.patch

Requires: mailcap, urlview

# Build NeoMutt
BuildRequires: cyrus-sasl-devel, gcc, gettext, gettext-devel, gnutls-devel
BuildRequires: gpgme-devel, krb5-devel, libidn2-devel, libzstd-devel
BuildRequires: lmdb-devel, lz4-devel, ncurses-devel, pcre2-devel
BuildRequires: tokyocabinet-devel, zlib-devel

# Generate Documentation
BuildRequires: /usr/bin/xsltproc, docbook-dtds, docbook-style-xsl, perl, lynx

# Autocrypt, Lua and Notmuch don't work in rhel7
%if "0%{?rhel}" != "07"
# Enabled
%bcond_without autocrypt
%bcond_without lua
%bcond_without notmuch
%endif

%{?with_autocrypt:BuildRequires: sqlite-devel}
%{?with_lua:BuildRequires: lua-devel}
%{?with_notmuch:BuildRequires: notmuch-devel}

%description
NeoMutt is a small but very powerful text-based MIME mail client.  NeoMutt is
highly configurable, and is well suited to the mail power user with advanced
features like key bindings, keyboard macros, mail threading, regular expression
searches and a powerful pattern matching language for selecting groups of
messages.

%prep
%setup -q -n %{name}-%{version}
%patch1 -p1 -b .system_certs
%if ! 0%{?rhel}
%patch2 -p1 -b .ssl_ciphers
%endif
%if 0%{?rhel}
%patch3 -p1 -b .rhel
%endif

%build
rpm --showrc

%{configure} \
    SENDMAIL=%{_sbindir}/sendmail \
    ISPELL=%{_bindir}/hunspell \
    --disable-idn --gnutls --gpgme --gss --idn2 --lmdb --lz4 --pcre2 --sasl \
    --tokyocabinet --zlib --zstd --full-doc \
    %{?with_autocrypt: --autocrypt} \
    %{?with_lua:       --lua} \
    %{?with_notmuch:   --notmuch} \

%{make_build}

# remove unique id in manual.html because multilib conflicts
sed -i -r 's/<a id="id[a-z0-9]\+">/<a id="id">/g' docs/manual.html

%install
%{make_install}

grep -C5 "^color" contrib/samples/sample.neomuttrc >> %{buildroot}%{_sysconfdir}/neomuttrc

%if "0%{?rhel}" == "07"
# we like GPG here
cat contrib/samples/gpg.rc >> %{buildroot}%{_sysconfdir}/neomuttrc
rm -rf %{buildroot}%{_docdir}/neomutt/oauth2
rm -rf %{buildroot}%{_docdir}/neomutt/samples/markdown2html.py
mv %{buildroot}%{_docdir}/neomutt %{buildroot}%{_docdir}/neomutt-%{version}
%endif

%find_lang %{name}

%files -f %{name}.lang
%config(noreplace) %{_sysconfdir}/neomuttrc
%{_bindir}/neomutt
%{_libexecdir}/neomutt
%license LICENSE.md
%doc LICENSE.md
%doc AUTHORS.md ChangeLog.md INSTALL.md README.md SECURITY.md
%doc docs/CODE_OF_CONDUCT.md docs/CONTRIBUTING.md
%doc docs/*.txt
%doc docs/*.html
%doc docs/mime.types
%doc contrib/account-command
%doc contrib/colorschemes
%doc contrib/hcache-bench
%doc contrib/keybase
%doc contrib/logo
%doc contrib/lua
%doc contrib/samples
%doc contrib/vim-keys
%if "0%{?rhel}" != "07"
%doc contrib/oauth2
%endif
%{_mandir}/man1/neomutt.*
%{_mandir}/man1/pgpewrap_neomutt.*
%{_mandir}/man1/smime_keys_neomutt.*
%{_mandir}/man5/mbox_neomutt.*
%{_mandir}/man5/mmdf_neomutt.*
%{_mandir}/man5/neomuttrc.*

%changelog
* Thu May 19 2022 Richard Russon <rich@flatcap.org> - NeoMutt-20220519
- Testing
