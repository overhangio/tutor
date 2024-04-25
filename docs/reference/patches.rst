.. _patches:

======================
Template patch catalog
======================

This is the list of all patches used across Tutor (outside of any plugin). Alternatively, you can search for patches in Tutor templates by grepping the source code::

    git clone https://github.com/overhangio/tutor
    cd tutor
    git grep "{{ patch" -- tutor/templates

Or you can list all available patches with the following command::

    tutor config patches list

See also `this GitHub search <https://github.com/search?utf8=✓&q={{+patch+repo%3Aoverhangio%2Ftutor+path%3A%2Ftutor%2Ftemplates&type=Code&ref=advsearch&l=&l= 8>`__.

.. patch:: caddyfile

``caddyfile``
=============

File: ``apps/caddy/Caddyfile``

Add here Caddy directives to redirect traffic from the outside to your service containers. You should make use of the "proxy" snippet that simplifies configuration and automatically configures logging. Also, make sure to use the ``$default_site_port`` environment variable to make sure that your service will be accessible both when HTTPS is enabled or disabled. For instance::

    {{ MYPLUGIN_HOST }}{$default_site_port} {
        import proxy "myservice:8000"
    }

See the `Caddy reference documentation <https://caddyserver.com/docs/caddyfile>`__ for more information.

.. patch:: caddyfile-cms

``caddyfile-cms``
=================

File: ``apps/caddy/Caddyfile``

.. patch:: caddyfile-global

``caddyfile-global``
====================

File: ``apps/caddy/Caddyfile``

.. patch:: caddyfile-lms

``caddyfile-lms``
=================

File: ``apps/caddy/Caddyfile``

.. patch:: caddyfile-proxy

``caddyfile-proxy``
===========================

File: ``apps/caddy/Caddyfile``

.. patch:: cms-env

``cms-env``
===========

File: ``apps/openedx/config/cms.env.yml``

.. patch:: cms-env-features

``cms-env-features``
====================

File: ``apps/openedx/config/cms.env.yml``

.. patch:: common-env-features

``common-env-features``
=======================

Files: ``apps/openedx/config/cms.env.yml``, ``apps/openedx/config/lms.env.yml``

.. patch:: dev-docker-compose-jobs-services

``dev-docker-compose-jobs-services``
====================================

File: ``dev/docker-compose.jobs.yml``

.. patch:: k8s-deployments

``k8s-deployments``
===================

File: ``k8s/deployments.yml``

.. patch:: k8s-jobs

``k8s-jobs``
============

File: ``k8s/jobs.yml``

.. patch:: k8s-override

``k8s-override``
================

File: ``k8s/override.yml``

Any Kubernetes resource definition in this patch will override the resource defined by Tutor, provided that their names match. See :ref:`Customizing Kubernetes resources <customizing_kubernetes_sources>` for an example.

.. patch:: k8s-services

``k8s-services``
================

File: ``k8s/services.yml``

.. patch:: k8s-volumes

``k8s-volumes``
===============

File: ``k8s/volumes.yml``

.. patch:: kustomization

``kustomization``
=================

File: ``kustomization.yml``

.. patch:: kustomization-commonlabels

``kustomization-commonlabels``
==============================

File: ``kustomization.yml``

.. patch:: kustomization-configmapgenerator

``kustomization-configmapgenerator``
====================================

File: ``kustomization.yml``

.. patch:: kustomization-patches-strategic-merge

``kustomization-patches-strategic-merge``
=========================================

File: ``kustomization.yml``

This can be used to add more Kustomization patches that make use of the `strategic merge mechanism <https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/#customizing>`__. 

.. patch:: kustomization-resources

``kustomization-resources``
===========================

File: ``kustomization.yml``

.. patch:: lms-env

``lms-env``
===========

File: ``apps/openedx/config/lms.env.yml``

.. patch:: lms-env-features

``lms-env-features``
====================

File: ``apps/openedx/config/lms.env.yml``

.. patch:: local-docker-compose-caddy-aliases

``local-docker-compose-caddy-aliases``
======================================

File: ``local/docker-compose.prod.yml``

.. patch:: local-docker-compose-cms-dependencies

``local-docker-compose-cms-dependencies``
=========================================

File: ``local/docker-compose.yml``

.. patch:: local-docker-compose-dev-services

``local-docker-compose-dev-services``
=====================================

File: ``dev/docker-compose.yml``

.. patch:: local-docker-compose-jobs-services

``local-docker-compose-jobs-services``
======================================

File: ``local/docker-compose.jobs.yml``

.. patch:: local-docker-compose-lms-dependencies

``local-docker-compose-lms-dependencies``
=========================================

File: ``local/docker-compose.yml``

.. patch:: local-docker-compose-permissions-command

``local-docker-compose-permissions-command``
============================================

File: ``apps/permissions/setowners.sh``

Add commands to this script to set ownership of bind-mounted docker-compose volumes at runtime. See :patch:`local-docker-compose-permissions-volumes`.


.. patch:: local-docker-compose-permissions-volumes

``local-docker-compose-permissions-volumes``
============================================

File: ``local/docker-compose.yml``

Add bind-mounted volumes to this patch to set their owners properly. See :patch:`local-docker-compose-permissions-command`.

.. patch:: local-docker-compose-prod-services

``local-docker-compose-prod-services``
======================================

File: ``local/docker-compose.prod.yml``

.. patch:: local-docker-compose-services

``local-docker-compose-services``
=================================

File: ``local/docker-compose.yml``

.. patch:: openedx-auth

``openedx-auth``
================

File: ``apps/openedx/config/partials/auth.yml``

.. patch:: openedx-cms-common-settings

``openedx-cms-common-settings``
===============================

File: ``apps/openedx/settings/partials/common_cms.py``

.. patch:: openedx-cms-development-settings

``openedx-cms-development-settings``
====================================

File: ``apps/openedx/settings/cms/development.py``

.. patch:: openedx-cms-production-settings

``openedx-cms-production-settings``
===================================

File: ``apps/openedx/settings/cms/production.py``

.. patch:: openedx-common-assets-settings

``openedx-common-assets-settings``
==================================

File: ``build/openedx/settings/partials/assets.py``


.. patch:: openedx-common-i18n-settings

``openedx-common-i18n-settings``
================================

File: ``build/openedx/settings/partials/i18n.py``

.. patch:: openedx-common-settings

``openedx-common-settings``
===========================

File: ``apps/openedx/settings/partials/common_all.py``

.. patch:: openedx-dev-dockerfile-post-python-requirements

``openedx-dev-dockerfile-post-python-requirements``
===================================================

File: ``build/openedx/Dockerfile``

.. patch:: openedx-development-settings

``openedx-development-settings``
================================

Files: ``apps/openedx/settings/cms/development.py``, ``apps/openedx/settings/lms/development.py``

.. patch:: openedx-dockerfile

``openedx-dockerfile``
======================

File: ``build/openedx/Dockerfile``

.. patch:: openedx-dockerfile-final

``openedx-dockerfile-final``
============================

File: ``build/openedx/Dockerfile``

.. patch:: openedx-dockerfile-git-patches-default

``openedx-dockerfile-git-patches-default``
==========================================

File: ``build/openedx/Dockerfile``

.. patch:: openedx-dockerfile-minimal

``openedx-dockerfile-minimal``
==============================

File: ``build/openedx/Dockerfile``

.. patch:: openedx-dockerfile-post-git-checkout

``openedx-dockerfile-post-git-checkout``
========================================

File: ``build/openedx/Dockerfile``

.. patch:: openedx-dockerfile-post-python-requirements

``openedx-dockerfile-post-python-requirements``
===============================================

File: ``build/openedx/Dockerfile``

.. patch:: openedx-dockerfile-pre-assets

``openedx-dockerfile-pre-assets``
=================================

File: ``build/openedx/Dockerfile``

.. patch:: openedx-lms-common-settings

``openedx-lms-common-settings``
===============================

File: ``apps/openedx/settings/partials/common_lms.py``

Python-formatted LMS settings used both in production and development.

.. patch:: openedx-lms-development-settings

``openedx-lms-development-settings``
====================================

File: ``apps/openedx/settings/lms/development.py``

Python-formatted LMS settings in development. Values defined here override the values from :patch:`openedx-lms-common-settings` or :patch:`openedx-lms-production-settings`.

.. patch:: openedx-lms-production-settings

``openedx-lms-production-settings``
===================================

File: ``apps/openedx/settings/lms/production.py``

Python-formatted LMS settings in production. Values defined here override the values from :patch:`openedx-lms-common-settings`.

``redis-conf``
==============

File: ``apps/redis/redis.conf``

Implement this patch to override hard-coded Redis configuration values. See the `Redis configuration reference <https://redis.io/docs/management/config-file/>`__`.

``uwsgi-config``
================

File: ``apps/openedx/settings/uwsgi.ini``

A .INI formatted file used to extend or override the uWSGI configuration.

Check the uWSGI documentation for more details about the `.INI format <https://uwsgi-docs.readthedocs.io/en/latest/Configuration.html#ini-files>`__ and the `list of available options <https://uwsgi-docs.readthedocs.io/en/latest/Options.html>`__.

.. patch:: uwsgi-config
