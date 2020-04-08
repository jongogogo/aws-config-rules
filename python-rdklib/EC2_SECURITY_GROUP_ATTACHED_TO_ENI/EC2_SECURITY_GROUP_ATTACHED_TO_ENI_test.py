import unittest
from mock import patch, MagicMock
import rdklibtest
from rdklib import Evaluation, ComplianceType

##############
# Parameters #
##############

# Define the default resource to report to Config Rules
DEFAULT_RESOURCE_TYPE = 'AWS::EC2::SecurityGroup'

#############
# Main Code #
#############

CLIENT_FACTORY = MagicMock()
CONFIG_CLIENT_MOCK = MagicMock()

def mock_get_client(client_name, *args, **kwargs):
    return CONFIG_CLIENT_MOCK

MODULE = __import__('EC2_SECURITY_GROUP_ATTACHED_TO_ENI')
RULE = MODULE.EC2_SECURITY_GROUP_ATTACHED_TO_ENI()

@patch.object(CLIENT_FACTORY, 'build_client', MagicMock(side_effect=mock_get_client))
class ComplianceTest(unittest.TestCase):

    # Scenario 1: Security group is default
    def test_1_evaluatechange_sgisdefault_notapplicable(self):
        config_item = {
            "configuration": {
                "groupName": "default"
            },
            "resourceType": "AWS::EC2::SecurityGroup",
            "configurationItemCaptureTime": "2019-04-28T07:49:40.797Z",
            "resourceId": "sg-0123456789abcdefg"
        }
        response = RULE.evaluate_change({}, {}, config_item, {})
        resp_expected = [Evaluation(ComplianceType.NOT_APPLICABLE)]
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)

    # Scenario 2: Security group is not associated with any ENI/EC2
    def test_2_evaluatechange_sgnotassociated_noncompliant(self):
        CONFIG_CLIENT_MOCK.select_resource_config.return_value = {'Results': ['{"COUNT(*)": 0}']}
        config_item = {
            "configuration": {
                "groupName": "security-group-1"
            },
            "relationships": [{
                "resourceId":"vpc-01234567",
                "resourceType":"AWS::EC2::VPC"
            }],
            "resourceType": "AWS::EC2::SecurityGroup",
            "configurationItemCaptureTime": "2019-04-28T07:49:40.797Z",
            "resourceId": "sg-0123456789abcdefg"
        }
        response = RULE.evaluate_change({}, CLIENT_FACTORY, config_item, {})
        resp_expected = [Evaluation(ComplianceType.NON_COMPLIANT, annotation='This Amazon EC2 security group is not associated with an EC2 instance or an ENI.')]
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)


    # Scenario 3: Security group is not associated with at one or more CodeBuild project
    def test_3_evaluatechange_sgassociated_one_codebuild_compliant(self):
        config_item = {
            "configuration": {
                "groupName": "security-group-1"
            },
            "relationships": [{
                "resourceId":"vpc-01234567",
                "resourceType":"AWS::EC2::VPC"
            }],
            "resourceType": "AWS::EC2::SecurityGroup",
            "configurationItemCaptureTime": "2019-04-28T07:49:40.797Z",
            "resourceId": "sg-0123456789abcdefg"
        }

        CONFIG_CLIENT_MOCK.select_resource_config.return_value = {'Results': ['{"COUNT(*)": 1}']}
        response = RULE.evaluate_change({}, CLIENT_FACTORY, config_item, {})
        resp_expected = [Evaluation(ComplianceType.COMPLIANT, annotation='This Amazon EC2 security group is associated with at least one AWS CodeBuild project.')]
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)
        
        CONFIG_CLIENT_MOCK.select_resource_config.return_value = {'Results': ['{"COUNT(*)": 3}']}
        response = RULE.evaluate_change({}, CLIENT_FACTORY, config_item, {})
        resp_expected = [Evaluation(ComplianceType.COMPLIANT, annotation='This Amazon EC2 security group is associated with at least one AWS CodeBuild project.')]
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)

    # Scenario 4: Security group is associated with atleast 1 ENI/EC2
    def test_4_evaluatechange_sgassociated_compliant(self):
        config_item = {
            "configuration": {
                "groupName": "security-group-2"
            },
            "relationships": [{
                "resourceId": "vpc-01234567",
                "resourceType": "AWS::EC2::VPC"
            }, {
                "resourceId": "eni-123456abcdefghi18",
                "resourceType": "AWS::EC2::NetworkInterface"
            }],
            "resourceType": "AWS::EC2::SecurityGroup",
            "configurationItemCaptureTime": "2019-04-28T07:49:40.797Z",
            "resourceId": "sg-0123456789abcdefg"
        }
        response = RULE.evaluate_change({}, {}, config_item, {})
        resp_expected = [Evaluation(ComplianceType.COMPLIANT)]
        rdklibtest.assert_successful_evaluation(self, response, resp_expected)
