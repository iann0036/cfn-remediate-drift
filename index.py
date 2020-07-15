import boto3
import sys
import json
import time
from collections import OrderedDict
from cfn_flip import flip, to_yaml, to_json

resolve_matches = {}

def resolvePropertyValue(prop, match_resources, replace_values):
    if isinstance(prop, dict):
        if 'Ref' in prop:
            if prop['Ref'] in match_resources:
                if replace_values:
                    return resolve_matches['Ref' + prop['Ref']]
                else:
                    resolve_matches['Ref' + prop['Ref']] = {
                        'Ref': prop['Ref']
                    }
        elif 'Fn::GetAtt' in prop:
            if prop['Fn::GetAtt'][0] in match_resources:
                if replace_values:
                    return resolve_matches['GetAtt' + prop['Fn::GetAtt'][0] + prop['Fn::GetAtt'][1]]
                else:
                    resolve_matches['GetAtt' + prop['Fn::GetAtt'][0] + prop['Fn::GetAtt'][1]] = {
                        'Fn::GetAtt': prop['Fn::GetAtt']
                    }
        elif 'Fn::Sub' in prop:
            pass # TODO
        
        ret = {}
        for k, v in prop.items():
            ret[k] = resolvePropertyValue(v, match_resources, replace_values)
        return ret
    elif isinstance(prop, list) and not isinstance(prop, str):
        ret = []
        for listitem in prop:
            ret.append(resolvePropertyValue(listitem, match_resources, replace_values))
        return ret
    else:
        return prop

empty_template = {
    "Conditions": {
        "FalseCondition": {
            "Fn::Equals": [1, 2]
        }
    },
    "Resources": {
        "PlaceholderResource": {
            "Condition": "FalseCondition",
            "Type": "AWS::S3::Bucket"
        }
    }
}

eligible_import_resources = { # from Former2
    "AWS::ACMPCA::Certificate": {
        "importProperties": [
            "Arn", 
            "CertificateAuthorityArn"
        ]
    }, 
    "AWS::ACMPCA::CertificateAuthority": {
        "importProperties": [
            "Arn"
        ]
    }, 
    "AWS::ACMPCA::CertificateAuthorityActivation": {
        "importProperties": [
            "CertificateAuthorityArn"
        ]
    }, 
    "AWS::AccessAnalyzer::Analyzer": {
        "importProperties": [
            "Arn"
        ]
    }, 
    "AWS::ApiGateway::Authorizer": {
        "importProperties": [
            "RestApiId", 
            "AuthorizerId"
        ]
    }, 
    "AWS::ApiGateway::Deployment": {
        "importProperties": [
            "RestApiId", 
            "DeploymentId"
        ]
    }, 
    "AWS::ApiGateway::Method": {
        "importProperties": [
            "RestApiId", 
            "ResourceId", 
            "HttpMethod"
        ]
    }, 
    "AWS::ApiGateway::Model": {
        "importProperties": [
            "RestApiId", 
            "Name"
        ]
    }, 
    "AWS::ApiGateway::RequestValidator": {
        "importProperties": [
            "RestApiId", 
            "RequestValidatorId"
        ]
    }, 
    "AWS::ApiGateway::Resource": {
        "importProperties": [
            "RestApiId", 
            "ResourceId"
        ]
    }, 
    "AWS::ApiGateway::RestApi": {
        "importProperties": [
            "RestApiId"
        ]
    }, 
    "AWS::ApiGateway::Stage": {
        "importProperties": [
            "RestApiId", 
            "StageName"
        ]
    }, 
    "AWS::Athena::DataCatalog": {
        "importProperties": [
            "Name"
        ]
    }, 
    "AWS::Athena::NamedQuery": {
        "importProperties": [
            "NamedQueryId"
        ]
    }, 
    "AWS::Athena::WorkGroup": {
        "importProperties": [
            "Name"
        ]
    }, 
    "AWS::AutoScaling::AutoScalingGroup": {
        "importProperties": [
            "AutoScalingGroupName"
        ]
    }, 
    "AWS::AutoScaling::LaunchConfiguration": {
        "importProperties": [
            "LaunchConfigurationName"
        ]
    }, 
    "AWS::AutoScaling::LifecycleHook": {
        "importProperties": [
            "AutoScalingGroupName", 
            "LifecycleHookName"
        ]
    }, 
    "AWS::AutoScaling::ScalingPolicy": {
        "importProperties": [
            "PolicyName"
        ]
    }, 
    "AWS::AutoScaling::ScheduledAction": {
        "importProperties": [
            "ScheduledActionName"
        ]
    }, 
    "AWS::CE::CostCategory": {
        "importProperties": [
            "Arn"
        ]
    }, 
    "AWS::Cassandra::Keyspace": {
        "importProperties": [
            "KeyspaceName"
        ]
    }, 
    "AWS::Cassandra::Table": {
        "importProperties": [
            "KeyspaceName", 
            "TableName"
        ]
    }, 
    "AWS::Chatbot::SlackChannelConfiguration": {
        "importProperties": [
            "Arn"
        ]
    }, 
    "AWS::CloudFormation::Stack": {
        "importProperties": [
            "StackId"
        ]
    }, 
    "AWS::CloudTrail::Trail": {
        "importProperties": [
            "TrailName"
        ]
    }, 
    "AWS::CloudWatch::Alarm": {
        "importProperties": [
            "AlarmName"
        ]
    }, 
    "AWS::CloudWatch::CompositeAlarm": {
        "importProperties": [
            "AlarmName"
        ]
    }, 
    "AWS::CodeGuruProfiler::ProfilingGroup": {
        "importProperties": [
            "ProfilingGroupName"
        ]
    }, 
    "AWS::CodeStarConnections::Connection": {
        "importProperties": [
            "ConnectionArn"
        ]
    }, 
    "AWS::Config::ConformancePack": {
        "importProperties": [
            "ConformancePackName"
        ]
    }, 
    "AWS::Config::OrganizationConformancePack": {
        "importProperties": [
            "OrganizationConformancePackName"
        ]
    }, 
    "AWS::Detective::Graph": {
        "importProperties": [
            "Arn"
        ]
    }, 
    "AWS::Detective::MemberInvitation": {
        "importProperties": [
            "GraphArn", 
            "MemberId"
        ]
    }, 
    "AWS::DynamoDB::Table": {
        "importProperties": [
            "TableName"
        ]
    }, 
    "AWS::EC2::EIP": {
        "importProperties": [
            "PublicIp"
        ]
    }, 
    "AWS::EC2::FlowLog": {
        "importProperties": [
            "Id"
        ]
    }, 
    "AWS::EC2::GatewayRouteTableAssociation": {
        "importProperties": [
            "GatewayId"
        ]
    }, 
    "AWS::EC2::Instance": {
        "importProperties": [
            "InstanceId"
        ]
    }, 
    "AWS::EC2::InternetGateway": {
        "importProperties": [
            "InternetGatewayId"
        ]
    }, 
    "AWS::EC2::LocalGatewayRoute": {
        "importProperties": [
            "DestinationCidrBlock", 
            "LocalGatewayRouteTableId"
        ]
    }, 
    "AWS::EC2::LocalGatewayRouteTableVPCAssociation": {
        "importProperties": [
            "LocalGatewayRouteTableVpcAssociationId"
        ]
    }, 
    "AWS::EC2::NatGateway": {
        "importProperties": [
            "NatGatewayId"
        ]
    }, 
    "AWS::EC2::NetworkAcl": {
        "importProperties": [
            "NetworkAclId"
        ]
    }, 
    "AWS::EC2::NetworkInterface": {
        "importProperties": [
            "NetworkInterfaceId"
        ]
    }, 
    "AWS::EC2::PrefixList": {
        "importProperties": [
            "PrefixListId"
        ]
    }, 
    "AWS::EC2::RouteTable": {
        "importProperties": [
            "RouteTableId"
        ]
    }, 
    "AWS::EC2::SecurityGroup": {
        "importProperties": [
            "GroupId"
        ]
    }, 
    "AWS::EC2::Subnet": {
        "importProperties": [
            "SubnetId"
        ]
    }, 
    "AWS::EC2::VPC": {
        "importProperties": [
            "VpcId"
        ]
    }, 
    "AWS::EC2::Volume": {
        "importProperties": [
            "VolumeId"
        ]
    }, 
    "AWS::ECS::CapacityProvider": {
        "importProperties": [
            "Name"
        ]
    }, 
    "AWS::ECS::Cluster": {
        "importProperties": [
            "ClusterName"
        ]
    }, 
    "AWS::ECS::PrimaryTaskSet": {
        "importProperties": [
            "Cluster", 
            "Service"
        ]
    }, 
    "AWS::ECS::Service": {
        "importProperties": [
            "ServiceArn", 
            "Cluster"
        ]
    }, 
    "AWS::ECS::TaskDefinition": {
        "importProperties": [
            "TaskDefinitionArn"
        ]
    }, 
    "AWS::ECS::TaskSet": {
        "importProperties": [
            "Cluster", 
            "Service", 
            "Id"
        ]
    }, 
    "AWS::EFS::AccessPoint": {
        "importProperties": [
            "AccessPointId"
        ]
    }, 
    "AWS::EFS::FileSystem": {
        "importProperties": [
            "FileSystemId"
        ]
    }, 
    "AWS::ElasticLoadBalancing::LoadBalancer": {
        "importProperties": [
            "LoadBalancerName"
        ]
    }, 
    "AWS::ElasticLoadBalancingV2::Listener": {
        "importProperties": [
            "ListenerArn"
        ]
    }, 
    "AWS::ElasticLoadBalancingV2::ListenerRule": {
        "importProperties": [
            "RuleArn"
        ]
    }, 
    "AWS::ElasticLoadBalancingV2::LoadBalancer": {
        "importProperties": [
            "LoadBalancerArn"
        ]
    }, 
    "AWS::EventSchemas::RegistryPolicy": {
        "importProperties": [
            "Id"
        ]
    }, 
    "AWS::Events::Rule": {
        "importProperties": [
            "Name"
        ]
    }, 
    "AWS::FMS::NotificationChannel": {
        "importProperties": [
            "SnsTopicArn"
        ]
    }, 
    "AWS::FMS::Policy": {
        "importProperties": [
            "Id"
        ]
    }, 
    "AWS::GlobalAccelerator::Accelerator": {
        "importProperties": [
            "AcceleratorArn"
        ]
    }, 
    "AWS::GlobalAccelerator::EndpointGroup": {
        "importProperties": [
            "EndpointGroupArn"
        ]
    }, 
    "AWS::GlobalAccelerator::Listener": {
        "importProperties": [
            "ListenerArn"
        ]
    }, 
    "AWS::ImageBuilder::Component": {
        "importProperties": [
            "Arn"
        ]
    }, 
    "AWS::ImageBuilder::DistributionConfiguration": {
        "importProperties": [
            "Arn"
        ]
    }, 
    "AWS::ImageBuilder::Image": {
        "importProperties": [
            "Arn"
        ]
    }, 
    "AWS::ImageBuilder::ImagePipeline": {
        "importProperties": [
            "Arn"
        ]
    }, 
    "AWS::ImageBuilder::ImageRecipe": {
        "importProperties": [
            "Arn"
        ]
    }, 
    "AWS::ImageBuilder::InfrastructureConfiguration": {
        "importProperties": [
            "Arn"
        ]
    }, 
    "AWS::IoT::ProvisioningTemplate": {
        "importProperties": [
            "TemplateName"
        ]
    }, 
    "AWS::IoT::Thing": {
        "importProperties": [
            "ThingName"
        ]
    }, 
    "AWS::KinesisFirehose::DeliveryStream": {
        "importProperties": [
            "DeliveryStreamName"
        ]
    }, 
    "AWS::Lambda::Alias": {
        "importProperties": [
            "AliasArn"
        ]
    }, 
    "AWS::Lambda::Function": {
        "importProperties": [
            "FunctionName"
        ]
    }, 
    "AWS::Lambda::Version": {
        "importProperties": [
            "FunctionArn"
        ]
    }, 
    "AWS::Logs::LogGroup": {
        "importProperties": [
            "LogGroupName"
        ]
    }, 
    "AWS::Logs::MetricFilter": {
        "importProperties": [
            "FilterName"
        ]
    }, 
    "AWS::Logs::SubscriptionFilter": {
        "importProperties": [
            "LogGroupName", 
            "FilterName"
        ]
    }, 
    "AWS::Macie::CustomDataIdentifier": {
        "importProperties": [
            "Id"
        ]
    }, 
    "AWS::Macie::FindingsFilter": {
        "importProperties": [
            "Id"
        ]
    }, 
    "AWS::Macie::Session": {
        "importProperties": [
            "AwsAccountId"
        ]
    }, 
    "AWS::NetworkManager::CustomerGatewayAssociation": {
        "importProperties": [
            "GlobalNetworkId", 
            "CustomerGatewayArn"
        ]
    }, 
    "AWS::NetworkManager::Device": {
        "importProperties": [
            "GlobalNetworkId", 
            "DeviceId"
        ]
    }, 
    "AWS::NetworkManager::GlobalNetwork": {
        "importProperties": [
            "Id"
        ]
    }, 
    "AWS::NetworkManager::Link": {
        "importProperties": [
            "GlobalNetworkId", 
            "LinkId"
        ]
    }, 
    "AWS::NetworkManager::LinkAssociation": {
        "importProperties": [
            "GlobalNetworkId", 
            "DeviceId", 
            "LinkId"
        ]
    }, 
    "AWS::NetworkManager::Site": {
        "importProperties": [
            "GlobalNetworkId", 
            "SiteId"
        ]
    }, 
    "AWS::NetworkManager::TransitGatewayRegistration": {
        "importProperties": [
            "GlobalNetworkId", 
            "TransitGatewayArn"
        ]
    }, 
    "AWS::QLDB::Stream": {
        "importProperties": [
            "LedgerName", 
            "Id"
        ]
    }, 
    "AWS::RDS::DBCluster": {
        "importProperties": [
            "DBClusterIdentifier"
        ]
    }, 
    "AWS::RDS::DBInstance": {
        "importProperties": [
            "DBInstanceIdentifier"
        ]
    }, 
    "AWS::RDS::DBProxy": {
        "importProperties": [
            "DBProxyName"
        ]
    }, 
    "AWS::RDS::DBProxyTargetGroup": {
        "importProperties": [
            "TargetGroupArn"
        ]
    }, 
    "AWS::ResourceGroups::Group": {
        "importProperties": [
            "Name"
        ]
    }, 
    "AWS::Route53::HostedZone": {
        "importProperties": [
            "HostedZoneId"
        ]
    }, 
    "AWS::S3::AccessPoint": {
        "importProperties": [
            "Name"
        ]
    }, 
    "AWS::S3::Bucket": {
        "importProperties": [
            "BucketName"
        ]
    }, 
    "AWS::SES::ConfigurationSet": {
        "importProperties": [
            "Name"
        ]
    }, 
    "AWS::SNS::Topic": {
        "importProperties": [
            "TopicArn"
        ]
    }, 
    "AWS::SQS::Queue": {
        "importProperties": [
            "QueueUrl"
        ]
    }, 
    "AWS::SSM::Association": {
        "importProperties": [
            "AssociationId"
        ]
    }, 
    "AWS::ServiceCatalog::CloudFormationProvisionedProduct": {
        "importProperties": [
            "ProvisionedProductId"
        ]
    }, 
    "AWS::Synthetics::Canary": {
        "importProperties": [
            "Name"
        ]
    }, 
    "AWS::WAFv2::IPSet": {
        "importProperties": [
            "Name", 
            "Id", 
            "Scope"
        ]
    }, 
    "AWS::WAFv2::RegexPatternSet": {
        "importProperties": [
            "Name", 
            "Id", 
            "Scope"
        ]
    }, 
    "AWS::WAFv2::RuleGroup": {
        "importProperties": [
            "Name", 
            "Id", 
            "Scope"
        ]
    }, 
    "AWS::WAFv2::WebACL": {
        "importProperties": [
            "Name", 
            "Id", 
            "Scope"
        ]
    }, 
    "AWS::WAFv2::WebACLAssociation": {
        "importProperties": [
            "ResourceArn", 
            "WebACLArn"
        ]
    },
    "AWS::CloudFormation::Stack": {
        "importProperties": [
            "StackId"
        ],
        "capabilities": [
            "CAPABILITY_NAMED_IAM"
        ]
    },
    "AWS::IAM::Group": {
        "importProperties": [
            "GroupName"
        ],
        "capabilities": [
            "CAPABILITY_NAMED_IAM"
        ]
    },
    "AWS::IAM::InstanceProfile": {
        "importProperties": [
            "InstanceProfileName"
        ],
        "capabilities": [
            "CAPABILITY_NAMED_IAM"
        ]
    },
    "AWS::IAM::Role": {
        "importProperties": [
            "RoleName"
        ],
        "capabilities": [
            "CAPABILITY_NAMED_IAM"
        ]
    },
    "AWS::IAM::User": {
        "importProperties": [
            "UserName"
        ],
        "capabilities": [
            "CAPABILITY_NAMED_IAM"
        ]
    },
    "AWS::IAM::ManagedPolicy": {
        "importProperties": [
            "PolicyArn"
        ],
        "capabilities": [
            "CAPABILITY_NAMED_IAM"
        ]
    }
}

if len(sys.argv) == 3:
    cfnclient = boto3.client('cloudformation', region_name=sys.argv[2])
elif len(sys.argv) == 2:
    cfnclient = boto3.client('cloudformation')
else:
    print("Inconsistent arguments")
    quit()

try:
    stacks = cfnclient.describe_stacks(
        StackName=sys.argv[1]
    )['Stacks']
except:
    print("Could not find stack")
    quit()

original_stack_id = stacks[0]['StackId']
stack_name = stacks[0]['StackName']
stack_params = []
if 'Parameters' in stacks[0]:
    stack_params = stacks[0]['Parameters']

original_template = cfnclient.get_template(
    StackName=original_stack_id,
    TemplateStage='Processed'
)['TemplateBody']

if not isinstance(original_template, str):
    original_template = json.dumps(dict(original_template)) # OrderedDict

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

for i in range(len(resource_drifts)): # filter non-importable resources
    if resource_drifts[i]['ResourceType'] not in eligible_import_resources.keys():
        del resource_drifts[i]

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
    ],
    Parameters=stack_params
)

waiter = cfnclient.get_waiter('stack_update_complete')
waiter.wait(
    StackName=original_stack_id,
    WaiterConfig={
        'Delay': 10,
        'MaxAttempts': 360
    }
)

# De-ref
match_resources = []
for drifted_resource in resource_drifts:
    match_resources.append(drifted_resource['LogicalResourceId'])
resolvePropertyValue(template, match_resources, False)

if len(resolve_matches) > 0:
    print("Temporarily dereferencing removed resources...")

    if not 'Outputs' in template:
        template['Outputs'] = {}

    for k, v in resolve_matches.items():
        template['Outputs']['Drift' + str(k)] = {
            'Value': v
        }

    cfnclient.update_stack(
        StackName=original_stack_id,
        TemplateBody=json.dumps(template),
        Capabilities=[
            'CAPABILITY_NAMED_IAM',
            'CAPABILITY_AUTO_EXPAND'
        ],
        Parameters=stack_params
    )

    waiter = cfnclient.get_waiter('stack_update_complete')
    waiter.wait(
        StackName=original_stack_id,
        WaiterConfig={
            'Delay': 10,
            'MaxAttempts': 360
        }
    )

    stack_outputs = cfnclient.describe_stacks(
        StackName=original_stack_id
    )['Stacks'][0]['Outputs']

    for k, v in resolve_matches.items():
        for output in stack_outputs:
            if output['OutputKey'] == 'Drift' + str(k):
                resolve_matches[k] = output['OutputValue']

    template = resolvePropertyValue(template, match_resources, True)

print("Removing drifted resources (whilst retaining resources!)...")

for drifted_resource in resource_drifts:
    del template['Resources'][drifted_resource['LogicalResourceId']]

if len(template['Resources']) == 0: # last ditch effort to retain stack
    template = empty_template

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

import_resources = []
for drifted_resource in resource_drifts:
    resource_identifier = {}

    import_properties = eligible_import_resources[drifted_resource['ResourceType']]['importProperties'].copy()
    if 'PhysicalResourceIdContext' in drifted_resource:
        for prop in drifted_resource['PhysicalResourceIdContext']:
            if prop['Key'] in import_properties:
                resource_identifier[prop['Key']] = prop['Value']
                import_properties.remove(prop['Key'])
    
    if len(import_properties) > 1:
        print("ERROR: Unexpected additional importable keys required, aborting...")
        quit()
    elif len(import_properties) == 1:
        resource_identifier[import_properties[0]] = drifted_resource['PhysicalResourceId']

    template['Resources'][drifted_resource['LogicalResourceId']] = {
        'DeletionPolicy': 'Retain',
        'Type': drifted_resource['ResourceType'],
        'Properties': json.loads(drifted_resource['ActualProperties'])
    }

    import_resources.append({
        'ResourceType': drifted_resource['ResourceType'],
        'LogicalResourceId': drifted_resource['LogicalResourceId'],
        'ResourceIdentifier': resource_identifier
    })

print("Recreating drifted resources with current state...")

change_set_name = 'Drift-Remediation-' + str(int(time.time()))
new_stack_id = cfnclient.create_change_set(
    StackName=stack_name,
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
    StackName=stack_name,
    TemplateBody=original_template,
    Capabilities=[
        'CAPABILITY_NAMED_IAM',
        'CAPABILITY_AUTO_EXPAND'
    ],
    Parameters=stack_params
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
