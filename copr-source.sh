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


rm -fr rpmbuild
rpmbuild_tree

cp ../mutt-1.7.0.tar.gz rpmbuild/SOURCES
cp *.patch              rpmbuild/SOURCES
cp mutt_ldap_query      rpmbuild/SOURCES

rpmbuild -bs --target=noarch --define=_topdir\ /home/mutt/release/copr/rpmbuild neomutt.spec

cp rpmbuild/SRPMS/neomutt-1.7.0-20160910.fc24.src.rpm .

rm -fr rpmbuild

