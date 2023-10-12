.PHONY : aliasmap_tests recognizer_test

help:
	@echo "Nothing useful here"

aliasmap:
	gantry -f gantry_aliasmap.def.yml -g gantry_aliasmap.env.yml

recognize:
	gantry -f gantry_recognizer.def.yml -g gantry_recognizer.env.yml

merge:
	gantry -f gantry_merger.def.yml -g gantry_merger.env.yml

recognize_and_merge:
	gantry -f gantry_recognize_and_merge.def.yml -g gantry_recognize_and_merge.env.yml

evaluate:
	gantry -f gantry_evaluation.def.yml -g gantry_evaluation.env.yml

aliasmap_tests:
	gantry -f gantry_testcases_aliasmap.def.yml -g gantry_testcases_aliasmap.env.yml

recognizer_tests:
	gantry -f gantry_testcases_recognizer.def.yml -g gantry_testcases_recognizer.env.yml

recognizer_only_tests:
	gantry -f gantry_testcases_recognizer_onlytests.def.yml -g gantry_testcases_recognizer.env.yml

tests: aliasmap_tests recognizer_tests
