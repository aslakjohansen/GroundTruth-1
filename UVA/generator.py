import re
import csv

src = [i.strip().split(',')[0] for i in open('Rice_Type').readlines()]
tagList = set()
tagSet = set()
output = list()
for s in src:
    #print s, '-->',
    tmp = []
    tmp.append(s)
    identifier = re.findall('[0-9]+', s)
    s = re.sub('[0-9]', '_', s)
    s = re.sub('\s', '_', s)
    s = re.sub('(\bHW\b)', r'_\1_', s)
    s = re.sub('(VAV)', r'_\1_', s)
    s = re.sub('([A-Z]{1}[a-z]+|[A-Z]{3})', r'_\1', s)
    s = re.sub('^_+|_+$', '', s)
    s = re.split('_+', s)
    tagList |= set(s)
    tagSet.add('_'.join(s))
    #tmp.append('_'.join(ss.lower() for ss in s))
    tmp.append('_'.join(s))
    tmp.extend(identifier)
    output.append(tmp)

out = open('tagList','wb')
for tag in sorted(tagList):
    print >> out, tag
out.close()

out = open('tagSet','wb')
for tag in sorted(tagSet):
    print >> out, tag
out.close()


out = open('point.csv', 'wb')
wr = csv.writer(out, quoting=csv.QUOTE_ALL)
#wr.writerow('original point name', 'tagsets','identifier')
wr.writerows(output[2:])
