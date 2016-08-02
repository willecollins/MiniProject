#!/usr/bin/python
import sys
import boto3
import botocore
import time
import subprocess
import logging



# Initialize variables from command line

MyStackName = str(sys.argv[1])
MyOpsWorksStackName = str(sys.argv[2])
TemplatePath = str(sys.argv[3])
OpsWorksTemplatePath = str(sys.argv[4])
RegionName = str(sys.argv[5])
SSHKey = str(sys.argv[6])


#Hard-coded variables - to be changed in next version

NatInstanceType = "t2.micro"
Parameters = "[{'ParameterKey': 'NATInstanceType', 'ParameterValue: 't2.micro']"
tagdict = ""

#Upload Template to S3

#Hard coded Random Bucknet Name
BucketName = "dkr4543kd3---mini-project"
s3=boto3.resource('s3')

#Create the bucket if it doesn't already exist

try:
    s3.meta.client.head_bucket(Bucket='mybucket')
except botocore.exceptions.ClientError as e:
    # If a client error is thrown, then check that it was a 404 error.
    # If it was a 404 error, then the bucket does not exist.
    error_code = int(e.response['Error']['Code'])
    if error_code == 404:
        exists = False
    s3.create_bucket(Bucket=BucketName)
#Cloud Formation Template
s3.Bucket(BucketName).upload_file(TemplatePath, 'MyTemplate')
#OpsWorks Template
s3.Bucket(BucketName).upload_file(OpsWorksTemplatePath, 'OpsWorksTemplate')

#Create TemplateURL for Cloudformation stack
MyTemplateURL = "https://s3" + ".amazonaws.com/" + BucketName + "/MyTemplate"

#CreateTemplateURL for OpsWorks stack
OpsWorksTemplateURL = "https://s3"  + ".amazonaws.com/" + BucketName + "/OpsWorksTemplate"


#Create a Cloud Formation Connection
Client = boto3.client(service_name='cloudformation', region_name=RegionName)

#Function to Check for the existence of a an existing template
def StackExist(str):
    stacks = Client.list_stacks(StackStatusFilter=['CREATE_COMPLETE'])['StackSummaries']
    names = [stack['StackName'] for stack in stacks]
    DoesExist = 0
    if str in (names):
       DoesExist = 1
    return DoesExist

#Check to see if Stack Already Exists

if StackExist(MyOpsWorksStackName) == 0:
    print('Creating Stack')
    #try:
    stackID = Client.create_stack(
 		   StackName=MyStackName,
 		   # template_body=json,
 		   TemplateURL=MyTemplateURL,
 		   #Parameters=Parameters,
 		   DisableRollback=False,
 		   TimeoutInMinutes=30,
 		   #Capabilities=None,
 		   #Tags=tagdict
 		)
else:
    print('Updating Stack')
    # try:
    stackID = Client.update_stack(
            StackName=MyStackName,
            # template_body=json,
            TemplateURL=MyTemplateURL,
            # Parameters=Parameters,
            # Capabilities=None,
            # Tags=tagdict
        )
#Wait Until Stack is complete
waiter = Client.get_waiter('stack_create_complete')
waiter.wait(StackName=MyStackName)

#Get Information about the newly created stack
cloudformation = boto3.resource('cloudformation')
stack = cloudformation.Stack(MyStackName)
outputs = stack.outputs

#Set Values to pass to Next stack
for dict in outputs:

     if dict['OutputKey'] == 'PrivateSubnets':
             PrivateSubnet = dict['OutputValue']
     elif dict['OutputKey'] == 'PublicSubnets':
             PublicSubnet = dict['OutputValue']
     elif (dict['OutputKey']) == 'VPC':
             VPCId = dict['OutputValue']
     elif (dict['OutputKey']) == 'LoadBalancer':
            LoadBalancer = dict['OutputValue']

 #Iterate Through List and get the


print('VPC Created')
#except Exception as e:




#Create Opsworks Stack
#try:
myParam = [{"ParameterKey": "VPCId", "ParameterValue":  VPCId}, {"ParameterKey": "PublicSubnets","ParameterValue": PublicSubnet},
           { "ParameterKey": "DefSubnet", "ParameterValue": PublicSubnet}, {"ParameterKey": "KeyName", "ParameterValue": SSHKey}]

#Check to see if specified Opsworks stack exists
if StackExist(MyOpsWorksStackName) == 0:
    print('Creating OpsWorks Stack')
    stackID2 = Client.create_stack(
 		   StackName=MyOpsWorksStackName,
 		   TemplateURL=OpsWorksTemplateURL,
 		   Parameters=myParam,
 		   DisableRollback=False,
 		   TimeoutInMinutes=30
		   #Capabilities=['CAPABILITY_IAM']
           #Tags=tagdict
    )
else:
    print('Updating OpsWorks Stack')
    stackID2 = Client.update_stack(
        StackName='OpsWorksTestStack',
        TemplateURL=OpsWorksTemplateURL,
        Parameters=myParam
        #Capabilities=['CAPABILITY_IAM']
        # Tags=tagdict
 		)

#Wait Until Stack is complete
waiter2 = Client.get_waiter('stack_create_complete')
waiter2.wait(StackName=MyOpsWorksStackName)

#Client2 = boto3.client(service_name='ec2', region_name='us-west-2')
time.sleep(180)

#GetPublicAddreess
Client3 = boto3.client(service_name='ec2', region_name=RegionName)
RunningInstances = Client3.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
InstanceList = (RunningInstances["Reservations"])


for instance in InstanceList:
   if "static1" in str(instance):
      for key, value in instance.items():
            if key == 'Instances':
                   for i in value:
                       for key2, value2 in i.items():
                          if key2 == 'PublicIpAddress':
                            PublicIpAddress = value2
                            print("should have gotten the ip address")

print (PublicIpAddress)

#Run Server Tests
TestCommand = 'inspec exec SimpleTest.rb -t ssh://ec2-user@' + PublicIpAddress + ' --key-files ' + SSHKey + '.pem'
subprocess.call (TestCommand, shell=True)





#print(DnsName)
print('Program Complete')
     #events = Client.describe_stack_events( stackID, None )
