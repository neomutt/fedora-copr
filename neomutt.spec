%bcond_without debug
%bcond_without imap
%bcond_without pop
%bcond_without smtp
%bcond_without gnutls
%bcond_without gss
%bcond_without sasl
%bcond_without idn
%bcond_without hcache
%bcond_without tokyocabinet
%bcond_with bdb
%bcond_with qdbm
%bcond_with gdbm
%bcond_without gpgme
%bcond_without sidebar
%bcond_without nntp
%bcond_without compress

# Notmuch doesn't exist on rhel, yet
%if 0%{?rhel}
%bcond_with notmuch
%else
%bcond_without notmuch
%endif

%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}
%global _origname mutt
%global _date 20160910

Summary: A text mode mail user agent
Name: neomutt
Version: 1.7.0
Release: %{_date}%{?dist}
Epoch: 5
# The entire source code is GPLv2+ except
# pgpewrap.c setenv.c sha1.c wcwidth.c which are Public Domain
License: GPLv2+ and Public Domain
Group: Applications/Internet
# git snapshot created from https://github.com/neomutt/neomutt
Source: %{_origname}-%{version}.tar.gz
Source1: mutt_ldap_query
Patch1: mutt-1.7.0.neomutt.patch
Patch2: mutt-1.5.18-muttrc.patch
Patch3: mutt-1.5.21-cabundle.patch
Patch4: mutt-1.5.23-system_certs.patch
Patch5: mutt-1.5.23-ssl_ciphers.patch
Patch6: mutt-1.6.0-syncdebug.patch
Url: http://www.neomutt.org/
Requires: mailcap, urlview
# Provides: %{_origname}
Conflicts: %{_origname}
BuildRequires: ncurses-devel, gettext, automake
# manual generation
BuildRequires: /usr/bin/xsltproc, docbook-style-xsl, perl
# html manual -> txt manual conversion (lynx messes up the encoding)
BuildRequires: w3m

%if %{with hcache}
%{?with_tokyocabinet:BuildRequires: tokyocabinet-devel}
%{?with_bdb:BuildRequires: db4-devel}
%{?with_qdbm:BuildRequires: qdbm-devel}
%{?with_gdbm:BuildRequires: gdbm-devel}
%endif

%if %{with imap} || %{with pop} || %{with smtp}
%{?with_gnutls:BuildRequires: gnutls-devel}
%{?with_sasl:BuildRequires: cyrus-sasl-devel}
%endif

%if %{with imap}
%{?with_gss:BuildRequires: krb5-devel}
%endif

%{?with_idn:BuildRequires: libidn-devel}
%{?with_gpgme:BuildRequires: gpgme-devel}
%{?with_notmuch:BuildRequires: notmuch-devel}


%description
Mutt is a small but very powerful text-based MIME mail client.  Mutt
is highly configurable, and is well suited to the mail power user with
advanced features like key bindings, keyboard macros, mail threading,
regular expression searches and a powerful pattern matching language
for selecting groups of messages.


%prep
# unpack; cd
%setup -q -n %{_origname}-%{version}
# disable mutt_dotlock program - disable post-install mutt_dotlock checking
sed -i -r 's|install-exec-hook|my-useless-label|' Makefile.am
%patch1 -p1 -b .neomutt
%patch2 -p1 -b .muttrc
%patch3 -p1 -b .cabundle
%patch4 -p1 -b .system_certs
%patch5 -p1 -b .ssl_ciphers
%patch6 -p1 -b .syncdebug

sed -i -r 's/`$GPGME_CONFIG --libs`/"\0 -lgpg-error"/' configure
# disable mutt_dotlock program - remove support from mutt binary
sed -i -r 's|USE_DOTLOCK|DO_NOT_USE_DOTLOCK|' configure*

install -p -m644 %{SOURCE1} mutt_ldap_query

# Create a release date based on the rpm version
echo -n 'const char *ReleaseDate = ' > reldate.h
echo %{release} | sed -r 's/.*(201[0-9])([0-1][0-9])([0-3][0-9]).*/"\1-\2-\3";/' >> reldate.h

# remove mutt_ssl.c to be sure it won't be used because it violates
# Packaging:CryptoPolicies
# https://fedoraproject.org/wiki/Packaging:CryptoPolicies
rm -f mutt_ssl.c

find . -type f -size 0 -name '*.neomutt' -delete

chmod +x git-version-gen

%build
# do not run ./prepare -V, because it also runs ./configure
autoreconf --install
%configure \
    SENDMAIL=%{_sbindir}/sendmail \
    ISPELL=%{_bindir}/hunspell \
    %{?with_debug:	--enable-debug}\
    %{?with_pop:	--enable-pop}\
    %{?with_imap:	--enable-imap} \
    %{?with_smtp:	--enable-smtp} \
    %{?with_sidebar:	--enable-sidebar} \
    %{?with_notmuch:	--enable-notmuch} \
    %{?with_nntp:	--enable-nntp} \
    %{?with_compress:	--enable-compressed} \
\
    %if %{with hcache}
    --enable-hcache \
    %{!?with_tokyocabinet:	--without-tokyocabinet} \
    %{!?with_gdbm:	--without-gdbm} \
    %{!?with_qdbm:	--without-qdbm} \
    %endif
\
    %if %{with imap} || %{with pop} || %{with smtp}
    %{?with_gnutls:	--with-gnutls} \
    %{?with_sasl:	--with-sasl} \
    %endif
\
    %if %{with imap}
    %{?with_gss:	--with-gss} \
    %endif
\
    %{!?with_idn:	--without-idn} \
    %{?with_gpgme:	--enable-gpgme} \
    --with-docdir=%{_pkgdocdir}

make %{?_smp_mflags}

# remove unique id in manual.html because multilib conflicts
sed -i -r 's/<a id="id[a-z0-9]\+">/<a id="id">/g' doc/manual.html


%install
make install DESTDIR=$RPM_BUILD_ROOT

# we like GPG here
cat contrib/gpg.rc >> \
      $RPM_BUILD_ROOT%{_sysconfdir}/Muttrc

grep -5 "^color" contrib/sample.muttrc >> \
      $RPM_BUILD_ROOT%{_sysconfdir}/Muttrc

cat >> $RPM_BUILD_ROOT%{_sysconfdir}/Muttrc <<\EOF
source %{_sysconfdir}/Muttrc.local
EOF

echo "# Local configuration for Mutt." > \
      $RPM_BUILD_ROOT%{_sysconfdir}/Muttrc.local

# remove unpackaged files from the buildroot
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/*.dist
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/mime.types
# disable mutt_dotlock program - remove the compiled binary
rm -f $RPM_BUILD_ROOT%{_bindir}/mutt_dotlock
rm -f $RPM_BUILD_ROOT%{_bindir}/muttbug
rm -f $RPM_BUILD_ROOT%{_bindir}/flea
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/mutt_dotlock.1*
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/muttbug.1*
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/flea.1*
rm -f $RPM_BUILD_ROOT%{_mandir}/man5/mbox.5*
rm -f $RPM_BUILD_ROOT%{_mandir}/man5/mmdf.5*

rm -rf $RPM_BUILD_ROOT%{_pkgdocdir}/samples
rm -rf $RPM_BUILD_ROOT%{_pkgdocdir}/applying-patches.txt
rm -rf $RPM_BUILD_ROOT%{_pkgdocdir}/devel-notes.txt
rm -rf $RPM_BUILD_ROOT%{_pkgdocdir}/INSTALL
rm -rf $RPM_BUILD_ROOT%{_pkgdocdir}/patch-notes.txt
rm -rf $RPM_BUILD_ROOT%{_pkgdocdir}/PGP-Notes.txt
rm -rf $RPM_BUILD_ROOT%{_pkgdocdir}/TODO

# provide muttrc.local(5): the same as muttrc(5)
ln -sf ./muttrc.5 $RPM_BUILD_ROOT%{_mandir}/man5/muttrc.local.5

# %find_lang %{_origname}
%find_lang %{name}

%files -f %{name}.lang
%config(noreplace) %{_sysconfdir}/Muttrc
%config(noreplace) %{_sysconfdir}/Muttrc.local
%doc COPYRIGHT ChangeLog* GPL NEWS README* UPDATING mutt_ldap_query
%doc contrib/*.rc contrib/sample.* contrib/colors.*
%doc doc/manual.txt doc/smime-notes.txt
%doc doc/*.html
%doc contrib/keybase
%doc contrib/vim-keybindings
%{_bindir}/mutt
%{_bindir}/pgpring
%{_bindir}/pgpewrap
%{_bindir}/smime_keys
%{_mandir}/man1/mutt.*
%{_mandir}/man1/smime_keys.*
%{_mandir}/man1/pgpring.*
%{_mandir}/man1/pgpewrap.*
%{_mandir}/man5/muttrc.*


%changelog
* Sat Sep 10 2016 Richard Russon <rich@flatcap.org> - NeoMutt-20160910
- New Features
  - Colouring Attachments with Regexp
    Guillaume Brogi (guiniol)
  - PGP Encrypt to Self
    Guillaume Brogi (guiniol)
  - Sensible Browser
    Pierre-Elliott Bécue (p-eb)
  - Reply using X-Original-To: header
    Pierre-Elliott Bécue (p-eb)
  - Purge Thread
    Darshit Shah (darnir)
  - Forgotten attachment
    Darshit Shah (darnir)
  - Add sidebar_ordinary color
- Bug Fixes
  - align the nntp code with mutt
    Fabian Groffen (grobian)
  - check for new mail while in pager when idle
    Stefan Assmann (sassmann)
  - Allow the user to interrupt slow IO operations
    Antonio Radici (aradici)
  - keywords: check there are emails to tag
  - fix duplicate saved messages
  - flatten contrib/keybase dir to fix install
  - restore the pager keymapping 'i' to exit
  - proposed fix for clearing labels
  - notmuch: sync vfolder_format to folder_format
- Docs
  - Update List of Features and Authors
- Build
  - fix configure check for fmemopen
  - use fixed version strings
- Upstream
  - Increase date buffer size for $folder_format.
  - Disable ~X when message scoring.
  - Fix pgpring reporting of DSA and Elgamal key lengths.
  - Stub out getdnsdomainname() unless HAVE_GETADDRINFO.
  - Autoconf: always check for getaddrinfo().
  - Add missing sidebar contrib sample files to dist tarball.

* Sat Aug 27 2016 Richard Russon <rich@flatcap.org> - NeoMutt-20160827
- Ported to Mutt-1.7.0

* Fri Aug 26 2016 Richard Russon <rich@flatcap.org> - NeoMutt-20160826
- Build
  - Disable fmemopen until bug is fixed
- Contrib
  - Keybase portability improvements
    Joshua Jordi (JakkinStewart)
- Bug Fixes
  - Fix notmuch crash toggling virtual folders 
  - Fix display of pager index when sidebar toggled

* Sun Aug 21 2016 Richard Russon <rich@flatcap.org> - NeoMutt-20160821
- Contrib
  - Updates to Keybase Support
    Joshua Jordi (JakkinStewart)
- Bug Fixes
  - Fix data-loss when appending a compressed file
  - Don't paint invisible progress bars
  - Revert to Mutt keybindings
  - Don't de-tag emails after labelling them
  - Don't whine if getrandom() fails
    Adam Borowski (kilobyte)
  - Fix display when 'from' field is invalid
- Config
  - Support for $XDG_CONFIG_HOME and $XDG_CONFIG_DIRS
    Marco Hinz (mhinz)
- Docs
  - Fix DocBook validation
  - Document NotMuch queries
- Build
  - More Autoconf improvements
    Darshit Shah (darnir)
  - Create Distribution Tarballs with autogen sources
    Darshit Shah (darnir)

* Mon Aug 08 2016 Richard Russon <rich@flatcap.org> - NeoMutt-20160808
- New Features
  - Timeout Hook - Run a command periodically
  - Multiple fcc - Save multiple copies of outgoing mail
- Contrib
  - Keybase Integration
    Joshua Jordi (JakkinStewart)
- Devel
  - Attached - Prevent missing attachments
    Darshit Shah (darnir)
  - Virtual Unmailboxes - Remove unwanted virtual mailboxes
    Richard Russon (flatcap)
- Bug Fixes
  - Sidebar's inbox occasionally shows zero/wrong value
  - Fix crash opening a second compressed mailbox
- Config
  - Look for /etc/NeoMuttrc and ~/.neomuttrc
- Docs
  - Fix broken links, typos
  - Update project link
  - Fix version string in the manual
- Build
  - Add option to disable fmemopen
  - Install all the READMEs and contribs
  - Big overhaul of the build
    Darshit Shah (darnir)

* Sat Jul 23 2016 Richard Russon <rich@flatcap.org> - NeoMutt-20160723
- New Motto: "Teaching an Old Dog New Tricks"
  - Thanks to Alok Singh
- New Features
  - New Mail Command - Execute a command on receipt of new mail
  - vim-keybindings - Mutt config for vim users
  - LMDB: In-memory header caching database
  - SMIME Encrypt to Self - Secure storage of sensitive email
- Bug Fixes
  - rework mutt_draw_statusline()
  - fix cursor position after sidebar redraw
  - Add sidebar_format flag '%n' to display 'N' on new mail.
  - fix index_format truncation problem
  - Fix compiler warnings due to always true condition
  - Change sidebar next/prev-new to look at buffy->new too.
  - Change the default for sidebar_format to use %n.
  - sidebar "unsorted" order to match Buffy list order.
  - Include ncurses tinfo library if found.
  - Sidebar width problem
  - sidebar crash for non-existent mailbox
  - Temporary compatibility workaround
  - Reset buffy->new for the current mailbox in IMAP.
  - version.sh regression
  - crash when notmuch tries to read a message
  - status line wrapping
- Docs
  - Mass tidy up of the docs
  - Fix xml validation
  - Add missing docs for new features
- Travis
  - New build system:
    https://github.com/neomutt/travis-build
    Now we have central control over what gets built

* Sat Jul 09 2016 Richard Russon <rich@flatcap.org> - NeoMutt-20160709
- Bug-fixes
  - This release was a temporary measure

* Sat Jun 11 2016 Richard Russon <rich@flatcap.org> - NeoMutt-20160611
- Change in behaviour
  - Temporarily disable $sidebar_refresh_time
    Unfortunately, this was causing too many problems.
    It will be fixed and re-enabled as soon as possible.
- Bug Fixes
  - Fix several crashes, on startup, in Keywords
  - Reflow text now works as it should
  - Lots of typos fixed
  - Compress config bug prevented it working
  - Some minor bug-fixes from mutt/default
  - Single quote at line beginning misinterpreted by groff
  - Setting $sidebar_width to more than 128 would cause bad things to happen.
  - Fix alignment in the compose menu.
  - Fix sidebar buffy stats updating on mailbox close.
- Build Changes
  - Sync whitespace to mutt/default
  - Alter ChangeLog date format to simplify Makefiles
  - Use the new notmuch functions that return a status
  - Rename sidebar functions sb_* -> mutt_sb_*

* Mon May 23 2016 Richard Russon <rich@flatcap.org> - NeoMutt-20160523
- New Features:
  - Keywords: Email Label/Keywords/Tagging
  - Compress: Compressed mailboxes support
  - NNTP: Talk to a usenet news server
  - Separate mappings for <enter> and <return>
  - New configure option: --enable-quick-build
  - Various build fixes

* Mon May 02 2016 Richard Russon <rich@flatcap.org> - NeoMutt-20160502
- Update for Mutt-1.6.0
- Bug Fixes:
  - Build for Notmuch works if Sidebar is disabled
  - Sidebar functions work even if the Sidebar is hidden
  - sidebar-next-new, etc, only find *new* mail, as documented
  - Notmuch supports *very* long queries

* Sat Apr 16 2016 Richard Russon <rich@flatcap.org> - NeoMutt-20160416
- Big Bugfix Release
- Bug Fixes:
  - Fix crash caused by sidebar_folder_indent
  - Allow the user to change mailboxes again
  - Correct sidebar's messages counts
  - Only sort the sidebar if we're asked to
  - Fix refresh of pager when toggling the sidebar
  - Compose mode: make messages respect the TITLE_FMT
  - Conditional include if sys/syscall.h
  - Build fix for old compilers
  - Try harder to keep track of the open mailbox
- Changes to Features
  - Allow sidebar_divider_char to be longer
    (it was limited to one character)
  - Ignore case when sorting the sidebar alphabetically
- Other Changes
  - Numerous small tweaks to the docs
  - Lots of minor code tidy-ups
  - Enabling NotMuch now forcibly enables Sidebar
    (it is dependent on it, for now)
  - A couple of bug fixes from mutt/stable

* Mon Apr 04 2016 Richard Russon <rich@flatcap.org> - NeoMutt-20160404
- Update for Mutt-1.6.0
- No other changes in this release

* Mon Mar 28 2016 Richard Russon <rich@flatcap.org> - NeoMutt-20160328
- New Features
  - skip-quoted          - skip quoted text
  - limit-current-thread - limit index view to current thread
- Sidebar Intro - A Gentle Introduction to the Sidebar (with pictures).

* Sun Mar 20 2016 Richard Russon <rich@flatcap.org> - NeoMutt-20160320
- Numerous small bugfixes
- TravisCI integration

* Thu Mar 17 2016 Richard Russon <rich@flatcap.org> - NeoMutt-20160317
- New Features
  - notmuch - email search support
  - ifdef   - improvements

* Mon Mar 07 2016 Richard Russon <rich@flatcap.org> - NeoMutt-20160307
- First NeoMutt release
- List of Features:
  - bug-fixes    - various bug fixes
  - cond-date    - use rules to choose date format
  - fmemopen     - use memory buffers instead of files
  - ifdef        - conditional config options
  - index-color  - theme the email index
  - initials     - expando for author's initials
  - nested-if    - allow deeply nested conditions
  - progress     - show a visual progress bar
  - quasi-delete - mark emails to be hidden
  - sidebar      - overview of mailboxes
  - status-color - theming the status bar
  - tls-sni      - negotiate for a certificate
  - trash        - move 'deleted' emails to a trash bin

