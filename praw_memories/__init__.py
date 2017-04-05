import configparser
import os.path


def get_config(base=None, name='fyke_config.ini', path='.hoopyfyke',
               section='mainuser'):
    if base is None:
        base = os.path.expanduser('~')
        if base == '~':
            base = os.path.expandvars('%userprofile%')
    else:
        base = os.path.dirname(base)
    if path is None:
        path = '.'
    configfile = os.path.join(base, path, name)
    if not os.path.exists(configfile):
        raise FileNotFoundError(
                '%s: %s' % (configfile, os.path.abspath(configfile)))
    config = configparser.ConfigParser()
    config.read(configfile)
    if section:
        return config[section]
    return config
