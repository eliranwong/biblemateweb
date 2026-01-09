TOOLS_SCHEMA = {'anyalyze_psalms': {'description': 'analyze the context and background of the '
                                    'Psalms in the bible; Psalm reference must '
                                    'be given, e.g. Psalm 23:1-3',
                     'name': 'anyalyze_psalms',
                     'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                         'type': 'object'},
                                                               'type': 'array'}},
                                    'required': ['request'],
                                    'type': 'object'}},
 'ask_bible_scholar': {'description': 'ask a bible scholar about the bible',
                       'name': 'ask_bible_scholar',
                       'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                           'type': 'object'},
                                                                 'type': 'array'}},
                                      'required': ['request'],
                                      'type': 'object'}},
 'ask_pastor': {'description': 'ask a church pastor about the bible',
                'name': 'ask_pastor',
                'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                    'type': 'object'},
                                                          'type': 'array'}},
                               'required': ['request'],
                               'type': 'object'}},
 'ask_theologian': {'description': 'ask a theologian about the bible',
                    'name': 'ask_theologian',
                    'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                        'type': 'object'},
                                                              'type': 'array'}},
                                   'required': ['request'],
                                   'type': 'object'}},
 'compare_bible_translations': {'description': 'compare Bible translations; '
                                               'bible verse reference(s) must '
                                               'be given',
                                'name': 'compare_bible_translations',
                                'parameters': {'properties': {'request': {'type': 'string'}},
                                               'required': ['request'],
                                               'type': 'object'}},
 'explain_bible_meaning': {'description': 'Explain the meaning of the '
                                          'user-given content in reference to '
                                          'the Bible',
                           'name': 'explain_bible_meaning',
                           'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                               'type': 'object'},
                                                                     'type': 'array'}},
                                          'required': ['request'],
                                          'type': 'object'}},
 'expound_bible_topic': {'description': 'Expound the user-given topic in '
                                        'reference to the Bible; a topic must '
                                        'be given',
                         'name': 'expound_bible_topic',
                         'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                             'type': 'object'},
                                                                   'type': 'array'}},
                                        'required': ['request'],
                                        'type': 'object'}},
 'identify_bible_keywords': {'description': 'Identify bible key words from the '
                                            'user-given content',
                             'name': 'identify_bible_keywords',
                             'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                 'type': 'object'},
                                                                       'type': 'array'}},
                                            'required': ['request'],
                                            'type': 'object'}},
 'interpret_new_testament_verse': {'description': 'Interpret the user-given '
                                                  'bible verse from the New '
                                                  'Testament in the light of '
                                                  'its context, together with '
                                                  'insights of biblical Greek '
                                                  'studies; a new testament '
                                                  'bible verse / reference(s) '
                                                  'must be given',
                                   'name': 'interpret_new_testament_verse',
                                   'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                       'type': 'object'},
                                                                             'type': 'array'}},
                                                  'required': ['request'],
                                                  'type': 'object'}},
 'interpret_old_testament_verse': {'description': 'Interpret the user-given '
                                                  'bible verse from the Old '
                                                  'Testament in the light of '
                                                  'its context, together with '
                                                  'insights of biblical Hebrew '
                                                  'studies; an old testament '
                                                  'bible verse / reference(s) '
                                                  'must be given',
                                   'name': 'interpret_old_testament_verse',
                                   'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                       'type': 'object'},
                                                                             'type': 'array'}},
                                                  'required': ['request'],
                                                  'type': 'object'}},
 'quote_bible_promises': {'description': 'Quote relevant Bible promises in '
                                         'response to user request',
                          'name': 'quote_bible_promises',
                          'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                              'type': 'object'},
                                                                    'type': 'array'}},
                                         'required': ['request'],
                                         'type': 'object'}},
 'quote_bible_verses': {'description': 'quote multiple bible verses in '
                                       'response to user request',
                        'name': 'quote_bible_verses',
                        'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                            'type': 'object'},
                                                                  'type': 'array'}},
                                       'required': ['request'],
                                       'type': 'object'}},
 'read_bible_commentary': {'description': 'read bible commentary on individual '
                                          'bible verses; bible verse '
                                          'reference(s) must be given, like , '
                                          'like John 3:16 or John 3:16-18',
                           'name': 'read_bible_commentary',
                           'parameters': {'properties': {'request': {'type': 'string'}},
                                          'required': ['request'],
                                          'type': 'object'}},
 'refine_bible_translation': {'description': 'refine the translation of a '
                                             'Bible verse or passage',
                              'name': 'refine_bible_translation',
                              'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                  'type': 'object'},
                                                                        'type': 'array'}},
                                             'required': ['request'],
                                             'type': 'object'}},
 'retrieve_bible_chapter': {'description': 'retrieve a whole Bible chapter; '
                                           'bible chapter reference must be '
                                           'given, e.g. John 3',
                            'name': 'retrieve_bible_chapter',
                            'parameters': {'properties': {'request': {'type': 'string'}},
                                           'required': ['request'],
                                           'type': 'object'}},
 'retrieve_bible_cross_references': {'description': 'retrieve cross-references '
                                                    'of Bible verses; bible '
                                                    'verse reference(s) must '
                                                    'be given',
                                     'name': 'retrieve_bible_cross_references',
                                     'parameters': {'properties': {'request': {'type': 'string'}},
                                                    'required': ['request'],
                                                    'type': 'object'}},
 'retrieve_bible_verses': {'description': 'retrieve Bible verses; bible verse '
                                          'reference(s) must be given, e.g. '
                                          'John 3:16-17; single or multiple '
                                          'references accepted, e.g. Deut 6:4; '
                                          'Gen 1:26-27',
                           'name': 'retrieve_bible_verses',
                           'parameters': {'properties': {'request': {'type': 'string'}},
                                          'required': ['request'],
                                          'type': 'object'}},
 'retrieve_hebrew_or_greek_bible_verses': {'description': 'retrieve Hebrew or '
                                                          'Greek Bible verses; '
                                                          'bible verse '
                                                          'reference(s) must '
                                                          'be given, e.g. John '
                                                          '3:16-17; single or '
                                                          'multiple references '
                                                          'accepted, e.g. Deut '
                                                          '6:4; Gen 1:26-27',
                                           'name': 'retrieve_hebrew_or_greek_bible_verses',
                                           'parameters': {'properties': {'request': {'type': 'string'}},
                                                          'required': ['request'],
                                                          'type': 'object'}},
 'retrieve_interlinear_hebrew_or_greek_bible_verses': {'description': 'retrieve '
                                                                      'interlinear '
                                                                      'Hebrew-English '
                                                                      'or '
                                                                      'Greek-English '
                                                                      'Bible '
                                                                      'verses; '
                                                                      'bible '
                                                                      'verse '
                                                                      'reference(s) '
                                                                      'must be '
                                                                      'given, '
                                                                      'e.g. '
                                                                      'John '
                                                                      '3:16-17; '
                                                                      'single '
                                                                      'or '
                                                                      'multiple '
                                                                      'references '
                                                                      'accepted, '
                                                                      'e.g. '
                                                                      'Deut '
                                                                      '6:4; '
                                                                      'Gen '
                                                                      '1:26-27',
                                                       'name': 'retrieve_interlinear_hebrew_or_greek_bible_verses',
                                                       'parameters': {'properties': {'request': {'type': 'string'}},
                                                                      'required': ['request'],
                                                                      'type': 'object'}},
 'retrieve_verse_morphology': {'description': 'retrieve parsing and morphology '
                                              'of individual bible verses; '
                                              'bible verse reference(s) must '
                                              'be given, e.g. John 3:16-17; '
                                              'single or multiple references '
                                              'accepted, e.g. Deut 6:4; Gen '
                                              '1:26-27',
                               'name': 'retrieve_verse_morphology',
                               'parameters': {'properties': {'request': {'type': 'string'}},
                                              'required': ['request'],
                                              'type': 'object'}},
 'search_1_chronicles_only': {'description': 'search the book of 1 Chronicles '
                                             'only; search string must be '
                                             'given',
                              'name': 'search_1_chronicles_only',
                              'parameters': {'properties': {'request': {'type': 'string'}},
                                             'required': ['request'],
                                             'type': 'object'}},
 'search_1_corinthians_only': {'description': 'search the book of 1 '
                                              'Corinthians only; search string '
                                              'must be given',
                               'name': 'search_1_corinthians_only',
                               'parameters': {'properties': {'request': {'type': 'string'}},
                                              'required': ['request'],
                                              'type': 'object'}},
 'search_1_john_only': {'description': 'search the book of 1 John only; search '
                                       'string must be given',
                        'name': 'search_1_john_only',
                        'parameters': {'properties': {'request': {'type': 'string'}},
                                       'required': ['request'],
                                       'type': 'object'}},
 'search_1_kings_only': {'description': 'search the book of 1 Kings only; '
                                        'search string must be given',
                         'name': 'search_1_kings_only',
                         'parameters': {'properties': {'request': {'type': 'string'}},
                                        'required': ['request'],
                                        'type': 'object'}},
 'search_1_peter_only': {'description': 'search the book of 1 Peter only; '
                                        'search string must be given',
                         'name': 'search_1_peter_only',
                         'parameters': {'properties': {'request': {'type': 'string'}},
                                        'required': ['request'],
                                        'type': 'object'}},
 'search_1_samuel_only': {'description': 'search the book of 1 Samuel only; '
                                         'search string must be given',
                          'name': 'search_1_samuel_only',
                          'parameters': {'properties': {'request': {'type': 'string'}},
                                         'required': ['request'],
                                         'type': 'object'}},
 'search_1_thessalonians_only': {'description': 'search the book of 1 '
                                                'Thessalonians only; search '
                                                'string must be given',
                                 'name': 'search_1_thessalonians_only',
                                 'parameters': {'properties': {'request': {'type': 'string'}},
                                                'required': ['request'],
                                                'type': 'object'}},
 'search_1_timothy_only': {'description': 'search the book of 1 Timothy only; '
                                          'search string must be given',
                           'name': 'search_1_timothy_only',
                           'parameters': {'properties': {'request': {'type': 'string'}},
                                          'required': ['request'],
                                          'type': 'object'}},
 'search_2_chronicles_only': {'description': 'search the book of 2 Chronicles '
                                             'only; search string must be '
                                             'given',
                              'name': 'search_2_chronicles_only',
                              'parameters': {'properties': {'request': {'type': 'string'}},
                                             'required': ['request'],
                                             'type': 'object'}},
 'search_2_corinthians_only': {'description': 'search the book of 2 '
                                              'Corinthians only; search string '
                                              'must be given',
                               'name': 'search_2_corinthians_only',
                               'parameters': {'properties': {'request': {'type': 'string'}},
                                              'required': ['request'],
                                              'type': 'object'}},
 'search_2_john_only': {'description': 'search the book of 2 John only; search '
                                       'string must be given',
                        'name': 'search_2_john_only',
                        'parameters': {'properties': {'request': {'type': 'string'}},
                                       'required': ['request'],
                                       'type': 'object'}},
 'search_2_kings_only': {'description': 'search the book of 2 Kings only; '
                                        'search string must be given',
                         'name': 'search_2_kings_only',
                         'parameters': {'properties': {'request': {'type': 'string'}},
                                        'required': ['request'],
                                        'type': 'object'}},
 'search_2_peter_only': {'description': 'search the book of 2 Peter only; '
                                        'search string must be given',
                         'name': 'search_2_peter_only',
                         'parameters': {'properties': {'request': {'type': 'string'}},
                                        'required': ['request'],
                                        'type': 'object'}},
 'search_2_samuel_only': {'description': 'search the book of 2 Samuel only; '
                                         'search string must be given',
                          'name': 'search_2_samuel_only',
                          'parameters': {'properties': {'request': {'type': 'string'}},
                                         'required': ['request'],
                                         'type': 'object'}},
 'search_2_thessalonians_only': {'description': 'search the book of 2 '
                                                'Thessalonians only; search '
                                                'string must be given',
                                 'name': 'search_2_thessalonians_only',
                                 'parameters': {'properties': {'request': {'type': 'string'}},
                                                'required': ['request'],
                                                'type': 'object'}},
 'search_2_timothy_only': {'description': 'search the book of 2 Timothy only; '
                                          'search string must be given',
                           'name': 'search_2_timothy_only',
                           'parameters': {'properties': {'request': {'type': 'string'}},
                                          'required': ['request'],
                                          'type': 'object'}},
 'search_3_john_only': {'description': 'search the book of 3 John only; search '
                                       'string must be given',
                        'name': 'search_3_john_only',
                        'parameters': {'properties': {'request': {'type': 'string'}},
                                       'required': ['request'],
                                       'type': 'object'}},
 'search_acts_only': {'description': 'search the book of Acts only; search '
                                     'string must be given',
                      'name': 'search_acts_only',
                      'parameters': {'properties': {'request': {'type': 'string'}},
                                     'required': ['request'],
                                     'type': 'object'}},
 'search_amos_only': {'description': 'search the book of Amos only; search '
                                     'string must be given',
                      'name': 'search_amos_only',
                      'parameters': {'properties': {'request': {'type': 'string'}},
                                     'required': ['request'],
                                     'type': 'object'}},
 'search_colossians_only': {'description': 'search the book of Colossians '
                                           'only; search string must be given',
                            'name': 'search_colossians_only',
                            'parameters': {'properties': {'request': {'type': 'string'}},
                                           'required': ['request'],
                                           'type': 'object'}},
 'search_daniel_only': {'description': 'search the book of Daniel only; search '
                                       'string must be given',
                        'name': 'search_daniel_only',
                        'parameters': {'properties': {'request': {'type': 'string'}},
                                       'required': ['request'],
                                       'type': 'object'}},
 'search_deuteronomy_only': {'description': 'search the book of Deuteronomy '
                                            'only; search string must be given',
                             'name': 'search_deuteronomy_only',
                             'parameters': {'properties': {'request': {'type': 'string'}},
                                            'required': ['request'],
                                            'type': 'object'}},
 'search_ecclesiastes_only': {'description': 'search the book of Ecclesiastes '
                                             'only; search string must be '
                                             'given',
                              'name': 'search_ecclesiastes_only',
                              'parameters': {'properties': {'request': {'type': 'string'}},
                                             'required': ['request'],
                                             'type': 'object'}},
 'search_ephesians_only': {'description': 'search the book of Ephesians only; '
                                          'search string must be given',
                           'name': 'search_ephesians_only',
                           'parameters': {'properties': {'request': {'type': 'string'}},
                                          'required': ['request'],
                                          'type': 'object'}},
 'search_esther_only': {'description': 'search the book of Esther only; search '
                                       'string must be given',
                        'name': 'search_esther_only',
                        'parameters': {'properties': {'request': {'type': 'string'}},
                                       'required': ['request'],
                                       'type': 'object'}},
 'search_exodus_only': {'description': 'search the book of Exodus only; search '
                                       'string must be given',
                        'name': 'search_exodus_only',
                        'parameters': {'properties': {'request': {'type': 'string'}},
                                       'required': ['request'],
                                       'type': 'object'}},
 'search_ezekiel_only': {'description': 'search the book of Ezekiel only; '
                                        'search string must be given',
                         'name': 'search_ezekiel_only',
                         'parameters': {'properties': {'request': {'type': 'string'}},
                                        'required': ['request'],
                                        'type': 'object'}},
 'search_ezra_only': {'description': 'search the book of Ezra only; search '
                                     'string must be given',
                      'name': 'search_ezra_only',
                      'parameters': {'properties': {'request': {'type': 'string'}},
                                     'required': ['request'],
                                     'type': 'object'}},
 'search_galatians_only': {'description': 'search the book of Galatians only; '
                                          'search string must be given',
                           'name': 'search_galatians_only',
                           'parameters': {'properties': {'request': {'type': 'string'}},
                                          'required': ['request'],
                                          'type': 'object'}},
 'search_genesis_only': {'description': 'search the book of Genesis only; '
                                        'search string must be given',
                         'name': 'search_genesis_only',
                         'parameters': {'properties': {'request': {'type': 'string'}},
                                        'required': ['request'],
                                        'type': 'object'}},
 'search_habakkuk_only': {'description': 'search the book of Habakkuk only; '
                                         'search string must be given',
                          'name': 'search_habakkuk_only',
                          'parameters': {'properties': {'request': {'type': 'string'}},
                                         'required': ['request'],
                                         'type': 'object'}},
 'search_haggai_only': {'description': 'search the book of Haggai only; search '
                                       'string must be given',
                        'name': 'search_haggai_only',
                        'parameters': {'properties': {'request': {'type': 'string'}},
                                       'required': ['request'],
                                       'type': 'object'}},
 'search_hebrews_only': {'description': 'search the book of Hebrews only; '
                                        'search string must be given',
                         'name': 'search_hebrews_only',
                         'parameters': {'properties': {'request': {'type': 'string'}},
                                        'required': ['request'],
                                        'type': 'object'}},
 'search_hosea_only': {'description': 'search the book of Hosea only; search '
                                      'string must be given',
                       'name': 'search_hosea_only',
                       'parameters': {'properties': {'request': {'type': 'string'}},
                                      'required': ['request'],
                                      'type': 'object'}},
 'search_isaiah_only': {'description': 'search the book of Isaiah only; search '
                                       'string must be given',
                        'name': 'search_isaiah_only',
                        'parameters': {'properties': {'request': {'type': 'string'}},
                                       'required': ['request'],
                                       'type': 'object'}},
 'search_james_only': {'description': 'search the book of James only; search '
                                      'string must be given',
                       'name': 'search_james_only',
                       'parameters': {'properties': {'request': {'type': 'string'}},
                                      'required': ['request'],
                                      'type': 'object'}},
 'search_jeremiah_only': {'description': 'search the book of Jeremiah only; '
                                         'search string must be given',
                          'name': 'search_jeremiah_only',
                          'parameters': {'properties': {'request': {'type': 'string'}},
                                         'required': ['request'],
                                         'type': 'object'}},
 'search_job_only': {'description': 'search the book of Job only; search '
                                    'string must be given',
                     'name': 'search_job_only',
                     'parameters': {'properties': {'request': {'type': 'string'}},
                                    'required': ['request'],
                                    'type': 'object'}},
 'search_joel_only': {'description': 'search the book of Joel only; search '
                                     'string must be given',
                      'name': 'search_joel_only',
                      'parameters': {'properties': {'request': {'type': 'string'}},
                                     'required': ['request'],
                                     'type': 'object'}},
 'search_john_only': {'description': 'search the book of John only; search '
                                     'string must be given',
                      'name': 'search_john_only',
                      'parameters': {'properties': {'request': {'type': 'string'}},
                                     'required': ['request'],
                                     'type': 'object'}},
 'search_jonah_only': {'description': 'search the book of Jonah only; search '
                                      'string must be given',
                       'name': 'search_jonah_only',
                       'parameters': {'properties': {'request': {'type': 'string'}},
                                      'required': ['request'],
                                      'type': 'object'}},
 'search_joshua_only': {'description': 'search the book of Joshua only; search '
                                       'string must be given',
                        'name': 'search_joshua_only',
                        'parameters': {'properties': {'request': {'type': 'string'}},
                                       'required': ['request'],
                                       'type': 'object'}},
 'search_jude_only': {'description': 'search the book of Jude only; search '
                                     'string must be given',
                      'name': 'search_jude_only',
                      'parameters': {'properties': {'request': {'type': 'string'}},
                                     'required': ['request'],
                                     'type': 'object'}},
 'search_judges_only': {'description': 'search the book of Judges only; search '
                                       'string must be given',
                        'name': 'search_judges_only',
                        'parameters': {'properties': {'request': {'type': 'string'}},
                                       'required': ['request'],
                                       'type': 'object'}},
 'search_lamentations_only': {'description': 'search the book of Lamentations '
                                             'only; search string must be '
                                             'given',
                              'name': 'search_lamentations_only',
                              'parameters': {'properties': {'request': {'type': 'string'}},
                                             'required': ['request'],
                                             'type': 'object'}},
 'search_leviticus_only': {'description': 'search the book of Leviticus only; '
                                          'search string must be given',
                           'name': 'search_leviticus_only',
                           'parameters': {'properties': {'request': {'type': 'string'}},
                                          'required': ['request'],
                                          'type': 'object'}},
 'search_luke_only': {'description': 'search the book of Luke only; search '
                                     'string must be given',
                      'name': 'search_luke_only',
                      'parameters': {'properties': {'request': {'type': 'string'}},
                                     'required': ['request'],
                                     'type': 'object'}},
 'search_malachi_only': {'description': 'search the book of Malachi only; '
                                        'search string must be given',
                         'name': 'search_malachi_only',
                         'parameters': {'properties': {'request': {'type': 'string'}},
                                        'required': ['request'],
                                        'type': 'object'}},
 'search_mark_only': {'description': 'search the book of Mark only; search '
                                     'string must be given',
                      'name': 'search_mark_only',
                      'parameters': {'properties': {'request': {'type': 'string'}},
                                     'required': ['request'],
                                     'type': 'object'}},
 'search_matthew_only': {'description': 'search the book of Matthew only; '
                                        'search string must be given',
                         'name': 'search_matthew_only',
                         'parameters': {'properties': {'request': {'type': 'string'}},
                                        'required': ['request'],
                                        'type': 'object'}},
 'search_micah_only': {'description': 'search the book of Micah only; search '
                                      'string must be given',
                       'name': 'search_micah_only',
                       'parameters': {'properties': {'request': {'type': 'string'}},
                                      'required': ['request'],
                                      'type': 'object'}},
 'search_nahum_only': {'description': 'search the book of Nahum only; search '
                                      'string must be given',
                       'name': 'search_nahum_only',
                       'parameters': {'properties': {'request': {'type': 'string'}},
                                      'required': ['request'],
                                      'type': 'object'}},
 'search_nehemiah_only': {'description': 'search the book of Nehemiah only; '
                                         'search string must be given',
                          'name': 'search_nehemiah_only',
                          'parameters': {'properties': {'request': {'type': 'string'}},
                                         'required': ['request'],
                                         'type': 'object'}},
 'search_numbers_only': {'description': 'search the book of Numbers only; '
                                        'search string must be given',
                         'name': 'search_numbers_only',
                         'parameters': {'properties': {'request': {'type': 'string'}},
                                        'required': ['request'],
                                        'type': 'object'}},
 'search_obadiah_only': {'description': 'search the book of Obadiah only; '
                                        'search string must be given',
                         'name': 'search_obadiah_only',
                         'parameters': {'properties': {'request': {'type': 'string'}},
                                        'required': ['request'],
                                        'type': 'object'}},
 'search_philemon_only': {'description': 'search the book of Philemon only; '
                                         'search string must be given',
                          'name': 'search_philemon_only',
                          'parameters': {'properties': {'request': {'type': 'string'}},
                                         'required': ['request'],
                                         'type': 'object'}},
 'search_philippians_only': {'description': 'search the book of Philippians '
                                            'only; search string must be given',
                             'name': 'search_philippians_only',
                             'parameters': {'properties': {'request': {'type': 'string'}},
                                            'required': ['request'],
                                            'type': 'object'}},
 'search_proverbs_only': {'description': 'search the book of Proverbs only; '
                                         'search string must be given',
                          'name': 'search_proverbs_only',
                          'parameters': {'properties': {'request': {'type': 'string'}},
                                         'required': ['request'],
                                         'type': 'object'}},
 'search_psalms_only': {'description': 'search the book of Psalms only; search '
                                       'string must be given',
                        'name': 'search_psalms_only',
                        'parameters': {'properties': {'request': {'type': 'string'}},
                                       'required': ['request'],
                                       'type': 'object'}},
 'search_revelation_only': {'description': 'search the book of Revelation '
                                           'only; search string must be given',
                            'name': 'search_revelation_only',
                            'parameters': {'properties': {'request': {'type': 'string'}},
                                           'required': ['request'],
                                           'type': 'object'}},
 'search_romans_only': {'description': 'search the book of Romans only; search '
                                       'string must be given',
                        'name': 'search_romans_only',
                        'parameters': {'properties': {'request': {'type': 'string'}},
                                       'required': ['request'],
                                       'type': 'object'}},
 'search_ruth_only': {'description': 'search the book of Ruth only; search '
                                     'string must be given',
                      'name': 'search_ruth_only',
                      'parameters': {'properties': {'request': {'type': 'string'}},
                                     'required': ['request'],
                                     'type': 'object'}},
 'search_song_of_songs_only': {'description': 'search the book of Song of '
                                              'Songs only; search string must '
                                              'be given',
                               'name': 'search_song_of_songs_only',
                               'parameters': {'properties': {'request': {'type': 'string'}},
                                              'required': ['request'],
                                              'type': 'object'}},
 'search_the_whole_bible': {'description': 'search the whole bible; search '
                                           'string must be given',
                            'name': 'search_the_whole_bible',
                            'parameters': {'properties': {'request': {'type': 'string'}},
                                           'required': ['request'],
                                           'type': 'object'}},
 'search_titus_only': {'description': 'search the book of Titus only; search '
                                      'string must be given',
                       'name': 'search_titus_only',
                       'parameters': {'properties': {'request': {'type': 'string'}},
                                      'required': ['request'],
                                      'type': 'object'}},
 'search_zechariah_only': {'description': 'search the book of Zechariah only; '
                                          'search string must be given',
                           'name': 'search_zechariah_only',
                           'parameters': {'properties': {'request': {'type': 'string'}},
                                          'required': ['request'],
                                          'type': 'object'}},
 'search_zephaniah_only': {'description': 'search the book of Zephaniah only; '
                                          'search string must be given',
                           'name': 'search_zephaniah_only',
                           'parameters': {'properties': {'request': {'type': 'string'}},
                                          'required': ['request'],
                                          'type': 'object'}},
 'study_bible_themes': {'description': 'Study Bible Themes in relation to the '
                                       'user content',
                        'name': 'study_bible_themes',
                        'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                            'type': 'object'},
                                                                  'type': 'array'}},
                                       'required': ['request'],
                                       'type': 'object'}},
 'study_new_testament_themes': {'description': 'Study Bible Themes in a New '
                                               'Testament passage; new '
                                               'testament bible book / chapter '
                                               '/ passage / reference(s) must '
                                               'be given',
                                'name': 'study_new_testament_themes',
                                'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                    'type': 'object'},
                                                                          'type': 'array'}},
                                               'required': ['request'],
                                               'type': 'object'}},
 'study_old_testament_themes': {'description': 'Study Bible Themes in a Old '
                                               'Testament passage; old '
                                               'testatment bible book / '
                                               'chapter / passage / '
                                               'reference(s) must be given',
                                'name': 'study_old_testament_themes',
                                'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                    'type': 'object'},
                                                                          'type': 'array'}},
                                               'required': ['request'],
                                               'type': 'object'}},
 'translate_greek_bible_verse': {'description': 'Translate a Greek bible '
                                                'verse: Greek bible text must '
                                                'be given',
                                 'name': 'translate_greek_bible_verse',
                                 'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                     'type': 'object'},
                                                                           'type': 'array'}},
                                                'required': ['request'],
                                                'type': 'object'}},
 'translate_hebrew_bible_verse': {'description': 'Translate a Hebrew bible '
                                                 'verse; Hebrew bible text '
                                                 'must be given',
                                  'name': 'translate_hebrew_bible_verse',
                                  'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                      'type': 'object'},
                                                                            'type': 'array'}},
                                                 'required': ['request'],
                                                 'type': 'object'}},
 'write_bible_applications': {'description': 'Provide detailed applications of '
                                             'a bible passages; bible book / '
                                             'chapter / passage / reference(s) '
                                             'must be given',
                              'name': 'write_bible_applications',
                              'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                  'type': 'object'},
                                                                        'type': 'array'}},
                                             'required': ['request'],
                                             'type': 'object'}},
 'write_bible_book_introduction': {'description': 'Write a detailed '
                                                  'introduction on a book in '
                                                  'the bible; bible book must '
                                                  'be given',
                                   'name': 'write_bible_book_introduction',
                                   'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                       'type': 'object'},
                                                                             'type': 'array'}},
                                                  'required': ['request'],
                                                  'type': 'object'}},
 'write_bible_canonical_context': {'description': 'Write about canonical '
                                                  'context of a bible book / '
                                                  'chapter / passage; bible '
                                                  'book / chapter / passage / '
                                                  'reference(s) must be given',
                                   'name': 'write_bible_canonical_context',
                                   'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                       'type': 'object'},
                                                                             'type': 'array'}},
                                                  'required': ['request'],
                                                  'type': 'object'}},
 'write_bible_chapter_summary': {'description': 'Write a detailed '
                                                'interpretation on a bible '
                                                'chapter; a bible chapter must '
                                                'be given',
                                 'name': 'write_bible_chapter_summary',
                                 'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                     'type': 'object'},
                                                                           'type': 'array'}},
                                                'required': ['request'],
                                                'type': 'object'}},
 'write_bible_character_study': {'description': 'Write comprehensive '
                                                'information on a given bible '
                                                'character in the bible; a '
                                                'bible character name must be '
                                                'given',
                                 'name': 'write_bible_character_study',
                                 'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                     'type': 'object'},
                                                                           'type': 'array'}},
                                                'required': ['request'],
                                                'type': 'object'}},
 'write_bible_devotion': {'description': 'Write a devotion on a bible passage; '
                                         'bible book / chapter / passage / '
                                         'reference(s) must be given',
                          'name': 'write_bible_devotion',
                          'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                              'type': 'object'},
                                                                    'type': 'array'}},
                                         'required': ['request'],
                                         'type': 'object'}},
 'write_bible_insights': {'description': 'Write exegetical insights in detail '
                                         'on a bible passage; bible book / '
                                         'chapter / passage / reference(s) '
                                         'must be given',
                          'name': 'write_bible_insights',
                          'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                              'type': 'object'},
                                                                    'type': 'array'}},
                                         'required': ['request'],
                                         'type': 'object'}},
 'write_bible_location_study': {'description': 'write comprehensive '
                                               'information on a bible '
                                               'location; a bible location '
                                               'name must be given',
                                'name': 'write_bible_location_study',
                                'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                    'type': 'object'},
                                                                          'type': 'array'}},
                                               'required': ['request'],
                                               'type': 'object'}},
 'write_bible_outline': {'description': 'provide a detailed outline of a bible '
                                        'book / chapter / passage; bible book '
                                        '/ chapter / passage / reference(s) '
                                        'must be given',
                         'name': 'write_bible_outline',
                         'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                             'type': 'object'},
                                                                   'type': 'array'}},
                                        'required': ['request'],
                                        'type': 'object'}},
 'write_bible_perspectives': {'description': 'Write biblical perspectives and '
                                             'principles in relation to the '
                                             'user content',
                              'name': 'write_bible_perspectives',
                              'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                  'type': 'object'},
                                                                        'type': 'array'}},
                                             'required': ['request'],
                                             'type': 'object'}},
 'write_bible_prayer': {'description': 'Write a prayer pertaining to the user '
                                       'content in reference to the Bible',
                        'name': 'write_bible_prayer',
                        'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                            'type': 'object'},
                                                                  'type': 'array'}},
                                       'required': ['request'],
                                       'type': 'object'}},
 'write_bible_questions': {'description': 'Write thought-provoking questions '
                                          'for bible study group discussion; '
                                          'bible book / chapter / passage / '
                                          'reference(s) must be given',
                           'name': 'write_bible_questions',
                           'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                               'type': 'object'},
                                                                     'type': 'array'}},
                                          'required': ['request'],
                                          'type': 'object'}},
 'write_bible_related_summary': {'description': 'Write a summary on the '
                                                'user-given content in '
                                                'reference to the Bible',
                                 'name': 'write_bible_related_summary',
                                 'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                     'type': 'object'},
                                                                           'type': 'array'}},
                                                'required': ['request'],
                                                'type': 'object'}},
 'write_bible_sermon': {'description': 'Write a bible sermon based on a bible '
                                       'passage; bible book / chapter / '
                                       'passage / reference(s) must be given',
                        'name': 'write_bible_sermon',
                        'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                            'type': 'object'},
                                                                  'type': 'array'}},
                                       'required': ['request'],
                                       'type': 'object'}},
 'write_bible_theology': {'description': 'write the theological messages '
                                         'conveyed in the user-given content, '
                                         'in reference to the Bible',
                          'name': 'write_bible_theology',
                          'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                              'type': 'object'},
                                                                    'type': 'array'}},
                                         'required': ['request'],
                                         'type': 'object'}},
 'write_bible_thought_progression': {'description': 'write Bible Thought '
                                                    'Progression of a bible '
                                                    'book / chapter / passage; '
                                                    'bible book / chapter / '
                                                    'passage / reference(s) '
                                                    'must be given',
                                     'name': 'write_bible_thought_progression',
                                     'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                         'type': 'object'},
                                                                               'type': 'array'}},
                                                    'required': ['request'],
                                                    'type': 'object'}},
 'write_new_testament_highlights': {'description': 'Write Highlights in a New '
                                                   'Testament passage in the '
                                                   'bible; new testament bible '
                                                   'book / chapter / passage / '
                                                   'reference(s) must be given',
                                    'name': 'write_new_testament_highlights',
                                    'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                        'type': 'object'},
                                                                              'type': 'array'}},
                                                   'required': ['request'],
                                                   'type': 'object'}},
 'write_new_testament_historical_context': {'description': 'write the Bible '
                                                           'Historical Context '
                                                           'of a New Testament '
                                                           'passage in the '
                                                           'bible; new '
                                                           'testament bible '
                                                           'book / chapter / '
                                                           'passage / '
                                                           'reference(s) must '
                                                           'be given',
                                            'name': 'write_new_testament_historical_context',
                                            'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                                'type': 'object'},
                                                                                      'type': 'array'}},
                                                           'required': ['request'],
                                                           'type': 'object'}},
 'write_old_testament_highlights': {'description': 'Write Highlights in a Old '
                                                   'Testament passage in the '
                                                   'bible; old testament bible '
                                                   'book / chapter / passage / '
                                                   'reference(s) must be given',
                                    'name': 'write_old_testament_highlights',
                                    'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                        'type': 'object'},
                                                                              'type': 'array'}},
                                                   'required': ['request'],
                                                   'type': 'object'}},
 'write_old_testament_historical_context': {'description': 'write the Bible '
                                                           'Historical Context '
                                                           'of a Old Testament '
                                                           'passage in the '
                                                           'bible; old '
                                                           'testament bible '
                                                           'book / chapter / '
                                                           'passage / '
                                                           'reference(s) must '
                                                           'be given',
                                            'name': 'write_old_testament_historical_context',
                                            'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                                'type': 'object'},
                                                                                      'type': 'array'}},
                                                           'required': ['request'],
                                                           'type': 'object'}},
 'write_pastor_prayer': {'description': 'write a prayer, out of a church '
                                        'pastor heart, based on user input',
                         'name': 'write_pastor_prayer',
                         'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                             'type': 'object'},
                                                                   'type': 'array'}},
                                        'required': ['request'],
                                        'type': 'object'}},
 'write_short_bible_prayer': {'description': 'Write a short prayer, in one '
                                             'paragraph only, pertaining to '
                                             'the user content in reference to '
                                             'the Bible',
                              'name': 'write_short_bible_prayer',
                              'parameters': {'properties': {'request': {'items': {'additionalProperties': True,
                                                                                  'type': 'object'},
                                                                        'type': 'array'}},
                                             'required': ['request'],
                                             'type': 'object'}}}