.. _k8s:

Kubernetes deployment
=====================

With the same docker images we created for :ref:`single server deployment <local>` and :ref:`local development <development>`, we can launch an Open edX platform on Kubernetes. Always in 1 click, of course :)

A word of warning: managing a Kubernetes platform is a fairly advanced endeavour. In this documentation, we assume familiarity with Kubernetes. Running an Open edX platform with Tutor on a single server or in a Kubernetes cluster are two very different things. The local Open edX install was designed such that users with no prior experience with system administration could still launch an Open edX platform. It is *not* the case for the installation method outlined here. You have been warned :)

Requirements
------------

Memory
~~~~~~

In the following, we assume you have access to a working Kubernetes cluster. `kubectl` should use your cluster configuration by default. To launch a cluster locally, you may try out Minikube. Just follow the `official installation instructions <https://kubernetes.io/docs/setup/minikube/>`_.

The Kubernetes cluster should have at least 4Gb of RAM on each node. When running Minikube, the virtual machine should have that much allocated memory. See below for an example with VirtualBox::
  
.. image:: img/virtualbox-minikube-system.png
    :alt: Virtualbox memory settings for Minikube

Ingress controller
~~~~~~~~~~~~~~~~~~

In order to access your platform, you will have to setup an Ingress controller. Instructions vary for each cloud provider. To deploy an Nginx Ingress controller, it might be as simple as running::

    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/nginx-0.24.1/deploy/mandatory.yaml
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/nginx-0.24.1/deploy/provider/cloud-generic.yaml

See the `official instructions <https://kubernetes.github.io/ingress-nginx/deploy/>`_ for more details.

On Minikube, run::
  
    minikube addons enable ingress

With Kubernetes, your Open edX platform will *not* be available at localhost or studio.localhost. Instead, you will have to access your platform with the domain names you specified for the LMS and the CMS. To do so on a local computer, you will need to add the following line to /etc/hosts::

    MINIKUBEIP yourdomain.com studio.yourdomain.com preview.yourdomain.com notes.yourdomain.com

where ``MINIKUBEIP`` should be replaced by the result of the command ``minikube ip``.

`ReadWriteMany` storage provider access mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some of the data volumes are shared between pods and thus require the `ReadWriteMany` access mode. We assume that a persistent volume provisioner with such capability is already installed on the cluster. For instance, on AWS the `AWS EBS <https://kubernetes.io/docs/concepts/storage/storage-classes/#aws-ebs>`_ provisioner is available. On DigitalOcean, there is `no such provider <https://www.digitalocean.com/docs/kubernetes/how-to/add-volumes/>`_ out of the box and you have to install one yourself.

On Minikube, the standard storage class uses the `k8s.io/minikube-hostpath <https://kubernetes.io/docs/concepts/storage/volumes/#hostpath>`_ provider, which supports `ReadWriteMany` access mode out of the box, so there is no need to install an extra provider. 

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

To learn more about "kustomizations", refer to the `official documentation <https://kubectl.docs.kubernetes.io/pages/app_customization/introduction.html>`_.

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

Missing features
----------------

For now, the following features from the local deployment are not supported:

- HTTPS certificates
- Xqueue

Kubernetes deployment is under intense development, and these features should be implemented pretty soon. Stay tuned 🤓
