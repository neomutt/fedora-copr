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


MUTT="1.7.0"
DATE="$(sed -n '/^*/{s/.*-//p;q}' neomutt.spec)"
OS="fc24"
HERE=$(pwd)

rm -fr rpmbuild
rpmbuild_tree

rpmbuild --rebuild --define=_topdir\ $HERE/rpmbuild neomutt-${MUTT}-${DATE}.${OS}.src.rpm

cp rpmbuild/RPMS/x86_64/* .

rm -fr rpmbuild

