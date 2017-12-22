#Util function is defined here
import json
from collections import namedtuple

def str2Object(data):
    x = json.loads(data)
    return x


def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
