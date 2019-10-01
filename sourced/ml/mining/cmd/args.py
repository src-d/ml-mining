import argparse


class ArgumentDefaultsHelpFormatterNoNone(argparse.ArgumentDefaultsHelpFormatter):
    """
    Pretty formatter of help message for arguments which adds default value to the end if it can.
    """

    def _get_help_string(self, action):
        if action.default is None:
            return action.help
        return super()._get_help_string(action)
