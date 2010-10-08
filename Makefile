# Dear emacs, this is -*- Makefile -*-
# Created by Andre Anjos <Andre.dos.Anjos@gmail.com>, 20-Mar-2007

# These are variables you can configure for your application
python=python2.5
LANGUAGES=en pt_BR fr es

# These are helpers
admin=sw/bin/django-admin.py
project=chords
MAKE_MESSAGE=$(admin) makemessages --all --extension=html,py,txt
COMPILE_MESSAGE=$(admin) compilemessages

.PHONY: clean mrproper generate_bootstrap bootstrap upgrade strings compile languages test

all: clean bootstrap strings compile test

generate_bootstrap:
	$(MAKE) --directory=installer generate

bootstrap: generate_bootstrap
	@./installer/bootstrap.py --quiet --python=$(python) sw

upgrade:
	@./installer/bootstrap.py --quiet --python=$(python) --upgrade sw

clean: 	
	@find . -name '*~' -print0 | xargs -0 rm -vf 
	@rm -rf pip-log.txt *.egg-info
	$(MAKE) --directory=installer clean
	$(MAKE) --directory=test clean

test:
	$(MAKE) --directory=test all

mrproper: clean
	@rm -rf sw 
	$(MAKE) --directory=installer mrproper 
	$(MAKE) --directory=test mrproper
	@find . -name '*.pyc' -or -name '*.pyo' -print0 | xargs -0 rm -vf

strings: bootstrap
	@cd $(project); for l in $(LANGUAGES); do if [ ! -d locale/$$l ]; then mkdir -pv locale/$$l; fi; done;
	@cd $(project) && ../$(MAKE_MESSAGE);

compile: bootstrap
	@cd $(project) && ../$(COMPILE_MESSAGE);

languages: strings compile
