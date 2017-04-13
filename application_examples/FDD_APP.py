
# coding: utf-8

# In[1]:

# read required inputs from excel
import pandas as pd
pt = pd.read_excel('names.xlsx')


# The rule-based FDD application requires the following minimal inputs from AHUs in order to run the rules:

# In[2]:

pd.set_option('max_colwidth',80)
pt


# In[3]:

points_map = {}
for row in pt.iterrows():
    points_map[str(row[1][2])] = str(row[1][1]).split('/')


# In[4]:

points_map


# In[5]:

import rdflib

g = rdflib.Graph()
g.parse('../CMU-Yuvraj/GHCYuvraj_brick.ttl', format='turtle')
# g.parse('../IBM/IBM_B3.ttl', format='turtle')
# g.parse('../UCSD/EBU3B/ebu3b_brick.ttl', format='turtle')
# g.parse('example_building.ttl', format='turtle')
# g.parse('../SDU/', format='turtle')

BRICKFRAME = rdflib.Namespace('https://brickschema.org/schema/1.0.1/BrickFrame#')
g.bind( 'bf', BRICKFRAME)
BRICK = rdflib.Namespace('https://brickschema.org/schema/1.0.1/Brick#')
g.bind('brick', BRICK)


# In[6]:

# query goes here
def get_points(acronym,brick_name,g):
    res = g.query("""
    SELECT ?%s
    WHERE {
        ?%s rdf:type brick:%s .
        ?ahu rdf:type brick:AHU .
        ?%s bf:isPointOf ?ahu .
    }
    """ % (acronym,acronym,brick_name,acronym))
    
    return list(res)


# In[7]:

from collections import defaultdict

Result = defaultdict(list)

for acr,brk_names in points_map.items():
    print "Runing query for %s ......" % acr
    for brk in brk_names:
        res = get_points(acr,brk,g)
        print "\tNumber of points found for %s : %d" % (brk,len(res))
        Result[acr].append(res)


# In[8]:

print "units containing out side air temperature sensor:"
for i in [str(i[0]) for i in Result['OAT'][0]]:
    print i

