.. _k8s:

Kubernetes deployment
=====================

With the same docker images we created for :ref:`single server deployment <local>` and :ref:`local development <development>`, we can launch an Open edX platform on Kubernetes. Always in 1 click, of course :)

A word of warning: managing a Kubernetes platform is a fairly advanced endeavour. In this documentation, we assume familiarity with Kubernetes. Running an Open edX platform with Tutor on a single server or in a Kubernetes cluster are two very different things. The local Open edX install was designed such that users with no prior experience with system administration could still launch an Open edX platform. It is *not* the case for the installation method outlined here.

Consider yourself warned :)

Requirements
------------

Version
~~~~~~~

Tutor was tested with server version 1.14.1 and client 1.14.3.

Memory
~~~~~~

In the following, we assume you have access to a working Kubernetes cluster. `kubectl` should use your cluster configuration by default. To launch a cluster locally, you may try out Minikube. Just follow the `official installation instructions <https://kubernetes.io/docs/setup/minikube/>`_.

The Kubernetes cluster should have at least 4Gb of RAM on each node. When running Minikube, the virtual machine should have that much allocated memory. See below for an example with VirtualBox:

.. image:: img/virtualbox-minikube-system.png
    :alt: Virtualbox memory settings for Minikube

Ingress controller and SSL/TLS certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As of Tutor v11, it is no longer required to setup an Ingress controller to access your platform. Instead Caddy exposes a LoadBalancer service and SSL/TLS certificates are transparently generated at runtime.

S3-like object storage with `MinIO <https://www.minio.io/>`_
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Like many web applications, Open edX needs to persist data. In particular, it needs to persist files uploaded by students and course designers. In the local installation, these files are persisted to disk, on the host filesystem. But on Kubernetes, it is difficult to share a single filesystem between different pods. This would require persistent volume claims with `ReadWriteMany` access mode, and these are difficult to setup.

Luckily, there is another solution: at `edx.org <edx.org>`_, uploaded files are persisted on AWS S3: Open edX is compatible out-of-the-box with the S3 API for storing user-generated files. The problem with S3 is that it introduces a dependency on AWS. To solve this problem, Tutor comes with a plugin that emulates the S3 API but stores files on premises. This is achieved thanks to `MinIO <https://www.minio.io/>`_. If you want to deploy a production platform to Kubernetes, you will most certainly need to enable the ``minio`` plugin::

    tutor plugins enable minio

The "minio.LMS_HOST" domain name will have to point to your Kubernetes cluster. This will not be necessary if you have a CNAME from "\*.LMS_HOST" to "LMS_HOST", of course.

Kubernetes dashboard
~~~~~~~~~~~~~~~~~~~~

This is not a requirement per se, but it's very convenient to have a visual interface of the Kubernetes cluster. We suggest the official `Kubernetes dashboard <https://github.com/kubernetes/dashboard/>`_. Depending on your Kubernetes provider, you may need to install a dashboard yourself. There are generic instructions on the `project's README <https://github.com/kubernetes/dashboard/blob/master/README.md>`_. AWS provides `specific instructions <https://docs.aws.amazon.com/eks/latest/userguide/dashboard-tutorial.html>`_.

On Minikube, the dashboard is already installed. To access the dashboard, run::

    minikube dashboard

Technical details
-----------------

Under the hood, Tutor wraps ``kubectl`` commands to interact with the cluster. The various commands called by Tutor are printed in the console, so that you can reproduce and modify them yourself.

Basically, the whole platform is described in manifest files stored in ``$(tutor config printroot)/env/k8s``. There is also a ``kustomization.yml`` file at the project root for `declarative application management <https://kubectl.docs.kubernetes.io/pages/app_management/apply.html>`_. This allows us to start and update resources with commands similar to ``kubectl apply -k $(tutor config printroot) --selector=...`` (see the ``kubectl apply`` `official documentation <https://kubectl.docs.kubernetes.io/pages/app_management/apply.html>`_).

The other benefit of ``kubectl apply`` is that it allows you to customise the Kubernetes resources as much as you want. For instance, the default Tutor configuration can be extended by a ``kustomization.yml`` file stored in ``$(tutor config printroot)/env-custom/`` and which would start with::

    apiVersion: kustomize.config.k8s.io/v1beta1
    kind: Kustomization
    bases:
    - ../env/
    ...

To learn more about "kustomizations", refer to the `official documentation <https://kubectl.docs.kubernetes.io/pages/app_customization/introduction.html>`__.

Quickstart
----------

Launch the platform on Kubernetes in one command::

    tutor k8s quickstart

All Kubernetes resources are associated to the "openedx" namespace. If you don't see anything in the Kubernetes dashboard, you are probably looking at the wrong namespace... 😉

.. image:: img/k8s-dashboard.png
    :alt: Kubernetes dashboard ("openedx" namespace)

The same ``tutor k8s quickstart`` command can be used to upgrade the cluster to the latest version.

Other commands
--------------

As with the :ref:`local installation <local>`, there are multiple commands to run operations on your Open edX platform. To view those commands, run::

    tutor k8s -h

In particular, the `tutor k8s start` command restarts and reconfigures all services by running ``kubectl apply``. That means that you can delete containers, deployments or just any other kind of resources, and Tutor will re-create them automatically. You should just beware of not deleting any persistent data stored in persistent volume claims. For instance, to restart from a "blank slate", run::

    tutor k8s stop
    tutor k8s start

All non-persisting data will be deleted, and then re-created.

Guides
------

Running a custom "openedx" Docker image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some Tutor plugins and customization procedures require that the "openedx" image be rebuilt (see :ref:`customization <custom_openedx_docker_image>`). This is for instance the case if you want to :ref:`install a custom XBlock <custom_extra_xblocks>` or :ref:`run an edx-platform fork <edx_platform_fork>`. When running Open edX on Kubernetes, your custom images will have to be downloaded from a custom registry. You should define a custom image name, build the image and then push them to your custom registry. For instance, for the "openedx" image::

    tutor config save --set "DOCKER_IMAGE_OPENEDX=docker.io/myusername/openedx:{{ TUTOR_VERSION }}"
    tutor images build openedx
    tutor images push openedx

Updating docker images
~~~~~~~~~~~~~~~~~~~~~~

Kubernetes does not provide a single command for updating docker images out of the box. A `commonly used trick <https://github.com/kubernetes/kubernetes/issues/33664>`_ is to modify an innocuous label on all resources::

    kubectl patch -k "$(tutor config printroot)/env" --patch "{\"spec\": {\"template\": {\"metadata\": {\"labels\": {\"date\": \"`date +'%Y%m%d-%H%M%S'`\"}}}}}"


