#!/bin/sh

if [ $# -ne 3 ]; then
    exit 1
fi

echostderr() { echo "$@" 1>&2; }

case "$1" in
  "brickv")
    $(/usr/bin/which apt-get) purge brickv -y &> /dev/null; \
    $(/usr/bin/which dpkg) -i $3 &> /dev/null

    if [ $? = 0 ]; then
      exit 0
    else
      exit 1
    fi

    ;;

  "c")
    $(/usr/bin/which unzip) -q -d $2/bindings/c $3 &> /dev/null && \
    cd $2/bindings/c/source &> /dev/null && \
    $(/usr/bin/which rm) -f /usr/lib/libtinkerforge.so &> /dev/null; \
    $(/usr/bin/which make) &> /dev/null && \
    $(/usr/bin/which make) prefix=/usr install &> /dev/null && \
    $(/usr/bin/which make) clean &> /dev/null

    if [ $? = 0 ]; then
      exit 0
    else
      exit 1
    fi

    ;;

  "csharp")
    $(/usr/bin/which unzip) -q -d $2/bindings/csharp $3 &> /dev/null && \
    cd $2/bindings/csharp &> /dev/null && \
    $(/usr/bin/which rm) -f /usr/lib/Tinkerforge.dll &> /dev/null; \
    $(/usr/bin/which cp) -f Tinkerforge.dll /usr/lib &> /dev/null

    if [ $? = 0 ]; then
      exit 0
    else
      exit 1
    fi

    ;;

  "delphi")
    $(/usr/bin/which unzip) -q -d $2/bindings/delphi $3 &> /dev/null && \
    cd $2/bindings/delphi/source &> /dev/null && \
    $(/usr/bin/which rm) -rf /usr/lib/fpc/default/units/arm-linux/tinkerforge &> /dev/null; \
    $(/usr/bin/which fpcmake) &> /dev/null && \
    $(/usr/bin/which make) FPCDIR=/usr/lib/fpc/default &> /dev/null && \
    $(/usr/bin/which make) FPCDIR=/usr/lib/fpc/default install &> /dev/null && \
    $(/usr/bin/which make) clean &> /dev/null

    if [ $? = 0 ]; then
      exit 0
    else
      exit 1
    fi

    ;;

  "java")
    $(/usr/bin/which unzip) -q -d $2/bindings/java $3 &> /dev/null

    if [ $? = 0 ]; then
      exit 0
    else
      exit 1
    fi

    ;;

  "javascript")
    $(/usr/bin/which unzip) -q -d $2/bindings/javascript $3 &> /dev/null && \
    cd $2/bindings/javascript/nodejs &> /dev/null && \
    $(/usr/bin/which npm) uninstall -g tinkerforge &> /dev/null; \
    $(/usr/bin/which npm) install -g ./tinkerforge.tgz &> /dev/null

    if [ $? = 0 ]; then
      exit 0
    else
      exit 1
    fi

    ;;

  "matlab")
    $(/usr/bin/which unzip) -q -d $2/bindings/matlab $3 &> /dev/null

    if [ $? = 0 ]; then
      exit 0
    else
      exit 1
    fi

    ;;

  "perl")
    $(/usr/bin/which unzip) -q -d $2/bindings/perl $3 &> /dev/null && \
    cd $2/bindings/perl/source &> /dev/null && \
    $(/usr/bin/which cpanm) -f --uninstall Tinkerforge &> /dev/null; \
    $(/usr/bin/which perl) Makefile.PL &> /dev/null && \
    $(/usr/bin/which make) all &> /dev/null && \
    $(/usr/bin/which make) install &> /dev/null

    if [ $? = 0 ]; then
      exit 0
    else
      exit 1
    fi

    ;;

  "php")
    $(/usr/bin/which unzip) -q -d $2/bindings/php $3 &> /dev/null && \
    cd $2/bindings/php &> /dev/null && \
    $(/usr/bin/which pear) uninstall __uri/Tinkerforge &> /dev/null; \
    $(/usr/bin/which pear) install ./Tinkerforge.tgz &> /dev/null

    if [ $? = 0 ]; then
      exit 0
    else
      exit 1
    fi

    ;;

  "python")
    # Some python bindings release use "setuptools"(older) and some
    # "distutils"(newer) to install the bindings. If the currently installed
    # Python bindings were installed with "setuptools" then it is installed as
    # ".egg" file.
    #
    # After an update if the newer bindings were installed with "distutils" then
    # it will be installed as an ".egg-info".
    #
    # The ".egg" file seem to have priority while resolving for Python modules.
    # As a result in this case the older modules will be loaded even after the
    # update.
    #
    # To fix this problem first "pip uninstall" is used before updating the
    # bindings.
    $(/usr/bin/which unzip) -q -d $2/bindings/python $3 &> /dev/null && \
    cd $2/bindings/python/source &> /dev/null && \
    $(/usr/bin/which pip) uninstall tinkerforge -y &> /dev/null; \
    $(/usr/bin/which pip3) uninstall tinkerforge -y &> /dev/null; \
    $(/usr/bin/which python2) setup.py install &> /dev/null && \
    $(/usr/bin/which python3) setup.py install &> /dev/null

    if [ $? = 0 ]; then
      exit 0
    else
      exit 1
    fi

    ;;

  "ruby")
    $(/usr/bin/which unzip) -q -d $2/bindings/ruby $3 &> /dev/null && \
    cd $2/bindings/ruby &> /dev/null && \
    $(/usr/bin/which gem) uninstall tinkerforge &> /dev/null; \
    $(/usr/bin/which gem) install --local --no-document ./tinkerforge.gem &> /dev/null

    if [ $? = 0 ]; then
      exit 0
    else
      exit 1
    fi

    ;;

  "shell")
    $(/usr/bin/which unzip) -q -d $2/bindings/shell $3 &> /dev/null && \
    cd $2/bindings/shell &> /dev/null && \
    $(/usr/bin/which rm) -f /usr/local/bin/tinkerforge &> /dev/null; \
    $(/usr/bin/which rm) -f /etc/bash_completion.d/tinkerforge-bash-completion.sh &> /dev/null; \
    $(/usr/bin/which cp) -f tinkerforge /usr/local/bin &> /dev/null && \
    $(/usr/bin/which cp) -f tinkerforge-bash-completion.sh /etc/bash_completion.d &> /dev/null

    if [ $? = 0 ]; then
      exit 0
    else
      exit 1
    fi

    ;;

  "vbnet")
    $(/usr/bin/which unzip) -q -d $2/bindings/vbnet $3 &> /dev/null

    if [ $? = 0 ]; then
      exit 0
    else
      exit 1
    fi

    ;;
esac

exit 0
