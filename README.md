## What is WiNERLi?

Read the blog post here to get an idea about what WiNERLi does and how it works: https://ad-blog.cs.uni-freiburg.de/post/introducing-winerli-2.0-an-extension-of-winerli/

## Usage

### Build the container

```make docker-build```

### Run the container

```make docker-run``` takes arguments for the different input and output directories. All paths have to be absolute.

**Arguments:**

- `INPUT_ALIASMAP`: The directory that contains the input for the aliasmap generation.

- `OUTPUT_ALIASMAP`: The directory into which the output of the aliasmap generation will be placed.

- `INPUT_RECOGNITION`: The directory that contains the input for the entity recognition/linking.

- `OUTPUT_RECOGNITION`: The directory into which the output of the entity recognition/linking will be placed.

**Optional:**

- `LOG`: The directory into which the log files will be written. By default this is the `log` directory in your working copy.

- `DATABASES`: The directory that contains the databases needed for the ER/EL procedure (aliasmap etc.). If this is argument is not given a default path containing precalculated databases will be used. If you want to first generate the aliasmap and then use it directly this path should be the same as the `OUTPUT_ALIASMAP`.

- `MAPPINGS`: The directory that contains different mappings to convert the ER/EL output. If this is argument is not given a default path containing precalculated databases will be used.

**Example call:**

```make docker-run INPUT_ALIASMAP=`pwd`/input OUTPUT_ALIASMAP=`pwd`/output INPUT_RECOGNITION=`pwd`/input OUTPUT_RECOGNITION=`pwd`/output```

### Build the aliasmap

**To build an aliasmap from a file of your choice, you need change to the following variables in `./env/aliasmap.env`:**

- `INPUT_FILE`: A wiki dump or a valid part of a wiki dump. This file has to be located in the `input_aliasmap` volume.

- `INDEX_FILE`: If you use a wiki dump, you should put the matching index file here. Otherwise leave this empty. This file has to be located in the `input_aliasmap` volume.

- `ALIASMAP_DB`: The name for the aliasmap database output file. This file will be located in the `output_aliasmap` volume.

- `PAGE_CATEGORY_DB`: The name for the page category database output file. This file will be located in the `output_aliasmap` volume.

- `LINKS_DB`: The name for the links database output file. This file will be located in the `output_aliasmap` volume.

- `INFOBOX_CATEGORY_FILE`: The name for the infobox category output file. This file will be located in the `output_aliasmap` volume.

- `FILTER_RED_LINKS`: If set to `true` ignore link data from links for which no entity (= a wiki page) exists yet.

**Variables that may need to be changed depending on your hardware:**

- `NUMBER_PROCESSES`: The total number of processes to use.

**Other variables that usually do not need to be changed:**

- `DROP_AND_VACUUM`: Drop temporary tables from the aliasmap database and vacuum to reduce its size.

**Run the code:**

```make aliasmap```

You can find an example of all the generated databases in the `databases` directory.


### Recognize and merge

**To run the recognizer on a file of your choice and merge the files into one, you need change to the following variables in `./env/recognize-and-merge.env`:**

- `INPUT_FILE`: This can be a wiki dump or a text/xml file. It should contain only text or it can be a wiki page in which case it should start with `<mediawiki>` and follow the structure of wiki pages in wiki dumps. This file has to be located in the `input_recognition` volume.

- `INDEX_FILE`: If you use a wiki dump, you should put the matching index file here. Otherwise leave this empty. This file has to be located in the `input_recognition` volume.

- `SCORING_FACTORS`: Set the scoring factors for all additional approaches as a tuple. If a value is smaller than 1 the approach will be disabled except for approach 4 (3rd value) where any value larger than 0 will enable the approach and approach 5 (4th value) where any value larger than 1 will enable the approach. Note that the values have to be given as a tuple and the tuple has to be enclosed in '...'.

- `THRESHOLD`: The threshold for the scores. Any entity that has a score smaller than this will not be recognised. This should be a number larger than 0.

- `USE_ADJECTIVES`: Use leading adjectives as a part of potential entities. This can be `true` or `false`.

- `USE_NUMBERS`: Use numbers as a part of potential entities. This can be `true` or `false`.

- `USE_NONBINARY`: Use the non-binary gender in the recognition. This can be `true` or `false`. Since the *they* pronoun commonly associated with the non-binary gender is ambiguous as it can also be a plural pronoun, enabling this can lead to unwanted results.

- `WRITE_SCORES`: Set to 0 to only write the pure relevance from the aliasmap. Set to 1 to only write the calculated final score. Set to 2 to write both (the second to last item will be the relevance and the last item will be the final score).

**Variables for the database files:**

- `WORDS_FILE`: The name for the words files that will be created. This file will be located in the `output_recognition` volume.

- `DOCS_FILE`: The name for the docs files that will be created. This file will be located in the `output_recognition` volume.

- `ALIASMAP_DB`: The name for the aliasmap database that should be used. This file has to be located in the `databases` volume.

- `PAGE_CATEGORY_DB`: The name for the page category database that should be used. This file has to be located in the `databases` volume.

- `LINKS_DB`: The name for the links database that should be used. This file has to be located in the `databases` volume.

- `INFOBOX_CATEGORY_FILE`: The name for the infobox category file that should be used. This file has to be located in the `databases` volume.

- `GENDER_DATA_FILE`: The name for the gender data file that should be used. This file has to be located in the `databases` volume.

The gender data file can be generated using the following Qlever (https://qlever.cs.uni-freiburg.de/wikidata/) query and downloading the file as a TSV file and saving it in the `databases` directory that you'll use:

```
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX schema: <http://schema.org/>
SELECT ?name ?gender WHERE {
 ?x wdt:P21 ?g .
 ?x schema:name ?name .
 ?g schema:name ?gender .
  FILTER (lang(?name)="en") .
  FILTER (lang(?gender)="en") .
}
ORDER BY ASC(?name)
```

**Variables that may need to be changed depending on your hardware:**

- `NUMBER_PROCESSES`: The total number of processes to use. The number of recognition processes will be this number minus the parsing and writing processes and minus the input process.

- `NUMBER_PARSE_PROCESSES`: The number of processes for parsing the input file.

- `NUMBER_WRITE_PROCESSES`: The number of processes that will write the output to files.

**Run the code:**

```make recognize-and-merge```

You can find an example of all the generated output files in the `output` directory.


### Tests

**Run the aliasmap tests:**

```make test-aliasmap```


**Run the recognizer tests:**

```make test-recognize```

**Run all tests:**

```make test-all```


### Evaluation

**To run the evaluation and output the results as a markdown-formatted table, you may change the following variables in `./env/evaluation.env`:**

- `RESULT_TABLE_FILE`: The file into which the result tables should be written in markdown formatting. This file will be located in the `evaluation` volume in the `output` subdirectory.


**Run the evaluation:**

Note that this can take some time because of all the different combinations of input values that are being evaluated and because it does not use multiprocessing.

```make evaluation```

**Attention: This only works within the university network because large databases are required that are stored on a uni server.**
