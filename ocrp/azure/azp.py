# -*- coding: utf-8 -*-



import json


class dict2obj(object):
    """
    https://stackoverflow.com/questions/1305532/how-to-convert-a-nested-python-dict-to-object
    """
    
    def __init__(self, obj):
        for name, value in obj.items():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)): 
            return type(value)([self._wrap(v) for v in value])
        else:
            return dict2obj(value) if isinstance(value, dict) else value
        
    # def __repr__(self):
    #     return '{%s}' % str(', '.join('%s : %s' % (k, repr(v)) for (k, v) in self.__dict__.items()))
    
    def __repr__(self): 
        return ("{ " + str(", ".join([f"'{k}': {v}" for k, v in [(k, repr(v)) for (k, v) in self.__dict__.items()]])) + " }")
        

def main(filen):
    with open ( filen,'r') as f:
        data = json.loads(f.read())
        
    s = dict2obj(data)
    
    return s
    
if __name__ == "__main__":
    
    #filen= '/Users/ross/Mirror/GitHub/src/ploncker/ocrp_package/test/data/azure_table.json'
    filen = '../../test/data/azure_table.json'
    #filen = '/Users/ross/GitHub/src/OCR/BoM/demo_data/f68_R038627030_95_0026-redacted.json'
    # import pandas as pd
    # azure = pd.read_json(filen)
    # azure.head()
    
    s = main(filen)
    
                                  

    
