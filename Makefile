docker-build:
	wharfer build -t johanna-goetz-winerli-20 .


DEFAULT_MAPPINGS=/nfs/students/niklas-baumert/input
DEFAULT_DATABASES=/nfs/students/johanna-goetz/winerli-20/databases/precalculated

# make docker-run INPUT_ALIASMAP=/nfs/students/johanna-goetz/winerli-20/test/input OUTPUT_ALIASMAP=`pwd`/output INPUT_RECOGNITION=`pwd`/input OUTPUT_RECOGNITION=`pwd`/output LOG=`pwd`/log
docker-run:
	wharfer run -v $(INPUT_ALIASMAP):/input_aliasmap -v $(INPUT_RECOGNITION):/input_recognition -v $(OUTPUT_ALIASMAP):/output_aliasmap -v $(OUTPUT_RECOGNITION):/output_recognition -v $(if $(DATABASES),$(DATABASES),$(DEFAULT_DATABASES)):/databases -v $(if $(MAPPINGS),$(MAPPINGS),$(DEFAULT_MAPPINGS)):/mappings -v $(LOG):/log -v /nfs/students/johanna-goetz/winerli-20/test/input:/test_input -v /nfs/students/johanna-goetz/winerli-20/test/output:/test_output -v /nfs/students/johanna-goetz/winerli-20/test/databases:/test_databases -v /nfs/students/johanna-goetz/winerli-20/evaluation:/evaluation -v $(PWD)/env:/env -it --name johanna-goetz-winerli-20 johanna-goetz-winerli-20

check-input-aliasmap-r:
	@echo "Checking if /input_aliasmap/ is readable"
	[ -d "/input_aliasmap/" ] && [ -r "/input_aliasmap/" ]

check-input-recognition-r:
	@echo "Checking if /input_recognition/ is readable"
	[ -d "/input_recognition/" ] && [ -r "/input_recognition/" ]

check-output-aliasmap-rw:
	@echo "Checking if /output_aliasmap/ is writable"
	[ -d "/output_aliasmap/" ] && [ -w "/output_aliasmap/" ]

check-output-recognition-rw:
	@echo "Checking if /output_recognition/ is writable"
	[ -d "/output_recognition/" ] && [ -w "/output_recognition/" ]

check-databases-r:
	@echo "Checking if /database/ is writable"
	[ -d "/databases/" ] && [ -r "/databases/" ]

check-log-rw:
	@echo "Checking if /log/ is writable"
	[ -d "/log/" ] && [ -w "/log/" ]

check-evaluation-rw:
	@echo "Checking if /evaluation/ is writable"
	[ -d "/evaluation/" ] && [ -w "/evaluation/" ]

check-mappings-r:
	@echo "Checking if /mappings/ is readable"
	[ -d "/mappings/" ] && [ -r "/mappings/" ]

check-test-databases-r:
	@echo "Checking if /test_databases/ is readable"
	[ -d "/test_databases/" ] && [ -r "/test_databases/" ]

check-test-input-r:
	@echo "Checking if /test_input/ is readable"
	[ -d "/test_input/" ] && [ -r "/test_input/" ]

check-test-output-rw:
	@echo "Checking if /test_output/ is writable"
	[ -d "/test_output/" ] && [ -w "/test_output/" ]


all: aliasmap recognize-and-merge

aliasmap: check-log-rw check-output-aliasmap-rw check-input-aliasmap-r
	bash -c "source ./env/aliasmap.env && python3 create_aliasmap_multi.py"

recognize: check-log-rw check-output-recognition-rw check-input-recognition-r check-databases-r
	bash -c "source ./env/recognize-and-merge.env && python3 entity_recognition.py"

merge: check-log-rw check-output-recognition-rw check-mappings-r
	bash -c "source ./env/merger.env && python3 merger.py"

recognize-and-merge: check-log-rw check-output-recognition-rw check-input-recognition-r check-databases-r check-mappings-r
	bash -c "source ./env/recognize-and-merge.env && python3 entity_recognition.py && python3 merger.py"

evaluation: check-log-rw check-evaluation-rw
	bash -c "source ./env/evaluation.env && python3 evaluation.py"


test-all: test-aliasmap test-recognize

test-aliasmap: test-aliasmap-1 test-aliasmap-2

test-aliasmap-1: check-log-rw check-test-input-r check-test-output-rw
	bash -c "source ./env/test-aliasmap-1.env && python3 create_aliasmap_multi.py"

test-aliasmap-2: check-log-rw check-test-output-rw
	pytest -p no:cacheprovider test_wikiparsing.py test_parse_info.py test_aliasmap.py -vv

test-recognize: test-recognize-1 test-recognize-2 test-recognize-3 test-recognize-4 test-recognize-5 test-recognize-6

test-recognize-1: check-log-rw check-test-input-r check-test-output-rw check-test-databases-r
	bash -c "source ./env/test-recognize-1.env && python3 entity_recognition.py"

test-recognize-2: check-log-rw check-test-input-r check-test-output-rw check-test-databases-r
	bash -c "source ./env/test-recognize-2.env && python3 entity_recognition.py"

test-recognize-3: check-log-rw check-test-input-r check-test-output-rw check-test-databases-r
	bash -c "source ./env/test-recognize-3.env && python3 entity_recognition.py"

test-recognize-4: check-log-rw check-test-input-r check-test-output-rw check-test-databases-r
	bash -c "source ./env/test-recognize-4.env && python3 entity_recognition.py"

test-recognize-5: check-log-rw check-test-input-r check-test-output-rw check-test-databases-r
	bash -c "source ./env/test-recognize-5.env && python3 entity_recognition.py"

test-recognize-6: check-log-rw check-test-input-r
	pytest -p no:cacheprovider test_wikiparsing.py test_cleanup.py test_recognizer.py -vv
