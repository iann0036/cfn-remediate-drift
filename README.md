# CloudFormation Remediate Drift [WORK IN PROGRESS]

The following script will programmatically perform the following steps:

* Check for drifted resources
* Remove any *supported* drifted resources from the stack, whilst retaining the resource
* Using CloudFormation outputs, extract any references to resources that have drifted and replace the references with the dereferenced values temporarily
* Import the resources with their current state back into the stack
* Perform an update on the stack back to its original template, effectively remediating the resources

> :exclamation: This script is not thoroughly tested and you should attempt to use this on a non-critical resource before real-world usage as some resources refuse to re-import for a variety of reasons. I am not responsible for your data loss.

## Usage

```
python3 index.py MyStackName
```

### Supported Resources

The following resources are supported for import operations (other resources will be ignored, even if drift is detected):

* AWS::ACMPCA::Certificate
* AWS::ACMPCA::CertificateAuthority
* AWS::ACMPCA::CertificateAuthorityActivation
* AWS::AccessAnalyzer::Analyzer
* AWS::ApiGateway::Authorizer
* AWS::ApiGateway::Deployment
* AWS::ApiGateway::Method
* AWS::ApiGateway::Model
* AWS::ApiGateway::RequestValidator
* AWS::ApiGateway::Resource
* AWS::ApiGateway::RestApi
* AWS::ApiGateway::Stage
* AWS::Athena::DataCatalog
* AWS::Athena::NamedQuery
* AWS::Athena::WorkGroup
* AWS::AutoScaling::AutoScalingGroup
* AWS::AutoScaling::LaunchConfiguration
* AWS::AutoScaling::LifecycleHook
* AWS::AutoScaling::ScalingPolicy
* AWS::AutoScaling::ScheduledAction
* AWS::CE::CostCategory
* AWS::Cassandra::Keyspace
* AWS::Cassandra::Table
* AWS::Chatbot::SlackChannelConfiguration
* AWS::CloudFormation::Stack
* AWS::CloudTrail::Trail
* AWS::CloudWatch::Alarm
* AWS::CloudWatch::CompositeAlarm
* AWS::CodeGuruProfiler::ProfilingGroup
* AWS::CodeStarConnections::Connection
* AWS::Config::ConformancePack
* AWS::Config::OrganizationConformancePack
* AWS::Detective::Graph
* AWS::Detective::MemberInvitation
* AWS::DynamoDB::Table
* AWS::EC2::EIP
* AWS::EC2::FlowLog
* AWS::EC2::GatewayRouteTableAssociation
* AWS::EC2::Instance
* AWS::EC2::InternetGateway
* AWS::EC2::LocalGatewayRoute
* AWS::EC2::LocalGatewayRouteTableVPCAssociation
* AWS::EC2::NatGateway
* AWS::EC2::NetworkAcl
* AWS::EC2::NetworkInterface
* AWS::EC2::PrefixList
* AWS::EC2::RouteTable
* AWS::EC2::SecurityGroup
* AWS::EC2::Subnet
* AWS::EC2::VPC
* AWS::EC2::Volume
* AWS::ECS::CapacityProvider
* AWS::ECS::Cluster
* AWS::ECS::PrimaryTaskSet
* AWS::ECS::Service
* AWS::ECS::TaskDefinition
* AWS::ECS::TaskSet
* AWS::EFS::AccessPoint
* AWS::EFS::FileSystem
* AWS::ElasticLoadBalancing::LoadBalancer
* AWS::ElasticLoadBalancingV2::Listener
* AWS::ElasticLoadBalancingV2::ListenerRule
* AWS::ElasticLoadBalancingV2::LoadBalancer
* AWS::EventSchemas::RegistryPolicy
* AWS::Events::Rule
* AWS::FMS::NotificationChannel
* AWS::FMS::Policy
* AWS::GlobalAccelerator::Accelerator
* AWS::GlobalAccelerator::EndpointGroup
* AWS::GlobalAccelerator::Listener
* AWS::ImageBuilder::Component
* AWS::ImageBuilder::DistributionConfiguration
* AWS::ImageBuilder::Image
* AWS::ImageBuilder::ImagePipeline
* AWS::ImageBuilder::ImageRecipe
* AWS::ImageBuilder::InfrastructureConfiguration
* AWS::IoT::ProvisioningTemplate
* AWS::IoT::Thing
* AWS::KinesisFirehose::DeliveryStream
* AWS::Lambda::Alias
* AWS::Lambda::Function
* AWS::Lambda::Version
* AWS::Logs::LogGroup
* AWS::Logs::MetricFilter
* AWS::Logs::SubscriptionFilter
* AWS::Macie::CustomDataIdentifier
* AWS::Macie::FindingsFilter
* AWS::Macie::Session
* AWS::NetworkManager::CustomerGatewayAssociation
* AWS::NetworkManager::Device
* AWS::NetworkManager::GlobalNetwork
* AWS::NetworkManager::Link
* AWS::NetworkManager::LinkAssociation
* AWS::NetworkManager::Site
* AWS::NetworkManager::TransitGatewayRegistration
* AWS::QLDB::Stream
* AWS::RDS::DBCluster
* AWS::RDS::DBInstance
* AWS::RDS::DBProxy
* AWS::RDS::DBProxyTargetGroup
* AWS::ResourceGroups::Group
* AWS::Route53::HostedZone
* AWS::S3::AccessPoint
* AWS::S3::Bucket
* AWS::SES::ConfigurationSet
* AWS::SNS::Topic
* AWS::SQS::Queue
* AWS::SSM::Association
* AWS::ServiceCatalog::CloudFormationProvisionedProduct
* AWS::Synthetics::Canary
* AWS::WAFv2::IPSet
* AWS::WAFv2::RegexPatternSet
* AWS::WAFv2::RuleGroup
* AWS::WAFv2::WebACL
* AWS::WAFv2::WebACLAssociation
* AWS::IAM::Group
* AWS::IAM::InstanceProfile
* AWS::IAM::Role
* AWS::IAM::User
* AWS::IAM::ManagedPolicy

### Known Issues

* Templates with a high amount of drifted resources may cause an error regarding too many outputs
* Drifted resources referenced within a `Fn::Sub` string may cause the process to fail
