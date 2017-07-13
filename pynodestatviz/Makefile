PYTHON=python

PROJECT=pynodestatviz

VERSION=0.2.1

.PHONY:	rpm spec

all-local:	setup.py
	$(PYTHON) setup.py build

clean:	setup.py clean-dist
	$(PYTHON) setup.py clean
	-rm -rf build
	-rm -f MANIFEST
	-rm -f setup.py
	-rm -f stdeb.cfg
	-find . -name "*.pyc" -delete

clean-dist:
	-rm -rf dist
	-rm -rf deb_dist

install:	setup.py
	$(PYTHON) setup.py install

dist:	setup.py
	$(PYTHON) setup.py sdist

bdist:	setup.py
	$(PYTHON) setup.py bdist

distclean:	clean

DEBIAN_VERSION=$(shell if [ -f  /etc/debian_version ]; \
                       then \
                       cat /etc/debian_version | awk -F/ '{print $$1}';\
                       fi)

edit = sed                              \
        -e 's|@VERSION[@]|$(VERSION)|g' \
        -e 's|@DEBIAN_VERSION[@]|$(DEBIAN_VERSION)|g'

setup.py:	setup.py.in
	if test -f $@; then chmod u+w $@; fi
	$(edit) $< > $@
	chmod g-w,u-w $@

stdeb.cfg: stdeb.cfg.in
	if test -f $@; then chmod u+w $@; fi
	$(edit) $< > $@
	chmod g-w,u-w $@

rpm:	setup.py 
	$(PYTHON) setup.py bdist_rpm  \
   --vendor "Adjacent Link LLC"  \
   --requires "tkinter python-pmw python-lxml"

deb:	setup.py stdeb.cfg
	$(PYTHON) setup.py --command-packages=stdeb.command bdist_deb
