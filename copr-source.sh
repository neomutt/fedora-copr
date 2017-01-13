#!/bin/bash

set -o errexit	# set -e
set -o nounset	# set -u

rpmbuild_tree()
{
	mkdir -p rpmbuild/BUILD
	mkdir -p rpmbuild/BUILDROOT
	mkdir -p rpmbuild/RPMS/athlon
	mkdir -p rpmbuild/RPMS/i386
	mkdir -p rpmbuild/RPMS/i586
	mkdir -p rpmbuild/RPMS/i686
	mkdir -p rpmbuild/RPMS/noarch
	mkdir -p rpmbuild/RPMS/x86_64
	mkdir -p rpmbuild/SOURCES
	mkdir -p rpmbuild/SPECS
	mkdir -p rpmbuild/SRPMS
}


SPEC="neomutt.spec"
MUTT="1.7.2"
DATE="$(sed -n '/^*/{s/.*-//p;q}' "$SPEC")"
OS="fc25"
HERE=$(pwd)

rm -fr rpmbuild
rpmbuild_tree

cp ../mutt-${MUTT}.tar.gz rpmbuild/SOURCES
cp *.patch                rpmbuild/SOURCES
cp mutt_ldap_query        rpmbuild/SOURCES

rpmbuild -bs --target=noarch --define=_topdir\ $HERE/rpmbuild "$SPEC"

cp rpmbuild/SRPMS/neomutt-${MUTT}-${DATE}.${OS}.src.rpm .

rm -fr rpmbuild

