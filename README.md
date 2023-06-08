## What is WiNERLi?

Read the blog post here to get an idea about what WiNERLi does and how it works: https://ad-blog.cs.uni-freiburg.de/post/introducing-winerli-2.0-an-extension-of-winerli/

## Usage

### Build the aliasmap

**To build an aliasmap from a file of your choice, you need change to the following variables in `gantry_aliasmap.def.yml`:**

- `INPUT_FILE`: A wiki dump or a valid part of a wiki dump. This file has to be located in the `input` volume.

- `INDEX_FILE`: If you use a wiki dump, you should put the matching index file here. Otherwise leave this empty. This file has to be located in the `input` volume.

- `ALIASMAP_DB`: The name for the aliasmap database output file. This file will be located in the `output` volume.

- `PAGE_CATEGORY_DB`: The name for the page category database output file. This file will be located in the `output` volume.

- `LINKS_DB`: The name for the links database output file. This file will be located in the `output` volume.

- `INFOBOX_CATEGORY_FILE`: The name for the infobox category output file. This file will be located in the `output` volume.

- `FILTER_RED_LINKS`: If set to `true` ignore link data from links for which no entity (= a wiki page) exists yet.


**Variables that may need to be changed depending on your hardware:**

- `NUMBER_PROCESSES`: The total number of processes to use.


**Other variables that usually do not need to be changed:**

- `DROP_AND_VACUUM`: Drop temporary tables from the aliasmap database and vacuum to reduce its size.


**Run the code:**

```make aliasmap```


### Recognize and merge

**To run the recognizer on a file of your choice and merge the files into one, you need change to the following variables in `gantry_recognize_and_merge.def.yml`:**

- `INPUT_FILE`: This can be a wiki dump or a text/xml file. It should contain only text or it can be a wiki page in which case it should start with `<mediawiki>` and follow the structure of wiki pages in wiki dumps. This file has to be located in the `input` volume.

- `INDEX_FILE`: If you use a wiki dump, you should put the matching index file here. Otherwise leave this empty. This file has to be located in the `input` volume.

- `SCORING_FACTORS`: Set the scoring factors for all additional approaches as a tuple. If a value is smaller than 1 the approach will be disabled except for approach 4 where any value larger than 0 will enable the approach.

- `THRESHOLD`: The threshold for the scores. Any entity that has a score smaller than this will not be recognised. This should be a number larger than 0.

- `USE_ADJECTIVES`: Use leading adjectives as a part of potential entities. This can be `true` or `false`.

- `USE_NUMBERS`: Use numbers as a part of potential entities. This can be `true` or `false`.

- `USE_NONBINARY`: Use the non-binary gender in the recognition. This can be `true` or `false`. Since the *they* pronoun commonly associated with the non-binary gender is ambiguous as it can also be a plural pronoun, enabling this can lead to unwanted results.

- `WRITE_SCORES`: Set to 0 to only write the pure relevance from the aliasmap. Set to 1 to only write the calculated final score. Set to 2 to write both (the second to last item will be the relevance and the last item will be the final score).


**Variables that may need to be changed depending on your hardware:**

- `NUMBER_PROCESSES`: The total number of processes to use. The number of recognition processes will be this number minus the parsing and writing processes.

- `NUMBER_PARSE_PROCESSES`: The number of processes for parsing the input file.

- `NUMBER_WRITE_PROCESSES`: The number of processes that will write the output to files.


**Other variables that usually do not need to be changed:**

- `WORDS_FILE`: The name for the words files that will be created. This file will be located in the `output` volume.

- `DOCS_FILE`: The name for the docs files that will be created. This file will be located in the `output` volume.

- `ALIASMAP_DB`: The name for the aliasmap database that should be used. This file has to be located in the `databases` volume.

- `PAGE_CATEGORY_DB`: The name for the page category database that should be used. This file has to be located in the `databases` volume.

- `LINKS_DB`: The name for the links database that should be used. This file has to be located in the `databases` volume.

- `INFOBOX_CATEGORY_FILE`: The name for the infobox category file that should be used. This file has to be located in the `databases` volume.

- `GENDER_DATA_FILE`: The name for the gender data file that should be used. This file has to be located in the `databases` volume.


**Run the code:**

```make recognize_and_merge```


### Tests

**Run the aliasmap tests:**

```make aliasmap_tests```


**Run the recognizer tests:**

```make recognizer_tests```

**Run all tests:**

```make tests```


### Evaluation

**To run the evaluation and output the results as a markdown-formatted table, you may change the following variables in `gantry_evaluation.def.yml`:**

- `RESULT_TABLE_FILE`: The file into which the result table should be written. This file will be located in the `output` volume.


**Run the evaluation:**

```make evaluate```