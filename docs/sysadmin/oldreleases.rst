Upgrading from older releases
-----------------------------

Upgrading from v3+
~~~~~~~~~~~~~~~~~~

Just upgrade Tutor using your :ref:`favorite installation method <install>` and run launch again::

    tutor local launch

Upgrading from v1 or v2
~~~~~~~~~~~~~~~~~~~~~~~

Versions 1 and 2 of Tutor were organized differently: they relied on many different ``Makefile`` and ``make`` commands instead of a single ``tutor`` executable. To migrate from an earlier version, you should first stop your platform::

    make stop

Then, install Tutor using one of the :ref:`installation methods <install>`. Then, create the Tutor project root and move your data::

    mkdir -p "$(tutor config printroot)"
    mv config.json data/ "$(tutor config printroot)"

Finally, launch your platform with::

    tutor local launch
