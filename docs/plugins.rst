.. _plugins:

Plugins
=======

Tutor comes with a plugin system that allows anyone to customise the deployment of an Open edX platform very easily. The vision behind this plugin system is that users should not have to fork the Tutor repository to customise their deployments. For instance, if you have created a new application that integrates with Open edX, you should not have to describe how to manually patch the platform settings, ``urls.py`` or ``*.env.json`` files. Instead, you can create a "tutor-myapp" plugin for Tutor. Then, users will start using your application in three simple steps::

    # 1) Install the plugin
    pip install tutor-myapp
    # 2) Enable the plugin
    tutor plugins enable myapp
    # 3) Reconfigure and restart the platform
    tutor local quickstart

In the following we see how to use and create Tutor plugins.

Commands
--------

List installed plugins::
  
    tutor plugins list
    
Enable/disable a plugin::
  
    tutor plugins enable myplugin
    tutor plugins disable myplugin
    
After enabling or disabling a plugin, the environment should be re-generated with::
  
    tutor config save
    
.. _existing_plugins:

Existing plugins
----------------

- `Course discovery <https://pypi.org/project/tutor-discovery>`__: Deploy an API for interacting with your course catalog
- `Ecommerce <https://pypi.org/project/tutor-ecommerce>`__: Sell courses and products on your Open edX platform
- `Figures <https://pypi.org/project/tutor-figures>`__: Visualize daily stats about course engagement
- `MinIO <https://pypi.org/project/tutor-minio>`__: S3 emulator for object storage and scalable Open edX deployment.
- `Notes <https://pypi.org/project/tutor-notes>`__:  Allows students to annotate portions of the courseware.
- `Xqueue <https://pypi.org/project/tutor-xqueue>`__: for external grading

Plugin development
------------------
 
.. toctree::
   :maxdepth: 2

   plugins/api
   plugins/gettingstarted