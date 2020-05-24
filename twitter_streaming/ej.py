import unidecode as unidecode
from flashtext import KeywordProcessor
keyword_processor = KeywordProcessor()
# keyword_processor.add_keyword(<unclean name>, <standardised name>)
keyword_processor.add_keyword('big apple', 'NEW YORK')
keyword_processor.add_keyword('Bay Area')
keywords_found = keyword_processor.extract_keywords('I loveb Big apple and Bay Area, Bay Area, Bay Area.')
print(keywords_found)
# ['New York', 'Bay Area']
print(unidecode.unidecode('áéŕ'))