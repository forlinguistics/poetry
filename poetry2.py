import string
import prosodic as p
from nltk.tokenize import word_tokenize
import nltk
from nltk.stem import WordNetLemmatizer
import pronouncing
import json

lem = WordNetLemmatizer()

"""
returns meter or ??? if it cannot be produced
"""


def meters(line):
    p.config['print_to_screen'] = False
    final_jsons = []
    mline = p.Text(line)
    mline.parse()
    i = mline.bestParses()
    final_json = {}
    if i != [] and i[0] is not None:

        meter = i[0].str_meter()
        final_json['meter'] = meter

        # final_json.clear()
    else:
        final_json['meter'] = '???'

    return final_json

"""
returns rhyme scheme
"""

def rhyme_scheme(lines):
    scheme = '0'
    i = 1
    r_words = {}
    words = word_tokenize(lines[0])
    if words[-1] in string.punctuation or words[-1] == '...':
        r_word = words[-2]
    else:
        r_word = words[-1]
    r_words[r_word] = 0

    while i < len(lines):
        words = word_tokenize(lines[i])
        if words[-1] in string.punctuation or words[-1] == '...':
            r_word = words[-2]
        else:
            r_word = words[-1]
        rhymes = pronouncing.rhymes(r_word)
        new_rhyme = True
        for j in r_words.keys():
            if j in rhymes:
                scheme = scheme + str(r_words[j])
                new_rhyme = False
        if new_rhyme:
            r_words[r_word] = len(r_words)
            scheme = scheme + str(r_words[r_word])
        i += 1
    return scheme

"""
creates tsakorpus json
"""

def tsa_json(file_name):
    text_dic = {}
    txt_file = file_name
    author = txt_file.split('_')[0]
    json_name = txt_file.split('_')[1]
    json_name = json_name.lower().replace(' ', '_')
    json_name = json_name.replace('txt', 'json')

    with open(txt_file, encoding='utf-8') as txt:
        lines = txt.readlines()
    lines = [x.strip() for x in lines]
    text_dic['meta'] = {}
    text_dic['meta']['filename'] = json_name
    text_dic['meta']['title'] = lines[0]
    text_dic['meta']['author'] = author
    text_dic['meta']['language'] = 'English'
    text_dic['meta']['school/period'] = 'proto'  # manually
    body = lines[1:]
    text = []
    stanza = 0
    num_of_stanzas = 1
    first_stanza = []
    for line in body:
        if line == '':
            num_of_stanzas += 1
            stanza += 1
            continue
        if stanza == 0:
            first_stanza.append(line)
        line = line.replace('’', '\'')
        words = word_tokenize(line)
        line_dict = {}
        line_dict['text '] = line
        wcnt = 0
        cnt = 0
        words_array = []
        meta = meters(line)
        meta['stanza'] = str(stanza)
        for word in words:
            word_dict = {}
            word_dict['wf'] = word
            if word in string.punctuation or word == '’':
                word_dict['wtype'] = 'punct'
            else:
                word_dict['wtype'] = 'word'
            word_dict['off_start'] = cnt
            cnt += len(word)
            word_dict['off_end'] = cnt
            word_dict['sentence_index'] = wcnt
            wcnt += 1
            word_dict['next_word'] = wcnt
            if word_dict['wtype'] == 'word':
                ana = []
                ana_dict = {}
                ana_dict['lex'] = lem.lemmatize(word)
                ana_dict['gr.pos'] = nltk.pos_tag([word])[0][1]
                word_dict['ana'] = ana_dict
            words_array.append(word_dict)
        line_dict['words'] = words_array
        line_dict['lang'] = 1
        line_dict['meta'] = meta
        text.append(line_dict)
    text_dic['sentences'] = text
    text_dic['meta']['number_of_stanzas'] = str(num_of_stanzas)
    text_dic['meta']['has_rhyme'] = 'True'
    if text_dic['meta']['has_rhyme'] == 'True':
        text_dic['meta']['rhyme_scheme'] = rhyme_scheme(first_stanza)
    else:
        text_dic['meta']['rhyme_scheme'] = 'None'

    with open(json_name, 'w') as fp:
        json.dump(text_dic, fp)
