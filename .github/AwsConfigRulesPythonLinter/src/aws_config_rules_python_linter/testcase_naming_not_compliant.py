import astroid

from pylint.interfaces import HIGH, IAstroidChecker
from pylint.checkers import BaseChecker


class TestCasesNamingChecker(BaseChecker):
    __implements__ = IAstroidChecker

    name = 'testcase-naming-not-compliant'

    msgs = {
        'C5003': ('Test case name is not compliant: "%s"',
                  'testcase-naming-not-compliant',
                  '''Refer to "For unit test functions, use descriptive name" part in Coding Standards
                  '''),
    }
    options = ()
    priority = -1

    def visit_module(self, node):
        # Only trigger checker if unittest is imported (is a test cases file)
        if "import unittest" in node.as_string():
            for sub_node in node.body:
                if isinstance(sub_node, astroid.ClassDef):
                    for function in sub_node.body:
                        if isinstance(function, astroid.FunctionDef):
                            if function.name.startswith("test_"):
                                fields = function.name.split("_")
                                if len(fields) != 5:
                                    self.add_message(
                                        'testcase-naming-not-compliant', node=function, args="Test case name should have 5 fields test_<scenarioName>_<methodName>_<inputconditions>_<outputResult>", confidence=HIGH
                                    )
                                else:
                                    if not fields[1].startswith("scenario"):
                                        self.add_message(
                                            'testcase-naming-not-compliant', node=function, args="Second field in test case name should be <scenrioName>", confidence=HIGH
                                        )
                                    if fields[2] not in ['evaluatePeriodic', 'evaluateParameters', 'evaluateChange']:
                                        self.add_message(
                                            'testcase-naming-not-compliant', node=function, args="Third field in test case name should be <methodName> from 'evaluatePeriodic', 'evaluateParameters', 'evaluateChange'", confidence=HIGH
                                        )
                                    if fields[4] not in ['returnsNonCompliant', 'returnsCompliant', 'returnsNotApplicable', 'raisesException']:
                                        self.add_message(
                                            'testcase-naming-not-compliant', node=function, args="Fifth field in test case name should be <outputResult> from 'returnsNonCompliant', 'returnsCompliant', 'returnsNotApplicable', 'raisesException'", confidence=HIGH
                                        )

def register(linter):
    """required method to auto register this checker"""
    linter.register_checker(TestCasesNamingChecker(linter))
