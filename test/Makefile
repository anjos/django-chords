# Created by Andre Anjos <andre.dos.anjos@cern.ch> 
# Thu  4 Mar 23:14:52 2010 

# a little make function to ease the administration task
admin=../sw/bin/djm
python=../sw/bin/python

all:
	@if [ ! -e db.sql3 ]; then $(MAKE) admin; fi
	@$(admin) runserver 0.0.0.0:8080

admin:
	@$(admin) syncdb --noinput
	@../sw/bin/start_project.py

shell:
	@$(admin) shell

clean:
	@find . -name '*.pyc' -print0 | xargs -0 rm -f
	@find . -name '*~' -print0 | xargs -0 rm -f

smtp:
	$(python) -m smtpd -n -c DebuggingServer localhost:1025

mrproper: clean
	@rm -f media/songs
	@rm -rf packages
	@rm -f *.sql3
