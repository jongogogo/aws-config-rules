'''
#####################################
##           Gherkin               ##
#####################################

Rule Name:
  EC2_SECURITY_GROUP_ATTACHED_TO_ENI

Description:
  Checks that non-default security groups are attached to Amazon Elastic Compute Cloud (EC2) instances or an elastic network interfaces (ENIs). The rule returns NON_COMPLIANT if the security group is not associated with an EC2 instance or an ENI.

Trigger:
  Configuration Changes

Reports on:
  AWS::EC2::SecurityGroup

Rule Parameters:
  None

Scenarios:
  Scenario: 1
    Given: The security group is the default security group
     Then: Return NOT_APPLICABLE
  Scenario: 2
    Given: 'relationships' in the configuration item does not contain a Network interface Id in resourceId
      And: the security group is not associated with a CodeBuild project
     Then: Return NON_COMPLIANT with annnotation "This Amazon EC2 security group is not associated with an EC2 instance or an ENI.".
  Scenario: 3
    Given: 'relationships' in the configuration item does not contain a Network interface Id in resourceId
      And: the security group is associated with one or more CodeBuild project
     Then: Return COMPLIANT with annnotation "This Amazon EC2 security group is associated with at least one AWS CodeBuild project.".
  Scenario: 4
    Given: 'relationships' in the configuration item contains at least one Network interface Id in resourceId
     Then: Return COMPLIANT
'''
import json
from rdklib import ConfigRule, Evaluator, Evaluation, ComplianceType

APPLICABLE_RESOURCES = ['AWS::EC2::SecurityGroup', 'AWS::CodeBuild::Project']

class EC2_SECURITY_GROUP_ATTACHED_TO_ENI(ConfigRule):
    def evaluate_change(self, event, client_factory, configuration_item, valid_rule_parameters):
        
        if configuration_item['resourceType'] == 'AWS::CodeBuild::Project':
            if configuration_item['configuration'].get('vpcConfig'):
                eval_list_sg = []
                for sg_id in configuration_item['configuration']['vpcConfig']['securityGroupIds']:
                    eval_list_sg.append(Evaluation(ComplianceType.COMPLIANT, sg_id, 'AWS::EC2::SecurityGroup'))
                return eval_list_sg

        if configuration_item['resourceType'] == 'AWS::EC2::SecurityGroup':    
            if configuration_item['configuration']['groupName'] == 'default':
                return [Evaluation(ComplianceType.NOT_APPLICABLE)]
            for relation in configuration_item['relationships']:
                #resourceId for eni: 'eni-123456abcdefghi12'
                if relation['resourceId'][0:3] == 'eni':
                    return [Evaluation(ComplianceType.COMPLIANT)]
            
            if is_security_group_attached_codebuild(client_factory, configuration_item['resourceId']):
                return [Evaluation(ComplianceType.COMPLIANT, annotation='This Amazon EC2 security group is associated with at least one AWS CodeBuild project.')]

            return [Evaluation(ComplianceType.NON_COMPLIANT, annotation='This Amazon EC2 security group is not associated with an EC2 instance or an ENI.')]
    
def is_security_group_attached_codebuild(client_factory, sg_id):

    query = "SELECT COUNT(*) WHERE  resourceType = 'AWS::CodeBuild::Project' AND configuration.vpcConfig.securityGroupIds = '{}'".format(sg_id)
    client_config = client_factory.build_client('config')
    query_result = json.loads(client_config.select_resource_config(Expression=query)['Results'][0])
    if query_result['COUNT(*)'] > 0:
        return True
    return False

################################
# DO NOT MODIFY ANYTHING BELOW #
################################
def lambda_handler(event, context):
    my_rule = EC2_SECURITY_GROUP_ATTACHED_TO_ENI()
    evaluator = Evaluator(my_rule, APPLICABLE_RESOURCES)
    return evaluator.handle(event, context)
