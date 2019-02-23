# -*- coding: UTF-8 -*-
import sys
import json
import re
from bs4 import BeautifulSoup
from html_table_extractor.extractor import Extractor

html_doc = open( sys.argv[1], "r" )
soup = BeautifulSoup( html_doc.read(), 'html.parser')
tables = soup.find_all('table')
if len(tables)<2:
    exit

def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

contents = []
headers = []
for table in tables:
    # parse the data after if the header is set
    if headers:
        extractor = Extractor( str(table), transformer=unicode)
        extractor.parse()
        raw_data = extractor.return_list()
        # augment the empty cell
        for i in xrange(0,len(raw_data)):
            for j in xrange(0, len(raw_data[i])):
                if raw_data[i][j].strip() == '':
                    raw_data[i][j] = raw_data[i-1][j]

        # assigning data with header as key
        data = []
        for i in xrange(0,len(raw_data)):
            data.append({})
            raw_data[i] = unique (raw_data[i])   # handle colspan here
            for j in xrange(0, len(raw_data[i])):       
                data[i][headers[0][j]] = raw_data[i][j]

        # merging cells content
        content = []
        for i in xrange(0, len(data)):
            if not ( u'案件號碼' in data[i] or u'案件編號' in data[i]):
                continue
            if content == [] or \
                ( u'案件號碼' in data[i-1] and data[i-1][u'案件號碼'].strip() != data[i][u'案件號碼'].strip() ) or \
                ( u'案件編號' in data[i-1] and data[i-1][u'案件編號'].strip() != data[i][u'案件編號'].strip() ):
                content.append(data[i])
            else:
                #print data[i-1][u'案件編號'].strip() != data[i][u'案件編號'].strip()
                for k, v in data[i].iteritems():
                    if data[i-1][k] != data[i][k]:
                        content[-1][k] += data[i][k]
        contents.append(content)
        headers = []
    # parse the header
    if "案件編號" in str(table) or "案件號碼" in str(table):
        extractor = Extractor( str(table), transformer=unicode)
        extractor.parse()
        headers = extractor.return_list()
        headers[0] = unique(headers[0])
        for i in xrange(0, len(headers[0])):
            headers[0][i] = re.sub('[A-Za-z]', '', headers[0][i]).strip()


print json.dumps(contents, ensure_ascii=False)
