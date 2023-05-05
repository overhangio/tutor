Uninstallation
==============

It is fairly easy to completely uninstall Tutor and to delete the Open edX platforms that are running locally.

First of all, stop any locally-running platform and remove all Tutor containers::

    tutor local dc down --remove-orphans
    tutor dev dc down --remove-orphans

Then, delete all data associated with your Open edX platform::

    # WARNING: this step is irreversible
    sudo rm -rf "$(tutor config printroot)"

Finally, uninstall Tutor itself::

    # If you installed tutor from source
    pip uninstall tutor

    # If you downloaded the tutor binary
    sudo rm /usr/local/bin/tutor

    # Optionally, you may want to remove Tutor plugins installed.
    # You can get a list of the installed plugins:
    pip freeze | grep tutor
    # You can then remove them using the following command:
    pip uninstall <plugin-name>
    