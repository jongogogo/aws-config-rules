import astroid
import re

from pylint.interfaces import HIGH, IAstroidChecker
from pylint.checkers import BaseChecker


class RDKFunctionsChecker(BaseChecker):
    __implements__ = IAstroidChecker

    name = 'rdk-functions-not-up-to-date'

    msgs = {
        'C5002': ('rdk functions not up to date: "%s"',
                  'rdk-functions-not-up-to-date',
                  '''Refer to RDK requirements
                  '''),
    }
    options = ()
    priority = -1

    def visit_functiondef(self, node):
        if node.name == "lambda_handler":
            if "Evaluator(my_rule)" in  node.as_string():
                self.add_message(
                    'rdk-functions-not-up-to-date', node=node, args="No resource type for Evaluator in lambda_handler", confidence=HIGH
                )

    def visit_module(self, node):
        functions = []
        InvalidParametersError_used = False
        IsConfigRule = False
        # Check if the rule has parameter(s) through Gherkin Rule
        if node.doc is not None and re.search('Rule Parameters:\n\s*None$', node.doc, re.M):
            has_parameters = False
        else:
            has_parameters = True
        for sub_node in node.body:
            # find ClassDef
            if isinstance(sub_node, astroid.ClassDef):
                # find class name
                for node_class in sub_node.bases:
                    # if class name is ConfigRule, trigger check
                    if hasattr(node_class, 'name') and node_class.name == "ConfigRule":
                        IsConfigRule = True
                        for function in sub_node.body:
                            functions.append(function.name)
                        if "evaluate_parameters" not in functions and has_parameters:
                            self.add_message(
                                'rdk-functions-not-up-to-date', node=node, args="'evaluate_parameters' is not included", confidence=HIGH
                            )
                        if "evaluate_change" not in functions and "evaluate_periodic" not in functions:
                            self.add_message(
                                'rdk-functions-not-up-to-date', node=node, args="'evaluate_change' or 'evaluate_periodic' is not included", confidence=HIGH
                            )
        # Find if InvalidParametersError is used
        if "InvalidParametersError" in node.as_string():
            InvalidParametersError_used = True
        # If it's a Config Rule and has Parameters but InvalidParametersError is not used
        if IsConfigRule and has_parameters and not InvalidParametersError_used:
            self.add_message(
                'rdk-functions-not-up-to-date', node=node, args="'InvalidParametersError' is not used for evaluating parameters", confidence=HIGH
            )

def register(linter):
    """required method to auto register this checker"""
    linter.register_checker(RDKFunctionsChecker(linter))
