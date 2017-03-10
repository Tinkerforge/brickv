#!/bin/sh

if [ $# -ne 3 ]; then
    exit 1
fi

echostderr() { echo "$@" 1>&2; }

case "$1" in
  "brickv")
    /usr/bin/dpkg -i $3;

    if [ $? = 0 ]; then
      exit 0
    else
      exit 1
    fi

    ;;

  "c")
    /usr/bin/unzip -q -d $2/bindings/c $3 && \
    cd $2/bindings/c/source && \
    /usr/bin/make && \
    prefix=/usr /usr/bin/make install

    ;;

  "csharp")
    /usr/bin/unzip -q -d $2/bindings/csharp $3 && \
    cd $2/bindings/csharp && \
    /bin/cp Tinkerforge.dll /usr/lib

    ;;

  "delphi")
    /usr/bin/unzip -q -d $2/bindings/delphi $3 && \
    cd $2/bindings/delphi/source && \
    export FPCDIR=/usr/lib/fpc/default && \
    /usr/bin/fpcmake && \
    /usr/bin/make && \
    /usr/bin/make install && \
    /usr/bin/make clean

    ;;

  "java")
    /usr/bin/unzip -q -d $2/bindings/java $3

    ;;

  "javascript")
    /usr/bin/unzip -q -d $2/bindings/javascript $3

    ;;

  "matlab")
    /usr/bin/unzip -q -d $2/bindings/matlab $3

    ;;

  "perl")
    /usr/bin/unzip -q -d $2/bindings/perl $3 && \
    cd $2/bindings/perl/source && \
    /usr/bin/perl Makefile.PL && \
    /usr/bin/make all && \
    /usr/bin/make test && \
    /usr/bin/make install

    ;;

  "php")
    /usr/bin/unzip -q -d $2/bindings/php $3 && \
    cd $2/bindings/php && \
    /usr/bin/pear install Tinkerforge.tgz

    ;;

  "python")
    /usr/bin/unzip -q -d $2/bindings/python $3 && \
    cd $2/bindings/python/source && \
    /usr/bin/python2 setup.py install; \
    /usr/bin/python3 setup.py install

    ;;

  "ruby")
    /usr/bin/unzip -q -d $2/bindings/ruby $3 && \
    cd $2/bindings/ruby && \
    /usr/bin/gem install tinkerforge.gem

    ;;

  "shell")
    /usr/bin/unzip -q -d $2/bindings/shell $3 && \
    cd $2/bindings/shell && \
    /bin/cp tinkerforge /usr/local/bin && \
    /bin/cp tinkerforge-bash-completion.sh /etc/bash_completion.d

    ;;

  "vbnet")
    /usr/bin/unzip -q -d $2/bindings/vbnet $3

    ;;
esac

exit 0
