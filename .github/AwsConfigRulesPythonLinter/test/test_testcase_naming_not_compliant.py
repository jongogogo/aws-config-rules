import pylint.testutils
import astroid
from aws_config_rules_python_linter import testcase_naming_not_compliant
from pylint.interfaces import Confidence

GOOD_NAME = """
import unittest
class ComplianceTest(unittest.TestCase):
    def test_scenario1_evaluateChange_stoppedInstanceWithoutDate_returnsCompliant(self):
        pass
"""

BAD_FIELD2 = """
import unittest
class ComplianceTest(unittest.TestCase):
    def test_abc_evaluateChange_stoppedInstanceWithoutDate_returnsCompliant(self):
        pass
"""

BAD_FIELD3 = """
import unittest
class ComplianceTest(unittest.TestCase):
    def test_scenario1_evaluateChanges_stoppedInstanceWithoutDate_returnsCompliant(self):
        pass
"""

BAD_FIELD5 = """
import unittest
class ComplianceTest(unittest.TestCase):
    def test_scenario1_evaluateChange_stoppedInstanceWithoutDate_Compliant(self):
        pass
"""

class TestTestCasesNamingChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = testcase_naming_not_compliant.TestCasesNamingChecker

    def test_good_name(self):
        module_node = astroid.parse(GOOD_NAME)
        with self.assertAddsMessages():
            self.checker.visit_module(module_node)

    def test_bad_field2_name(self):
        module_node = astroid.parse(BAD_FIELD2)
        for sub_node in module_node.body:
            if isinstance(sub_node, astroid.ClassDef):
                for function in sub_node.body:
                    function_node = function

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id='testcase-naming-not-compliant',
                args="Second field in test case name should be <scenrioName>",
                confidence=Confidence(name='HIGH', description='No false positive possible.'),
                node=function
            )
        ):
            self.checker.visit_module(module_node)

    def test_bad_field3_name(self):
        module_node = astroid.parse(BAD_FIELD3)
        for sub_node in module_node.body:
            if isinstance(sub_node, astroid.ClassDef):
                for function in sub_node.body:
                    function_node = function

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id='testcase-naming-not-compliant',
                args="Third field in test case name should be <methodName> from 'evaluatePeriodic', 'evaluateParameters', 'evaluateChange'",
                confidence=Confidence(name='HIGH', description='No false positive possible.'),
                node=function
            )
        ):
            self.checker.visit_module(module_node)

    def test_bad_field5_name(self):
        module_node = astroid.parse(BAD_FIELD5)
        for sub_node in module_node.body:
            if isinstance(sub_node, astroid.ClassDef):
                for function in sub_node.body:
                    function_node = function

        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id='testcase-naming-not-compliant',
                args="Fifth field in test case name should be <outputResult> from 'returnsNonCompliant', 'returnsCompliant', 'returnsNotApplicable', 'raisesException'",
                confidence=Confidence(name='HIGH', description='No false positive possible.'),
                node=function
            )
        ):
            self.checker.visit_module(module_node)
