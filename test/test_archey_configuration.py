
import os
import sys
import tempfile
import unittest

from archey.archey import Configuration


class TestConfigurationUtil(unittest.TestCase):
    """
    Simple test cases to check the behavior of `Configuration` tools.
    We can't use the `patch` method as the dictionary state after
      the initializations is unknown due to user's configuration files.
    Values will be manually set in the tests below.
    """
    def test_get(self):
        configuration = Configuration()
        configuration.config = {
            'ip_settings': {
                'lan_ip_max_count': 2,
            },
            'temperature': {
                'use_fahrenheit': False
            }
        }

        self.assertEqual(
            configuration.config.get('ip_settings')['lan_ip_max_count'],
            2
        )
        self.assertFalse(
            configuration.config.get('temperature')['use_fahrenheit']
        )
        self.assertTrue(configuration.config.get('does_not_exist', True))
        self.assertIsNone(configuration.config.get('does_not_exist_either'))

    def test_load_configuration(self):
        configuration = Configuration()
        configuration.config = {
            'allow_overriding': True,
            'suppress_warnings': False,
            'colors_palette': {
                'use_unicode': False
            },
            'ip_settings': {
                'lan_ip_max_count': 2
            },
            'temperature': {
                'use_fahrenheit': False
            }
        }

        with tempfile.TemporaryDirectory(suffix='/') as temp_dir:
            # We create a fake temporary configuration file
            file = open(temp_dir + 'config.json', 'w')
            file.write("""\
{
    "allow_overriding": false,
    "suppress_warnings": true,
    "colors_palette": {
        "use_unicode": false
    },
    "ip_settings": {
        "lan_ip_max_count": 4
    },
    "temperature": {
        "use_fahrenheit": true
    }
}
""")
            file.close()

            # Let's load it into our `Configuration` instance
            configuration.load_configuration(temp_dir)

            # Let's check the result :S
            self.assertDictEqual(
                configuration.config,
                {
                    'allow_overriding': False,
                    'suppress_warnings': True,
                    'colors_palette': {
                        'use_unicode': False
                    },
                    'ip_settings': {
                        'lan_ip_max_count': 4
                    },
                    'temperature': {
                        'use_fahrenheit': True
                    }
                }
            )
            # The `stderr` file descriptor has changed due to
            #   the `suppress_warnings` option.
            self.assertNotEqual(configuration._stderr, sys.stderr)

            # Let's try to load the `config.json` file present in this project.
            configuration.load_configuration(os.getcwd() + '/archey/')

            # It should not happen as `allow_overriding` has been set to false.
            # Thus, the configuration is supposed to be the same as before.
            self.assertDictEqual(
                configuration.config,
                {
                    'allow_overriding': False,
                    'suppress_warnings': True,
                    'colors_palette': {
                        'use_unicode': False
                    },
                    'ip_settings': {
                        'lan_ip_max_count': 4
                    },
                    'temperature': {
                        'use_fahrenheit': True
                    }
                }
            )

    def test_update_recursive(self):
        configuration = Configuration()
        configuration.config = {
            'allow_overriding': True,
            'suppress_warnings': False,
            'colors_palette': {
                'use_unicode': False
            },
            'default_strings': {
                'no_address': 'No Address',
                'not_detected': 'Not detected',
            },
            'ip_settings': {
                'lan_ip_max_count': 2
            },
            'temperature': {
                'use_fahrenheit': False
            }
        }

        # We change existing values, add new ones, and omit some others.
        configuration._update_recursive(
            configuration.config,
            {
                'suppress_warnings': True,
                'colors_palette': {
                    'use_unicode': False
                },
                'default_strings': {
                    'no_address': '\xde\xad \xbe\xef',
                    'not_detected': 'Not detected',
                    'virtual_environment': 'Virtual Environment',
                },
                'temperature': {
                    'a_weird_new_dict': [
                        None,
                        'l33t',
                        {
                            'really': 'one_more_?'
                        }
                    ]
                }
            }
        )

        self.assertDictEqual(
            configuration.config,
            {
                'allow_overriding': True,
                'suppress_warnings': True,
                'colors_palette': {
                    'use_unicode': False
                },
                'default_strings': {
                    'no_address': '\xde\xad \xbe\xef',
                    'not_detected': 'Not detected',
                    'virtual_environment': 'Virtual Environment',
                },
                'ip_settings': {
                    'lan_ip_max_count': 2
                },
                'temperature': {
                    'use_fahrenheit': False,
                    'a_weird_new_dict': [
                        None,
                        'l33t',
                        {
                            'really': 'one_more_?'
                        }
                    ]
                }
            }
        )


if __name__ == '__main__':
    unittest.main()
