import pylint.testutils
import astroid
from aws_config_rules_python_linter import gherkin_not_compliant
from pylint.interfaces import Confidence

GOOD_GHERKIN = """
\"\"\"
#####################################
##           Gherkin               ##
#####################################
Rule Name:
  EC2_STOPPED_INSTANCE
Description:
  Check if there are instances stopped for more than certain days.
Trigger:
  Periodic
Reports on:
  AWS::EC2::Instance
Rule Parameters:
  AllowedDays
    (Optional) Instance in stopped status for longer than how many days to be non-compliant, by default it is 30 days.
Scenarios:
  Scenario: 1
  Given: Days parameter is not in right format
   Then: Return ERROR
  Scenario: 2
  Given: No EC2 instance in stopped status is present
   Then: Return NOT_APPLICABLE
\"\"\"

import json
class EC2_STOPPED_INSTANCE(ConfigRule):
    def evaluate_periodic(self, event, client_factory, valid_rule_parameters):
        pass
"""

MISSING_FIELD_GHERKIN = """
\"\"\"
#####################################
##           Gherkin               ##
#####################################
Description:
  Check if there are instances stopped for more than certain days.
Trigger:
  Periodic
Reports on:
  AWS::EC2::Instance
Rule Parameters:
  AllowedDays
    (Optional) Instance in stopped status for longer than how many days to be non-compliant, by default it is 30 days.
Scenarios:
  Scenario: 1
  Given: Days parameter is not in right format
   Then: Return ERROR
  Scenario: 2
  Given: No EC2 instance in stopped status is present
   Then: Return NOT_APPLICABLE
\"\"\"

import json
class EC2_STOPPED_INSTANCE(ConfigRule):
    def evaluate_periodic(self, event, client_factory, valid_rule_parameters):
        pass
"""

BAD_FORMAT_GHERKIN = """
\"\"\"
#####################################
##           Gherkin               ##
#####################################
Rule Name:
  EC2_STOPPED_INSTANCE
Description:
  Check if there are instances stopped for more than certain days.
Trigger:
  Periodic
Reports on:
  AWS::EC2::Instance
Rule Parameters:
  AllowedDays
    (Optional) Instance in stopped status for longer than how many days to be non-compliant, by default it is 30 days.
Scenarios:
  Scenario 1:
  Given: Days parameter is not in right format
   Then: Return ERROR
  Scenario 2:
  Given: No EC2 instance in stopped status is present
   Then: Return NOT_APPLICABLE
\"\"\"

import json
class EC2_STOPPED_INSTANCE(ConfigRule):
    def evaluate_periodic(self, event, client_factory, valid_rule_parameters):
        pass
"""

NO_GHERKIN = """
import json
class EC2_STOPPED_INSTANCE(ConfigRule):
    def evaluate_periodic(self, event, client_factory, valid_rule_parameters):
        pass
"""

class TestGherkinCompliantChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = gherkin_not_compliant.GherkinCompliantChecker

    def test_gherkin_not_exist(self):
        module_node = astroid.parse(NO_GHERKIN)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id='gherkin-not-compliant',
                args="No Gherkin doc found",
                confidence=Confidence(name='HIGH', description='No false positive possible.'),
                node=module_node
            )
        ):
            self.checker.visit_module(module_node)

    def test_gherkin_compliant(self):
        module_node = astroid.parse(GOOD_GHERKIN)

        with self.assertAddsMessages():
            self.checker.visit_module(module_node)

    def test_gherkin_missing_field_not_compliant(self):
        module_node = astroid.parse(MISSING_FIELD_GHERKIN)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id='gherkin-not-compliant',
                args="'Rule Name' is not included",
                confidence=Confidence(name='HIGH', description='No false positive possible.'),
                node=module_node
            )
        ):
            self.checker.visit_module(module_node)

    def test_gherkin_bad_scenario_format_not_compliant(self):
        module_node = astroid.parse(BAD_FORMAT_GHERKIN)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id='gherkin-not-compliant',
                args="Scenario line '  Scenario 1:' is not using the right Gherkin Format",
                confidence=Confidence(name='HIGH', description='No false positive possible.'),
                node=module_node
            ),
            pylint.testutils.Message(
                msg_id='gherkin-not-compliant',
                args="Scenario line '  Scenario 2:' is not using the right Gherkin Format",
                confidence=Confidence(name='HIGH', description='No false positive possible.'),
                node=module_node
            )
        ):
            self.checker.visit_module(module_node)
