.. include:: ../README.rst
    :start-after: _readme_intro_start:
    :end-before: _readme_intro_end:
    
.. image:: ./img/quickstart.gif
    :alt: Tutor local quickstart
    :target: https://terminalizer.com/view/91b0bfdd557

----------------------------------

.. include:: quickstart.rst
    :start-line: 1

.. toctree::
   :maxdepth: 2
   :caption: User guide

   intro
   install
   quickstart
   configuration
   local
   k8s
   dev
   plugins
   extra
   troubleshooting
   tutor
   faq

Source code
-----------

The complete source code for Tutor is available on Github: https://github.com/overhangio/tutor

.. include:: ../README.rst
    :start-after: _readme_support_start:
    :end-before: _readme_support_end:
    
.. include:: ../README.rst
    :start-after: _readme_contributing_start:
    :end-before: _readme_contributing_end:
    
License
-------

This work is licensed under the terms of the `GNU Affero General Public License (AGPL) <https://github.com/overhangio/tutor/blob/master/LICENSE.txt>`_.

The AGPL license covers the Tutor code, including the Dockerfiles, but not the content of the Docker images which can be downloaded from https://hub.docker.com. Software other than Tutor provided with the docker images retain their original license.

The :ref:`Tutor Web UI <webui>` depends on the `Gotty <https://github.com/yudai/gotty/>`_ binary, which is provided under the terms of the `MIT license <https://github.com/yudai/gotty/blob/master/LICENSE>`_.
