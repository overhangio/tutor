Command line interface (CLI)
============================

How do I navigate Tutor's command-line interface?
-------------------------------------------------

Tutor commands are structured in an easy-to-follow hierarchy. At the top level, there are command trees for image and configuration management::

    tutor config ...
    tutor images ...

as well as command trees for each mode in which Tutor can run::

    tutor local ...  # Commands for managing a local Open edX deployment.
    tutor k8s ...    # Commands for managing a Kubernetes Open edX deployment.
    tutor dev ...    # Commands for hacking on Open edX in development mode.

Within each mode, Tutor has subcommands for managing that type of Open edX instance. Many of them are common between modes, such as ``launch``, ``start``, ``stop``, ``exec``, and ``logs``. For example::

    tutor local logs  # View logs of a local deployment.
    tutor k8s logs    # View logs of a Kubernetes-managed deployment.
    tutor dev logs    # View logs of a development platform.

Many commands can be further parameterized to specify their target and options, for example::

  tutor local logs cms          # View logs of the CMS container in a local deployment.
  tutor k8s logs mysql          # View logs of MySQL in Kubernetes-managed deployment.
  tutor dev logs lms --tail 10  # View ten lines of logs of the LMS container in development mode.

And that's it! You do not need to understand Tutor's entire command-line interface to get started. Using the ``--help`` option that's availble on every command, it is easy to learn as you go. For an in-depth guide, you can also explore the :ref:`CLI Reference <cli_reference>`.
