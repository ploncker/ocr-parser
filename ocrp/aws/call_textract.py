#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 14:45:10 2021

@author: ross
"""
#https://github.com/aws-samples/amazon-textract-code-samples/blob/master/python/12-pdf-text.py

import boto3
import time
import json
#import ocrp
#from ocrp.aws.config import aws_config

aws_config =  {
    'region':'',
    'access_key':'',
    'secret_key':''
}



def startJob(client, s3BucketName, objectName, extraction_type='detect'):
    #response = None
    if extraction_type=='analysis':
        jobId = startAnalysisJob(client, s3BucketName, objectName)
        
    else:
        jobId = startDetectionJob(client, s3BucketName, objectName)
    
    return jobId

def startDetectionJob(client, s3BucketName, objectName):
    response = None

    response = client.start_document_text_detection(
        DocumentLocation={
            'S3Object': {
            'Bucket': s3BucketName,
            'Name': objectName
            }
        })
    return response["JobId"]

def startAnalysisJob(client, s3BucketName, objectName):
    response = None

    response = client.start_document_analysis(
        DocumentLocation={
            'S3Object': {
            'Bucket': s3BucketName,
            'Name': objectName
            }
        },
        FeatureTypes = ['TABLES','FORMS']
    )
    return response["JobId"]


def isJobComplete(client, jobId, extraction_type='detect'):
    # For production use cases, use SNS based notification 
    # Details at: https://docs.aws.amazon.com/textract/latest/dg/api-async.html
    if extraction_type=='analysis':
        status = isAnalysisJobComplete(client, jobId)
        
    else:
        status = isDetectionJobComplete(client, jobId)
        
    return status


def isDetectionJobComplete(client, jobId):
    # For production use cases, use SNS based notification 
    # Details at: https://docs.aws.amazon.com/textract/latest/dg/api-async.html
    time.sleep(5)

    response = client.get_document_text_detection(JobId=jobId)
    status = response["JobStatus"]
    print("Job status: {}".format(status))
    while(status == "IN_PROGRESS"):
        time.sleep(5)
        response = client.get_document_text_detection(JobId=jobId)
        status = response["JobStatus"]
        print("Job status: {}".format(status))
    return status

def isAnalysisJobComplete(client, jobId):
    # For production use cases, use SNS based notification 
    # Details at: https://docs.aws.amazon.com/textract/latest/dg/api-async.html
    time.sleep(5)

    response = client.get_document_analysis(JobId=jobId)
    status = response["JobStatus"]
    print("Job status: {}".format(status))
    while(status == "IN_PROGRESS"):
        time.sleep(5)
        response = client.get_document_analysis(JobId=jobId)
        status = response["JobStatus"]
        print("Job status: {}".format(status))
    return status


def getJobResults(client, jobId, extraction_type='detect'):
    
    if extraction_type=='analysis':
        response = getAnalysisJobResults(client, jobId)
        
    else:
        response = getDetectionJobResults(client, jobId)
    
    return response
      
def getDetectionJobResults(client, jobId):
    
    mega_response = client.get_document_text_detection(
            JobId=jobId
        )
    
    nextToken = None
    if('NextToken' in mega_response):
        nextToken = mega_response['NextToken']
    while(nextToken):
        response = client.get_document_text_detection(JobId=jobId, NextToken=nextToken)
        mega_response['Blocks'].extend(response['Blocks'])
        nextToken = None
        if('NextToken' in response):
            nextToken = response['NextToken']
    #doc = trp.Document(mega_response)
    return mega_response

def getAnalysisJobResults(client, jobId):

    mega_response = client.get_document_analysis(
            JobId=jobId
        )
    
    nextToken = None
    if('NextToken' in mega_response):
        nextToken = mega_response['NextToken']
    while(nextToken):
        response = client.get_document_analysis(JobId=jobId, NextToken=nextToken)
        mega_response['Blocks'].extend(response['Blocks'])
        nextToken = None
        if('NextToken' in response):
            nextToken = response['NextToken']
    #doc = trp.Document(mega_response)
    return mega_response
    

def upload_s3(client, file, s3_bucket, object_name):
    

    response = client.upload_file(Filename=file, Bucket=s3_bucket, Key=object_name)
    print('file uploading {0}'.format(response))
    return response
    
    
def write_to_file(response, fname):
    
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=4)
        print('file written', fname)
          
  
def batch_extract_files(path, extraction_type='detect'):

    import os
    
    #import subprocess
    fname = ""
    
    for top, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith('.png'):
                print(filename)
                #download
                s3BucketName = "handwriting-ocr"
                path = 'textract/images/'
                file_n = filename
                jobId = startJob(s3BucketName, path+file_n, extraction_type=extraction_type)
                print("Started job with id: {}".format(jobId))
                status = isJobComplete(jobId, extraction_type=extraction_type)
                
                if status =='SUCCEEDED':
                    response = getJobResults(jobId, extraction_type=extraction_type)
        
                    
                    fname = path + file_n[:-3] + 'json'
                    write_to_file(response, fname)

    return fname


def textract(client, bucket, objectName, extraction_type='detect'): 
    #objectName = pdf.split('/')[-1]
    jobId = startJob(client, bucket, objectName, extraction_type=extraction_type)
    print("Started job with id: {}".format(jobId))

    status = isJobComplete(client, jobId, extraction_type=extraction_type)
    
    if status =='SUCCEEDED':
        response = getJobResults(client, jobId, extraction_type=extraction_type)
        # fname = pdf[:-3] + 'json'
        # write_to_file(response, fname)

            
    return response
    
if __name__ == "__main__":
    
    
    bucket = ""
    

    pdf = '.pdf'
    s3_folder = ''
    
    s3_bucket = bucket + '/' + s3_folder
    object_name = s3_folder + pdf.split('/')[-1]
    
    client = boto3.client('s3', 
                      aws_access_key_id = aws_config['access_key'], 
                      aws_secret_access_key = aws_config['secret_key'],
                      region_name = aws_config['region'],
                            verify = False)
    
    rep = upload_s3(client, pdf, bucket, object_name)
    
    
    client = boto3.client('textract' , 
                      aws_access_key_id = aws_config['access_key'], 
                      aws_secret_access_key = aws_config['secret_key'],
                      region_name = aws_config['region'],
                          verify = False)
    
    response = textract(client, bucket, object_name, extraction_type='detect')
    pdf = '.json'
    write_to_file(response, pdf)
    

    
 