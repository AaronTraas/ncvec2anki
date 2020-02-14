#!/usr/bin/env python3

import codecs
import os
import re
import yaml

INPUT_FILES = ['2020ExtraClassPoolJan22.txt']

TOKEN_SYLLABUS_END = '~~end of question pool syllabus~~'
TOKEN_SUBELEMENT_START = 'SUBELEMENT'

REGEX_SUBELEMENT_TITLE = re.compile(
    'SUBELEMENT (?P<id>[A-Z][0-9]*)[\s,\-]*(?P<title>[^\[]*) \[(?P<exam_questions>[0-9]) Exam Question[s]?[\s,\-]*(?P<groups>[0-9]*) Group[s]?\] ?(?P<questions>[0-9]*)?( Questions)?',
    flags=re.IGNORECASE
)

REGEX_SECTION_TITLE = re.compile(
    '(?P<id>[A-Z][0-9]{1,3}[A-Z]) (?P<title>.*)',
    flags=re.IGNORECASE
)

def split_subelements(text):
    subelements_raw = [TOKEN_SUBELEMENT_START + sub for sub in text.strip().split(TOKEN_SUBELEMENT_START) if sub][1:]

    subelements = []
    for sub in subelements_raw:
        subelements.append([s for s in sub.splitlines() if s.strip()])

    return subelements

def parse_questions(questions_text):
    subelements_raw = split_subelements(questions_text)

    subelements = []
    for sub in subelements_raw:
        new_sub = parse_subelement_title(sub[0])
        subelements.append(new_sub)

    return subelements

def parse_subelement_title(title):
    match = REGEX_SUBELEMENT_TITLE.match(title)
    return {
        'id': match.group('id'),
        'title': match.group('title'),
        'exam_questions': match.group('exam_questions'),
        'groups': match.group('groups'),
        'questions': match.group('questions')
    }

def parse_syllabus_section(section):
    (id, title) = section.split(' ', 1)
    return {'id': id, 'title': title}

def parse_syllabus(syllabus_text):
    subelements_raw = split_subelements(syllabus_text)

    subelements = []
    for sub in subelements_raw:
        new_sub = parse_subelement_title(sub[0])
        new_sub['sections'] = [parse_syllabus_section(s) for s in sub[1:] if s]
        subelements.append(new_sub)

    return subelements

def convert_ncvec_txt_to_dict(ncvec_txt):
    (syllabus_text, questions_text) = ncvec_txt.split(TOKEN_SYLLABUS_END)
    return {
        'syllabus': parse_syllabus(syllabus_text),
        'questions': parse_questions(questions_text)
    }

for input_file_name in INPUT_FILES:
    if os.path.isfile(input_file_name):
        ncvec_text = ""
        with open(input_file_name, errors='ignore') as infile:
            ncvec_text = infile.read()

        test = convert_ncvec_txt_to_dict(ncvec_text)

        output_file_name = os.path.splitext(input_file_name)[0] + '.yml'
        with codecs.open(output_file_name, 'w', 'utf-8') as outfile:
            outfile.write(yaml.dump(test))

