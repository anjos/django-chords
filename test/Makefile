# Created by Andre Anjos <andre.dos.anjos@cern.ch> 
# Thu  4 Mar 23:14:52 2010 

# a little make function to ease the administration task
admin=sw/bin/djm
python=python
project=../chords

# a little hack for the messaging infrastructure
LANGUAGES=en pt_BR fr es
MAKE_MESSAGE=../test/$(admin) makemessages --all --extension=html,py,txt
COMPILE_MESSAGE=../test/$(admin) compilemessages

.PHONY: all generate_bootstrap bootstrap upgrade strings compile start shell smtp clean mrproper

all:
	@if [ ! -e db.sql3 ]; then $(MAKE) start; fi
	@$(admin) runserver 0.0.0.0:8080

generate_bootstrap:
	$(MAKE) --directory=installer generate

bootstrap: generate_bootstrap
	@installer/bootstrap.py --quiet --python=$(python) sw

upgrade:
	@installer/bootstrap.py --quiet --python=$(python) --upgrade sw

strings: bootstrap
	@cd $(project); for l in $(LANGUAGES); do if [ ! -d locale/$$l ]; then mkdir -pv locale/$$l; fi; done;
	@cd $(project) && $(MAKE_MESSAGE);

compile: bootstrap
	@cd $(project) && $(COMPILE_MESSAGE);

languages: strings compile

start: bootstrap
	@$(admin) syncdb --noinput
	@sw/bin/start_project.py

shell:
	@$(admin) shell

smtp:
	sw/bin/python -m smtpd -n -c DebuggingServer localhost:1025

clean:
	@find . -name '*.pyc' -print0 | xargs -0 rm -f
	@find . -name '*~' -print0 | xargs -0 rm -f
	@rm -rf pip-log.txt *.egg-info
	$(MAKE) --directory=installer clean

mrproper: clean
	@rm -rf sw 
	@rm -f media/songs
	@rm -rf packages
	@rm -f *.sql3
	@find . -name '*.pyc' -or -name '*.pyo' -print0 | xargs -0 rm -vf
	$(MAKE) --directory=installer mrproper 
