import boto3
import sys
import json
import time
from cfn_flip import flip, to_yaml, to_json

cfnclient = boto3.client('cloudformation', region_name='us-east-1')

try:
    stacks = cfnclient.describe_stacks(
        StackName=sys.argv[1]
    )['Stacks']
except:
    print("Could not find stack")
    quit()

original_stack_id = stacks[0]['StackId']
original_stack_name = stacks[0]['StackName']

original_template = cfnclient.get_template(
    StackName=original_stack_id,
    TemplateStage='Processed'
)['TemplateBody']

print("Found stack, detecting drift...")

stack_drift_detection_id = cfnclient.detect_stack_drift(
    StackName=original_stack_id
)['StackDriftDetectionId']

stack_drift_detection_status = cfnclient.describe_stack_drift_detection_status( # no waiter :(
    StackDriftDetectionId=stack_drift_detection_id
)
while stack_drift_detection_status['DetectionStatus'] == "DETECTION_IN_PROGRESS":
    time.sleep(5)
    stack_drift_detection_status = cfnclient.describe_stack_drift_detection_status(
        StackDriftDetectionId=stack_drift_detection_id
    )

if stack_drift_detection_status['DetectionStatus'] != "DETECTION_COMPLETE" or stack_drift_detection_status['StackDriftStatus'] != "DRIFTED":
    if stack_drift_detection_status['StackDriftStatus'] == "IN_SYNC":
        print("Could not find any drifted resources")
    else:
        print("Could not determine drift results")
    quit()

resource_drifts = []
resource_drifts_result = cfnclient.describe_stack_resource_drifts(
    StackName=original_stack_id,
    StackResourceDriftStatusFilters=[
        'MODIFIED',
        'DELETED'
    ],
    MaxResults=100
)
resource_drifts += resource_drifts_result['StackResourceDrifts']
while 'NextToken' in resource_drifts_result:
    resource_drifts_result = cfnclient.describe_stack_resource_drifts(
        StackName=original_stack_id,
        StackResourceDriftStatusFilters=[
            'MODIFIED',
            'DELETED'
        ],
        NextToken=resource_drifts_result['NextToken'],
        MaxResults=100
    )
    resource_drifts += resource_drifts_result['StackResourceDrifts']

template = json.loads(to_json(original_template))

for k, v in template['Resources'].items():
    template['Resources'][k]['DeletionPolicy'] = 'Retain'

print("Drift detected, setting resource retention...")

cfnclient.update_stack(
    StackName=original_stack_id,
    TemplateBody=json.dumps(template),
    Capabilities=[
        'CAPABILITY_NAMED_IAM',
        'CAPABILITY_AUTO_EXPAND'
    ]
)

waiter = cfnclient.get_waiter('stack_update_complete')
waiter.wait(
    StackName=original_stack_id,
    WaiterConfig={
        'Delay': 10,
        'MaxAttempts': 360
    }
)

print("Deleting stack (whilst retaining resources!)...")

cfnclient.delete_stack(
    StackName=original_stack_id
)

waiter = cfnclient.get_waiter('stack_delete_complete')
waiter.wait(
    StackName=original_stack_id,
    WaiterConfig={
        'Delay': 10,
        'MaxAttempts': 360
    }
)

import_resources = []
for drifted_resource in resource_drifts:
    if 'PhysicalResourceIdContext' in drifted_resource:
        print(drifted_resource['PhysicalResourceIdContext'])
    if 'PhysicalResourceId' in drifted_resource:
        print(drifted_resource['PhysicalResourceId'])

    template['Resources'][drifted_resource['LogicalResourceId']]['Properties'] = json.loads(drifted_resource['ActualProperties'])
    template['Resources'][drifted_resource['LogicalResourceId']]['DeletionPolicy'] = 'Retain'

    import_resources.append({
        'ResourceType': drifted_resource['ResourceType'],
        'LogicalResourceId': drifted_resource['LogicalResourceId'],
        'ResourceIdentifier': {
            'RoleName': drifted_resource['PhysicalResourceId'] # TODO
        }
    })

print("Recreating stack with current state...")

change_set_name = 'Drift-Remediation-' + str(int(time.time()))
new_stack_id = cfnclient.create_change_set(
    StackName=original_stack_name,
    ChangeSetName=change_set_name,
    TemplateBody=json.dumps(template),
    ChangeSetType='IMPORT',
    Capabilities=[
        'CAPABILITY_NAMED_IAM',
        'CAPABILITY_AUTO_EXPAND'
    ],
    ResourcesToImport=import_resources
)['StackId']

waiter = cfnclient.get_waiter('change_set_create_complete')
waiter.wait(
    StackName=new_stack_id,
    ChangeSetName=change_set_name,
    WaiterConfig={
        'Delay': 10,
        'MaxAttempts': 360
    }
)

cfnclient.execute_change_set(
    ChangeSetName=change_set_name,
    StackName=new_stack_id
)

waiter = cfnclient.get_waiter('stack_import_complete')
waiter.wait(
    StackName=new_stack_id,
    WaiterConfig={
        'Delay': 10,
        'MaxAttempts': 360
    }
)

print("Remediating drift...")

cfnclient.update_stack(
    StackName=original_stack_name,
    TemplateBody=original_template,
    Capabilities=[
        'CAPABILITY_NAMED_IAM',
        'CAPABILITY_AUTO_EXPAND'
    ]
)

waiter = cfnclient.get_waiter('stack_update_complete')
waiter.wait(
    StackName=new_stack_id,
    WaiterConfig={
        'Delay': 10,
        'MaxAttempts': 360
    }
)

print("Succcessfully remediated drift")
