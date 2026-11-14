# API Query

The commands `.help` and `.resources` are reserved for specific functions:

`.help`: Retrieves help documentation and usage guides.

`.resources`: Lists all available Bible versions and resources.

## Standard Queries

All other API queries must follow a specific format consisting of a keyword and its associated options, delimited by a triple colon `:::`.

## Syntax Conventions:

`{option}`: Indicates a required parameter.

`{option}*`: Indicates an optional parameter.

Multiple Values: If a parameter accepts multiple values, separate them with commas (e.g., KJV,NET).

## Keyword - morphology
* Retrieve word morphology in bible verse(s)
* Syntax: morphology:::{verse_reference[s]}
* Example: morphology:::John 3:16

## Keyword - chapter
* Retrieve bible chapter(s)
* Syntax: chapter:::{bible}*:::{chapter_reference[s]}
* Example: chapter:::John 3, chapter:::KJV:::John 3

## Keyword - comparechapter
* Compare bible chapter(s)
* Syntax: comparechapter:::{bibles}*:::{chapter_reference[s]}
* Example: comparechapter:::KJV,CUV:::John 3

## Keyword - verses
* Retrieve bible verse(s)
* Syntax: verses:::{bibles}*:::{verse_reference[s]}
* Example: verses:::John 3:16; Rm 5:8, verses:::KJV:::John 3:16; Rm 5:8, verses:::KJV,CUV:::John 3:16; Rm 5:8

## Keyword - literal
* Literal string search for bible verse(s)
* Syntax: literal:::{bibles_books}*:::{search_string}
* Example: literal:::Jesus love, literal:::KJV:::Jesus love, literal:::Matt,KJV:::love

## Keyword - regex
* Regular expression search for bible verse(s)
* Syntax: regex:::{bibles_books}*:::{regex_pattern}
* Example: regex:::Jesus.*?love, regex:::KJV:::Jesus.*?love, regex:::Matt,KJV:::Jesus.*?love

## Keyword - semantic
* Semantic search for bible verse(s)
* Syntax: semantic:::{bibles_books}*:::{search_string}
* Example: semantic:::Jesus love, semantic:::KJV:::Jesus love , semantic:::Matt,KJV:::Jesus love

## Keyword - treasury
* Treasury of scripture knowledge of bible verse(s)
* Syntax: treasury:::{verse_reference[s]}
* Example: treasury:::John 3:16

## Keyword - commentary
* Retrieve bible commentary
* Syntax: commentary:::{commentary}*:::{verse_reference[s]}
* Example: commentary:::John 3:16, commentary:::AICTC:::John 3:16

## Keyword - chronology
* Retrieve or search for bible chronology
* Syntax: chronology:::{search_string}*
* Example: chronology:::, chronology:::70 AD, chronology:::Jesus, chronology:::Acts 15

## Keyword - xrefs
* Retrieve bible verse cross-references
* Syntax: xrefs:::{bible}*:::{verse_reference[s]}
* Example: xrefs:::John 3:16, xrefs:::KJV:::John 3:16

## Keyword - promises
* Retrieve bible promises
* Syntax: promises:::{bible}*:::{promise_entry}
* Example: promises:::1.1, promises:::KJV:::1.1

## Keyword - parallels
* Retrieve bible parallel passages
* Syntax: parallels:::{bible}*:::{parallel_entry}
* Example: parallels:::1.1, parallels:::KJV:::1.1

## Keyword - topics
* Retrieve bible topical studies
* Syntax: topics:::{topic_entry}
* Example: topics:::NAV100

## Keyword - characters
* Retrieve bible character studies
* Syntax: characters:::{character_entry}
* Example: characters:::BP100

## Keyword - locations
* Retrieve bible location studies
* Syntax: locations:::{location_entry}
* Example: locations:::BP100

## Keyword - names
* Search for bible names and their meanings
* Syntax: names:::{name}
* Example: names:::Joshua

## Keyword - dictionaries
* Retrieve bible dictionary entries
* Syntax: dictionaries:::{dictionary_entry}
* Example: dictionaries:::EAS100

## Keyword - encyclopedias
* Retrieve bible encyclopedia entries
* Syntax: encyclopedias:::{encyclopedia_entry}
* Example: encyclopedias:::ISBE100

## Keyword - lexicons
* Retrieve bible lexicon entries
* Syntax: lexicons:::{lexicon}*:::{lexicon_entry}
* Example: lexicons:::H100, lexicons:::Morphology:::G100