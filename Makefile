DOCKER:=$(shell which podman || which wharfer || which docker)

help:
	@echo "Available targets:"
	@echo "aliasmap	--	Build the aliasmap from a wiki dump. Creates 4 files: aliasmap.db, links_db.db, page_categories_db.db, infobox_category.tsv. Run the 'help-aliasmap' for further information."
	@echo "recognize-and-merge	--	Perform the recognition process on a wiki dump or a text file. Creates 2 files: a docsfile and a wordsfile. Run the 'help-recognize-and-merge' for further information."
	@echo "evaluation	--	Run the evaluaion. Creates 1 file containing the results as a markdown table. Run the 'help-evaluation' for further information."
	@echo "test-aliasmap	--	Run the aliasmap test cases"
	@echo "test-recognize	--	Run the recognizer test cases"
	@echo "test-all	--	Run all test cases"
	@echo "Note:"
	@echo "If you want to use different files than the default ones, you need to edit the files in the /env directory. Check the readme file for the definition of each variable."

help-aliasmap:
	@echo "Use the 'aliasmap' target to build the aliasmap:"
	@echo "This target builds the aliasmap from a wiki dump file. It creates 4 files in the output directory:"
	@echo "	aliasmap.db: This file contains synonym data to be used the recognition."
	@echo "	links_db.db: This file contains data about which wiki page links to which other page."
	@echo "	page_categories_db.db: This file contains data about which wiki page belongs to which categories."
	@echo "	infobox_category.tsv: This file contains data about the categories of the infoboxes that appear on a wiki page."
	@echo "Depending on your machine and size of your wiki dump, this may take up several hours. For a full wiki dump it may take 24 hours or longer and will produce files with a total size of approx. 42 GB but."
	@echo "If you want to use different files than the default ones, you need to edit the files in the /env directory. Check the readme file for the definition of each variable."

help-recognize-and-merge:
	@echo "Use the 'recognize-and-merge' target to perform the entity recognition/linking and merge the output files:"
	@echo "This target performs the entity recognition/linking on a wiki dump or text file."
	@echo "It requires the 4 files created by the 'aliasmap' target. If you want to run this step on a wiki dump, it's best to build the aliasmap and related files from the same dump."
	@echo "It creates 2 files in the output directory:"
	@echo "	The docsfile (the name contains the current date): This file contains all of the sentences, one sentence per line with the corresponding number."
	@echo "	The wordsfile (the name contains the current date): This file contains all of the tokens with the document they belong to and their assigned entities and the calculated scores, one token per line."
	@echo "Depending on your machine and size of your wiki dump or text file and your chosen parameters, this may take up several hours."
	@echo "If you want to use different files than the default ones, you need to edit the files in the /env directory. Check the readme file for the definition of each variable."

help-evaluation:
	@echo "Use the 'evaluation' to perform the evaluation:"
	@echo "This target performs the evaluation of the entity recognition/linking process."
	@echo "It creates 1 file in the evaluation/output directory:"
	@echo "	evaluation_result_table.txt: This file contains the evaluation results as a markdown table."
	@echo "Depending on your machine, this may take up several hours because lots of combinations of input parameters are run."


docker-build:
	${DOCKER} build -t johanna-goetz-winerli-20 .


DEFAULT_MAPPINGS=/nfs/students/niklas-baumert/input
DEFAULT_DATABASES=/nfs/students/johanna-goetz/winerli-20/databases/precalculated
DEFAULT_EVALUATION=/nfs/students/johanna-goetz/winerli-20/evaluation

# make docker-run INPUT_ALIASMAP=`pwd`/input OUTPUT_ALIASMAP=`pwd`/databases INPUT_RECOGNITION=`pwd`/input OUTPUT_RECOGNITION=`pwd`/output DATABASES=`pwd`/databases MAPPINGS=`pwd`/mappings EVALUATION=`pwd`/evaluation
docker-run:
	${DOCKER} run --rm -v $(INPUT_ALIASMAP):/input_aliasmap -v $(INPUT_RECOGNITION):/input_recognition -v $(OUTPUT_ALIASMAP):/output_aliasmap -v $(OUTPUT_RECOGNITION):/output_recognition -v $(if $(DATABASES),$(DATABASES),$(DEFAULT_DATABASES)):/databases -v $(if $(MAPPINGS),$(MAPPINGS),$(DEFAULT_MAPPINGS)):/mappings -v $(if $(LOG),$(LOG),$(PWD)/log):/log -v $(PWD)/test/input:/test_input -v $(PWD)/test/output:/test_output -v $(PWD)/test/databases:/test_databases -v $(if $(EVALUATION),$(EVALUATION),$(DEFAULT_EVALUATION)):/evaluation -v $(PWD)/env:/env -it --name johanna-goetz-winerli-20 johanna-goetz-winerli-20

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
	bash -c "source ./env/aliasmap.env && python3 create_aliasmap_multi.py > /log/winerli20-aliasmap-stdout.log 2> /log/winerli20-aliasmap-stderr.log"

recognize: check-log-rw check-output-recognition-rw check-input-recognition-r check-databases-r
	bash -c "source ./env/recognize-and-merge.env && python3 entity_recognition.py > /log/winerli20-recognize-stdout.log 2> /log/winerli20-recognize-stderr.log"

merge: check-log-rw check-output-recognition-rw check-mappings-r
	bash -c "source ./env/merger.env && python3 merger.py > /log/winerli20-merge-stdout.log 2> /log/winerli20-merge-stderr.log"

recognize-and-merge: check-log-rw check-output-recognition-rw check-input-recognition-r check-databases-r check-mappings-r
	bash -c "source ./env/recognize-and-merge.env && python3 entity_recognition.py > /log/winerli20-recognize-stdout.log 2> /log/winerli20-recognize-stderr.log && python3 merger.py > /log/winerli20-merge-stdout.log 2> /log/winerli20-merge-stderr.log"

evaluation: check-log-rw check-evaluation-rw
	bash -c "source ./env/evaluation.env && python3 evaluation.py > /log/winerli20-evaluation-stdout.log 2> /log/winerli20-evaluation-stderr.log"


test-all: test-aliasmap test-recognize

test-aliasmap: check-log-rw check-test-output-rw test-aliasmap-1
	echo "Finished generating aliasmap test input data. Running tests now..."
	pytest -p no:cacheprovider test_wikiparsing.py test_parse_info.py test_aliasmap.py -vv

test-aliasmap-1: check-log-rw check-test-input-r check-test-output-rw
	bash -c "source ./env/test-aliasmap-1.env && python3 create_aliasmap_multi.py"


test-recognize: check-log-rw check-test-input-r test-recognize-1 test-recognize-2 test-recognize-3 test-recognize-4 test-recognize-5
	echo "Finished generating ER/EL test input data. Running tests now..."
	pytest -p no:cacheprovider test_wikiparsing.py test_cleanup.py test_recognizer.py -vv

test-recognize-1: check-log-rw check-test-input-r check-test-output-rw check-test-databases-r
	bash -c "source ./env/test-recognize-1.env && python3 entity_recognition.py > /log/winerli20-test-recognize-1-stdout.log 2> /log/winerli20-test-recognize-1-stderr.log"

test-recognize-2: check-log-rw check-test-input-r check-test-output-rw check-test-databases-r
	bash -c "source ./env/test-recognize-2.env && python3 entity_recognition.py > /log/winerli20-test-recognize-2-stdout.log 2> /log/winerli20-test-recognize-2-stderr.log"

test-recognize-3: check-log-rw check-test-input-r check-test-output-rw check-test-databases-r
	bash -c "source ./env/test-recognize-3.env && python3 entity_recognition.py > /log/winerli20-test-recognize-3-stdout.log 2> /log/winerli20-test-recognize-3-stderr.log"

test-recognize-4: check-log-rw check-test-input-r check-test-output-rw check-test-databases-r
	bash -c "source ./env/test-recognize-4.env && python3 entity_recognition.py > /log/winerli20-test-recognize-4-stdout.log 2> /log/winerli20-test-recognize-4-stderr.log"

test-recognize-5: check-log-rw check-test-input-r check-test-output-rw check-test-databases-r
	bash -c "source ./env/test-recognize-5.env && python3 entity_recognition.py > /log/winerli20-test-recognize-5-stdout.log 2> /log/winerli20-test-recognize-5-stderr.log"
