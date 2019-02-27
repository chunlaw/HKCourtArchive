# -*- coding: UTF-8 -*-
import sys
import json
import re
import requests
from bs4 import BeautifulSoup
from html_table_extractor.extractor import Extractor

def printJson(obj):
    print json.dumps(obj, ensure_ascii=False, indent=4)

class CourtParser:
    headers = []

    def parseHeader(self, table):
        if "案件編號" in str(table) or "案件號碼" in str(table):
            extractor = Extractor( str(table), transformer=unicode)
            extractor.parse()
            headerTable = extractor.return_list()
            for i in xrange(0,len(headerTable)):
                if (''.join(headerTable[i])).find(u'案件號碼') != -1 or (''.join(headerTable[i])).find(u'案件編號') != -1:
                    self.headers = headerTable[i]
            self.headers = self.unique(self.headers)
            for i in xrange(0, len(self.headers)):
                self.headers[i] = re.sub('[A-Za-z]', '', self.headers[i]).strip()       

    def parseTable(self, table):
        self.parseHeader(table)
        # skip if header not found
        if self.headers == []:
            return []

        # parse the table, split merged cell and fill in value
        extractor = Extractor( str(table), transformer=unicode)
        extractor.parse()
        raw_data = extractor.return_list()

        # fill the empty cell by previous row value
        for i in xrange(0,len(raw_data)):
            for j in xrange(0, len(raw_data[i])):
                if raw_data[i][j].strip() == '':
                    raw_data[i][j] = raw_data[i-1][j]
        
        # select rows if there time qualifier appeared 
        raw_data = [a for a in raw_data if (''.join(a)).find(u'上午') != -1 or (''.join(a)).find(u'下午') != -1]

        # assigning columns with header as key
        data = []
        # printJson( self.headers )
        for i in xrange(0,len(raw_data)):
            data.append({})
            raw_data[i] = self.unique (raw_data[i])   # handle colspan here
            for j in xrange(0, len(raw_data[i])):       
                print j, raw_data[i][j]
                data[i][self.headers[j]] = raw_data[i][j]

        # mergeing cells content if the case no. is the same
        content = []
        for i in xrange(0, len(data)):
            if not ( u'案件號碼' in data[i] or u'案件編號' in data[i]):
                continue
            if content == [] or \
                ( u'案件號碼' in data[i] and content[-1][u'案件號碼'].strip() != data[i][u'案件號碼'].strip() and content[-1][u'案件號碼'].strip().strip(u'─') != '' ) or \
                ( u'案件編號' in data[i] and content[-1][u'案件編號'].strip() != data[i][u'案件編號'].strip() and content[-1][u'案件編號'].strip().strip(u'─') != '' ):
                content.append(data[i])
            else:
                print json.dumps(content[-1], ensure_ascii=False, indent=4)
                print json.dumps(data[i], ensure_ascii=False, indent=4)
                for k, v in data[i].iteritems():
                    print k
                    if content[-1][k] != data[i][k]:
                        content[-1][k] += data[i][k]

        # done
        return content

    def parseSite(self,htmlText):
        soup = BeautifulSoup( htmlText, 'html.parser')
        tables = soup.find_all('table')
        # exit if no table
        if len(tables) == 0:
            return []
        contents = []
        for table in tables:
            content = self.parseTable(table)
            if content != []:
                contents.append(content)
        return contents

    def unique(self, sequence):
        ret = [sequence[i] for i in xrange(1,len(sequence)) if not ( sequence[i-1] == sequence[i] )]
        return [sequence[1]] + ret

codes = ["cfa","cacfi","hcmc","mcl","bp","clpi","clcmc","crhpi","cwup","mia","otd","o14","ct","lands","dc","dcmc","etnmag","kcmag","ktmag","wkmag","stmag","flmag","tmmag","crc","lt","smt","oat"]
special_codes = ['fmc'] # TODO handle this
url_base = "https://e-services.judiciary.hk/dcl/view.jsp"
url_header = {'User-Agent': 'Mozilla/5.0'}

text = ''
if len(sys.argv) == 2:
    f = open(sys.argv[1],'r')
    text = f.read()
    cp = CourtParser()
    print json.dumps(cp.parseSite(text), ensure_ascii=False, indent=4)
else:
    cases = []
    # traverse all court codes
    for code in codes:
        code = code.upper()
        r = requests.get(url_base, headers = url_header, params = {"lang": "en", 'date': '25022019', 'court': code})
        text = r.text
        cp = CourtParser()
        print r.url
        cases.append([code, cp.parseSite(text)])
    print json.dumps(cases, ensure_ascii=False, indent=4)
