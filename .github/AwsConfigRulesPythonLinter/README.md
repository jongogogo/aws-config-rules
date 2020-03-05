# AwsConfigRulesPythonLinter

This is custom checkers/plugins for pylint specifically for AWS Config rule development.

## Documentation

### pylintrc changes

1. init-hook added to include checkers/plugins in "pylint-plugins" directory
2. ignore "lib.\*.py" pattern, so that we could only run checks towards the Config Rule files
3. in load-plugins specify the checks/plugins we developed
4. by default disable all the checks
5. maintain an enabled check list to only check things we care, currently 158 checks are enabled which should cover most of the pep8 standards

### gherkin-not-compliant

1. when ConfigRule class is used, check if Gherkin doc is included.
2. check if the scenarios are using the correct Gherkin format
3. check if the required fields are in place
  - Rule Name
  - Description
  - Reports on
  - Rule Parameters
  - Scenarios

### rdk-functions-not-up-to-date

1. when ConfigRule class is used, check if RDK mandatory functions (evaluate_change or evaluate_periodic) are used.
2. check if "evaluate_parameters" is included if "Rule Parameters" in Gherkin is not "None".
3. check if "InvalidParametersError" is used if it's ConfigRule and "Rule Parameters" in Gherkin is not "None". 
4. for "lambda_handler", check if resource type is included for "Evaluator"

### testcase-naming-not-compliant

1. when "unittest" is imported, consider the file a testcase file and triger checking logic.
2. if test function name does not have 5 fields, raise:
> Test case name should have 5 fields test\_<scenarioName>\_<methodName>\_<inputconditions>\_<outputResult>
3. if field 2 of test function name is not starting with "scenario", raise:
> Second field in test case name should be <scenrioName>
4. if field 3 is not one of the valid method names, raise:
> Third field in test case name should be <methodName> from 'evaluatePeriodic', 'evaluateParameters', 'evaluateChange'
5. if field 4 is not one of the valid output results, raise:
> Fifth field in test case name should be <outputResult> from 'returnsNonCompliant', 'returnsCompliant', 'returnsNotApplicable', 'raisesException'

## How to contribute

Customer checkers are placed in `src/aws_config_rules_python_linter/` directory.

You could find out more on how to write a checker from:
http://pylint.pycqa.org/en/latest/how_tos/custom_checkers.html

You should also write test cases for your custom checkers, the test cases are located in `test/` directory.
