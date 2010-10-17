# Created by Andre Anjos <andre.dos.anjos@cern.ch> 
# Thu  4 Mar 23:14:52 2010 

.PHONY: clean mrproper shell test

all: clean

clean:
	@find . -name '*.pyc' -print0 | xargs -0 rm -f
	@find . -name '*~' -print0 | xargs -0 rm -f
	$(MAKE) --directory=test clean

mrproper: clean
	$(MAKE) --directory=test mrproper 

test:
	@$(MAKE) --directory=test all 

shell:
	@$(MAKE) --directory=test shell
