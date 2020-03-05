import astroid
import re

from pylint.interfaces import HIGH, IAstroidChecker
from pylint.checkers import BaseChecker


class GherkinCompliantChecker(BaseChecker):
    __implements__ = IAstroidChecker

    name = 'gherkin-not-compliant'

    msgs = {
        'C5001': ('Gherkin is not compliant: "%s"',
                  'gherkin-not-compliant',
                  '''Refer to Gherkin requirements
                  '''),
    }
    options = ()
    priority = -1

    def check_field(self, key_word, node):
        if key_word + ":" not in node.doc:
            self.add_message(
                'gherkin-not-compliant', node=node, args="'" + key_word + "' is not included", confidence=HIGH
            )

    def check_scenarios(self, node):
        is_scenario = False
        for line in node.doc.split("\n"):
            if is_scenario and not re.match(r"^\s*$", line) and not re.match(r"^\s*(Scenario|Given|And|Then):.*", line):
                self.add_message(
                    'gherkin-not-compliant', node=node, args="Scenario line '" + line + "' is not using the right Gherkin Format", confidence=HIGH
                )
            # Set is_scenario to True when "Scenarios:" line is found
            if line == "Scenarios:":
                is_scenario = True

    def visit_module(self, node):
        checked = False
        for sub_node in node.body:
            # find ClassDef
            if isinstance(sub_node, astroid.ClassDef):
                # find class name
                for node_class in sub_node.bases:
                    # if class name is ConfigRule, trigger check
                    if hasattr(node_class, 'name') and node_class.name == "ConfigRule":
                        # check if Gherkin doc exists
                        if node.doc is None:
                            self.add_message(
                                'gherkin-not-compliant', node=node, args="No Gherkin doc found", confidence=HIGH
                            )
                        else:
                            # Check if required fields exist
                            self.check_field('Rule Name', node)
                            self.check_field('Description', node)
                            self.check_field('Reports on', node)
                            self.check_field('Rule Parameters', node)
                            self.check_field('Scenarios', node)
                            # Check scenarios format
                            self.check_scenarios(node)
                        checked = True
                        break
            if checked == True:
                break

def register(linter):
    """required method to auto register this checker"""
    linter.register_checker(GherkinCompliantChecker(linter))
