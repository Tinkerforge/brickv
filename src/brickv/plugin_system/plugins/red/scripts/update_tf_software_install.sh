#!/bin/sh

if [ $# -ne 3 ]; then
    exit 1
fi

echostderr() { echo "$@" 1>&2; }

case "$1" in
  "brickv")
    /usr/bin/dpkg -i $3 &> /dev/null;

    if [ $? = 0 ]; then
      exit 0
    else
      exit 1
    fi

    ;;

  "c")
    /usr/bin/unzip -q -d $2/bindings/c $3 &> /dev/null && \
    cd $2/bindings/c/source &> /dev/null && \
    /usr/bin/make &> /dev/null && \
    prefix=/usr /usr/bin/make install &> /dev/null

    ;;

  "csharp")
    /usr/bin/unzip -q -d $2/bindings/csharp $3 &> /dev/null && \
    cd $2/bindings/csharp &> /dev/null && \
    /bin/cp Tinkerforge.dll /usr/lib &> /dev/null

    ;;

  "delphi")
    /usr/bin/unzip -q -d $2/bindings/delphi $3 &> /dev/null && \
    cd $2/bindings/delphi/source &> /dev/null && \
    export FPCDIR=/usr/lib/fpc/default &> /dev/null && \
    /usr/bin/fpcmake &> /dev/null&& \
    /usr/bin/make &> /dev/null && \
    /usr/bin/make install &> /dev/null&& \
    /usr/bin/make clean &> /dev/null

    ;;

  "java")
    /usr/bin/unzip -q -d $2/bindings/java $3 &> /dev/null

    ;;

  "javascript")
    /usr/bin/unzip -q -d $2/bindings/javascript $3 &> /dev/null && \
    cd $2/bindings/javascript/nodejs &> /dev/null && \
    $(/usr/bin/which npm) uninstall -g tinkerforge &> /dev/null; \
    $(/usr/bin/which npm) install -g tinkerforge.tgz &> /dev/null

    ;;

  "matlab")
    /usr/bin/unzip -q -d $2/bindings/matlab $3 &> /dev/null

    ;;

  "perl")
    /usr/bin/unzip -q -d $2/bindings/perl $3 &> /dev/null && \
    cd $2/bindings/perl/source &> /dev/null && \
    /usr/bin/perl Makefile.PL &> /dev/null && \
    /usr/bin/make all &> /dev/null && \
    /usr/bin/make test &> /dev/null && \
    /usr/bin/make install &> /dev/null

    ;;

  "php")
    /usr/bin/unzip -q -d $2/bindings/php $3 &> /dev/null && \
    cd $2/bindings/php &> /dev/null && \
    /usr/bin/pear install Tinkerforge.tgz &> /dev/null

    ;;

  "python")
    /usr/bin/unzip -q -d $2/bindings/python $3 &> /dev/null && \
    cd $2/bindings/python/source &> /dev/null && \
    /usr/bin/python2 setup.py install &> /dev/null; \
    /usr/bin/python3 setup.py install &> /dev/null

    ;;

  "ruby")
    /usr/bin/unzip -q -d $2/bindings/ruby $3 &> /dev/null && \
    cd $2/bindings/ruby &> /dev/null && \
    /usr/bin/gem install tinkerforge.gem &> /dev/null

    ;;

  "shell")
    /usr/bin/unzip -q -d $2/bindings/shell $3 &> /dev/null && \
    cd $2/bindings/shell &> /dev/null && \
    /bin/cp tinkerforge /usr/local/bin &> /dev/null && \
    /bin/cp tinkerforge-bash-completion.sh /etc/bash_completion.d &> /dev/null

    ;;

  "vbnet")
    /usr/bin/unzip -q -d $2/bindings/vbnet $3 &> /dev/null

    ;;
esac

exit 0
