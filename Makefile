# Dear emacs, this is -*- Makefile -*-
# Created by Andre Anjos <Andre.dos.Anjos@gmail.com>, 20-Mar-2007

.PHONY: clean mrproper 

all: clean

clean: 	
	$(MAKE) --directory=test clean
	@find . -name '*~' -print0 | xargs -0 rm -vf 
	@rm -rf *.egg-info

mrproper: clean
	$(MAKE) --directory=test mrproper
	@find . -name '*.pyc' -or -name '*.pyo' -print0 | xargs -0 rm -vf
