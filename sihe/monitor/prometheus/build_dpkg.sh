#!/bin/bash
rm *.deb

if [ $# = 2 ]
then
    GIT_COMMIT=$1
    DATE=$2
    GIT_TAG=0.2.0
elif [ $# = 3 ]
then
    GIT_COMMIT=$1
    DATE=$2
    GIT_TAG=$3
else
    git submodule init
    git submodule update
    GIT_COMMIT=`git rev-parse --short HEAD`
    DATE=`date '+%Y%m%d_%H%M%S'`
    GIT_TAG=`git describe --tags --long`
fi

DATE=`date '+%Y%m%d_%H%M%S'`
FILENAME=falcon_agent-${GIT_TAG}-${GIT_COMMIT}-${DATE}.deb

echo -e "
api= falcon-api.sihe6.com
tag: cluster=detection-machine
endpoint: dm/mac
date: $DATE
version: ${GIT_TAG}-${GIT_COMMIT}-${DATE}
" > deb/home/work/version.txt

# deb version
: > deb/DEBIAN/control
echo "Package: open-falcon-agent" >> deb/DEBIAN/control
echo "Version: $GIT_TAG" >> deb/DEBIAN/control
echo "Section:" >> deb/DEBIAN/control
echo "Priority: optional" >> deb/DEBIAN/control
echo "Depends: golang-1.10-go,python,python-pip,wget,vim" >> deb/DEBIAN/control
echo "Architecture: amd64" >> deb/DEBIAN/control
echo "Installed-Size: 16948" >> deb/DEBIAN/control
echo "Maintainer: dai.yi" >> deb/DEBIAN/control
echo "Provides: hypereal" >> deb/DEBIAN/control
echo "Description: open-falcon-agent install" >> deb/DEBIAN/control

chmod -R 755 deb
chmod -R 755 deb/DEBIAN
dpkg-deb -b deb $FILENAME
