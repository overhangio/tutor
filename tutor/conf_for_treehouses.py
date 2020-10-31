import click
import subprocess
import re

from . import config as tutor_config
from . import env
from . import exceptions
from . import fmt
from .__about__ import __version__

process = subprocess.run(["sudo","treehouses", "tor"],
                          stdout=subprocess.PIPE)
onion_address = process.stdout[11:-10]
ONION_ADDRESS = onion_address.decode('utf-8')

def update(root, interactive=True):
    """
    Load and save the configuration.
    """
    lms = f"{ONION_ADDRESS}"
    cms = f"studio.{ONION_ADDRESS}"
    email = f"contact@{ONION_ADDRESS}"

    config, defaults = tutor_config.load_all(root)
    config["LMS_HOST"] = lms
    config["CMS_HOST"] = cms 
    config["PLATFORM_NAME"] = "OpenEdx"
    config["CONTACT_EMAIL"] = email
    config["LANGUAGE_CODE"] = "en"
    config["ACTIVATE_HTTPS"] = False
    tutor_config.save_config_file(root, config)
    tutor_config.merge(config, defaults)
    return config
