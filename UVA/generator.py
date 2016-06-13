import re

src = [i.strip().split(',')[0] for i in open('Rice_Type').readlines()]
tagList = set()
tagSet = set()
for s in src:
    #print s, '-->',
    s = re.sub('[0-9]', '_', s)
    s = re.sub('\s', '_', s)
    s = re.sub('(\bHW\b)', r'_\1_', s)
    s = re.sub('(VAV)', r'_\1_', s)
    s = re.sub('([A-Z]{1}[a-z]+|[A-Z]{3})', r'_\1', s)
    s = re.sub('^_+|_+$', '', s)
    s = re.split('_+', s)
    tagList |= set(s)
    #print s
    tagSet.add('_'.join(s))
    #raw_input()

out = open('tagList','wb')
for tag in sorted(tagList):
    print >> out, tag
out.close()

out = open('tagSet','wb')
for tag in sorted(tagSet):
    print >> out, tag
out.close()
