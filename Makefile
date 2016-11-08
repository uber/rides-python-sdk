.PHONY: test
test:
	@py.test -s tests/

.PHONY: clean
clean:
	@find . -type f -name '*.pyc' -exec rm {} ';'

.PHONY: bootstrap
bootstrap:
	@pip install -r requirements.txt
	@pip install -e .
