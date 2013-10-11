#!/usr/bin/python

import os
import os.path
import sys
import logging

def normalise(filename):
    return ' '.join(filename.replace('_', '.').replace('-', '.').split('.')[:-1])

class Entry(object):
    def __init__(self, label, full_path):
        self.label = label
        self.full_path = full_path
        self.tags = set()

    def add_tag(self, tag):
        self.tags.add(tag)

    def describe(self):
        return self.label + '(@ ' + self.full_path + ') - ' + str(self.tags)

class MediaIndex(object):
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.search_terms = set()
        self.index = dict()
        self.entries = set()
        self.base_dir_entry_length = len(os.path.abspath(self.base_dir).split('/'))

    def find(self, substr):
        matching_tags = set()
        for tag in self.search_terms:
            if tag.find(substr) > -1:
                matching_tags.add(tag)

        return matching_tags

    def get_entries(self, tag):
        matching_entries = set()
        if tag in self.index.keys():
            for entry in self.index[tag]:
                matching_entries.add(entry)

        return matching_entries

    def describe(self):
        for search_term in self.search_terms:
            print 'tag: ' + search_term
            for item in self.index[search_term] : print item.describe()

    def generate(self):
        for search_term in self.search_terms:
            entries_for_search_term = set()
            for entry in self.entries:
                if search_term in entry.tags:
                    entries_for_search_term.add(entry)

            self.index[search_term] = entries_for_search_term

    def build(self):
        num_files = 0
        for root, dirs, files in os.walk(self.base_dir):
            for filename in files:
                file_tag = normalise(filename)
                #self.search_terms.add(file_tag)
                file_tags = set()
                for dir_node in os.path.abspath(root).split('/')[self.base_dir_entry_length:]:
                    file_tags.add(dir_node)
                entry = Entry(file_tag, os.path.abspath(root + '/' + filename))
                for tag in file_tags:
                    entry.add_tag(tag)
                    self.search_terms.add(tag)
                self.entries.add(entry)
                num_files += 1
                if num_files % 100 == 0:
                    print 'processed {0} files'.format(num_files)
                    logging.info('processed {0} files'.format(num_files))

        self.generate()


if '__main__' == __name__:
    mediaIndex = MediaIndex(sys.argv[1])
    mediaIndex.build()


    tag = mediaIndex.find(sys.argv[2]).pop()

    print 'matching tag: ' + tag

    entries = mediaIndex.get_entries(tag)

    for entry in entries:
        print entry.describe()
