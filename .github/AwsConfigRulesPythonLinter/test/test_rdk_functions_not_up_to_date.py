import pylint.testutils
import astroid
from aws_config_rules_python_linter import rdk_functions_not_up_to_date
from pylint.interfaces import Confidence

GOOD_CODE = """
class S3_ACCOUNT_LEVEL_PUBLIC_ACCESS_BLOCKS(ConfigRule):
    def evaluate_change(self, event, client_factory, configuration_item, valid_rule_parameters):
        pass
    def evaluate_parameters(self, rule_parameters):
        if wrong:
            raise InvalidParametersError("Invalid value for parameter")
        pass
"""

MISSING_PARAMETERS_EVALUATION = """
class S3_ACCOUNT_LEVEL_PUBLIC_ACCESS_BLOCKS(ConfigRule):
    def evaluate_change(self, event, client_factory, configuration_item, valid_rule_parameters):
        pass
"""

MISSING_EVALUATION_FUNCTION = """
\"\"\"
Rule Parameters:
    None
\"\"\"
class S3_ACCOUNT_LEVEL_PUBLIC_ACCESS_BLOCKS(ConfigRule):
    def evaluate_parameters(self, rule_parameters):
        pass
"""

MISSING_INVALIDPARAMETERERROR = """
class S3_ACCOUNT_LEVEL_PUBLIC_ACCESS_BLOCKS(ConfigRule):
    def evaluate_parameters(self, rule_parameters):
        pass
    def evaluate_change(self, event, client_factory, configuration_item, valid_rule_parameters):
        pass
"""

MISSING_RESOURCE_TYPE = """
def lambda_handler(event, context):
    my_rule = S3_ACCOUNT_LEVEL_PUBLIC_ACCESS_BLOCKS()
    evaluator = Evaluator(my_rule)
    return evaluator.handle(event, context)
"""


class TestRDKFunctionsChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = rdk_functions_not_up_to_date.RDKFunctionsChecker

    def test_rdk_functions_ok(self):
        module_node = astroid.parse(GOOD_CODE)
        class_node = astroid.extract_node(GOOD_CODE)

        with self.assertAddsMessages():
            for func_node in class_node.body:
                self.checker.visit_functiondef(func_node)
            self.checker.visit_module(module_node)

    def test_rdk_functions_evaluate_parameters_not_exist(self):
        module_node = astroid.parse(MISSING_PARAMETERS_EVALUATION)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id='rdk-functions-not-up-to-date',
                args="'evaluate_parameters' is not included",
                confidence=Confidence(name='HIGH', description='No false positive possible.'),
                node=module_node
            ),
            pylint.testutils.Message(
                msg_id='rdk-functions-not-up-to-date',
                args="'InvalidParametersError' is not used for evaluating parameters",
                confidence=Confidence(name='HIGH', description='No false positive possible.'),
                node=module_node
            )
        ):
            self.checker.visit_module(module_node)

    def test_rdk_functions_evaluate_function_not_exist(self):
        module_node = astroid.parse(MISSING_EVALUATION_FUNCTION)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id='rdk-functions-not-up-to-date',
                args="'evaluate_change' or 'evaluate_periodic' is not included",
                confidence=Confidence(name='HIGH', description='No false positive possible.'),
                node=module_node
            )
        ):
            self.checker.visit_module(module_node)

    def test_rdk_functions_InvalidParametersError_not_used(self):
        module_node = astroid.parse(MISSING_INVALIDPARAMETERERROR)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id='rdk-functions-not-up-to-date',
                args="'InvalidParametersError' is not used for evaluating parameters",
                confidence=Confidence(name='HIGH', description='No false positive possible.'),
                node=module_node
            )
        ):
            self.checker.visit_module(module_node)

    def test_rdk_functions_no_resource_type_in_lambda_handler(self):
        func_node = astroid.extract_node(MISSING_RESOURCE_TYPE)

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id='rdk-functions-not-up-to-date',
                args="No resource type for Evaluator in lambda_handler, example https://code.amazon.com/packages/AwsFalconOrbiter/blobs/903db8f2fc93711f96047943e3be99c0ad7bd74e/--/managed-rule-code/API_GW_ENDPOINT_TYPE_CHECK.py#L80",
                confidence=Confidence(name='HIGH', description='No false positive possible.'),
                node=func_node
            )
        ):
            self.checker.visit_functiondef(func_node)
