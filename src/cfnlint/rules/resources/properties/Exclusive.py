"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
import cfnlint.helpers


class Exclusive(CloudFormationLintRule):
    """Check Properties Resource Configuration"""
    id = 'E2520'
    shortdesc = 'Check Properties that are mutually exclusive'
    description = 'Making sure CloudFormation properties ' + \
                  'that are exclusive are not defined'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint'
    tags = ['resources']

    def __init__(self):
        """Init"""
        super(Exclusive, self).__init__()
        exclusivespec = cfnlint.helpers.load_resources('data/AdditionalSpecs/Exclusive.json')
        self.resource_types_specs = exclusivespec['ResourceTypes']
        self.property_types_specs = exclusivespec['PropertyTypes']
        for resource_type_spec in self.resource_types_specs:
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in self.property_types_specs:
            self.resource_sub_property_types.append(property_type_spec)

    def check(self, properties, exclusions, path, cfn):
        """Check itself"""
        matches = []

        property_sets = cfn.get_object_without_conditions(properties)
        for property_set in property_sets:
            for prop in property_set['Object']:
                if prop in exclusions:
                    for excl_property in exclusions[prop]:
                        if excl_property in property_set['Object']:
                            if property_set['Scenario'] is None:
                                message = 'Property {0} should NOT exist with {1} for {2}'
                                matches.append(RuleMatch(
                                    path + [prop],
                                    message.format(excl_property, prop, '/'.join(map(str, path)))
                                ))
                            else:
                                scenario_text = ' and '.join(['when condition "%s" is %s' % (k, v) for (k, v) in property_set['Scenario'].items()])
                                message = 'Property {0} should NOT exist with {1} {2} for {3}'
                                matches.append(RuleMatch(
                                    path + [prop],
                                    message.format(excl_property, prop, scenario_text, '/'.join(map(str, path)))
                                ))

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = []

        exclusions = self.property_types_specs.get(property_type, {})
        matches.extend(self.check(properties, exclusions, path, cfn))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        exclusions = self.resource_types_specs.get(resource_type, {})
        matches.extend(self.check(properties, exclusions, path, cfn))

        return matches
