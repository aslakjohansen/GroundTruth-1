import re

src = [i.strip().split(',')[0] for i in open('Rice_Type').readlines()]
for s in src:
    print s, '---->',
    s = re.sub('\s|[0-9]', '', s)
    s = re.sub('([A-Z][a-z]+)',r'_\1',s)
    print s
