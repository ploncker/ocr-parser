#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 16:24:59 2021

@author: ross
"""
#from ocrp.aws.trp import *
#from ocrp.aws import trp_utils
from . import trp
from .call_textract import textract
from .paragraph_detector import extract_paragraphs