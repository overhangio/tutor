import yaml

def load(stream):
    return yaml.load(stream, Loader=yaml.SafeLoader)

def dump(content, fileobj):
    yaml.dump(content, fileobj, default_flow_style=False)

def parse_value(v):
    """
    Parse a yaml-formatted string. This is fairly basic and should only be used
    for parsing of elementary values.
    """
    if v.isdigit():
        v = int(v)
    elif v == "null":
        v = None
    elif v in ["true", "false"]:
        v = (v == "true")
    return v
