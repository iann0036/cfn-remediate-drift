# CloudFormation Remediate Drift [WORK IN PROGRESS]

> Automated CloudFormation drift remediation using Import functionality

The following script will programmatically perform the following steps:

* Check for drifted resources
* Remove any *supported* drifted resources from the stack, whilst retaining the resource
* Import the resources with their current state back into the stack
* Perform an update on the stack back to its original template, effectively remediating the resources

> :exclamation: This script is not thoroughly tested and you should attempt to use this on a non-critical resource before real-world use as some resources refuse to re-import for a variety of reasons. I am not responsible for your data loss.

## Usage

```
python3 index.py MyStackName
```

### Supported Resources

You should check [here](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resource-import-supported-resources.html) for a list of resources that support import. Other resources will be ignored, even if drift is detected.
