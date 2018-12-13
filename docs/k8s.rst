.. _k8s:

Kubernetes deployment
=====================

With the same docker images we created for :ref:`single server deployment <step>` and :ref:`local development <development>`, we can launch an Open edX platform on Kubernetes. Always in 1 click, of course :)

::

           _       _              __            _                  
      __ _| |_ __ | |__   __ _   / _| ___  __ _| |_ _   _ _ __ ___ 
     / _` | | '_ \| '_ \ / _` | | |_ / _ \/ _` | __| | | | '__/ _ \
    | (_| | | |_) | | | | (_| | |  _|  __/ (_| | |_| |_| | | |  __/
     \__,_|_| .__/|_| |_|\__,_| |_|  \___|\__,_|\__|\__,_|_|  \___|
            |_|                                                    

Kubernetes deployment is currently an alpha feature, and we are hard at work to make it 100% reliable 🛠️ If you are interested in deploying Open edX to Kubernetes, please get in touch! Your input will be much appreciated.

Requirements
------------

In the following, we assume you have a working Kubernetes platform. For a start, you can run Kubernetes locally inside a VM with Minikube. Just follow the `official documentation <https://kubernetes.io/docs/setup/minikube/>`_.

Start Minikube::

    minikube start

Ingress addon must be installed::

    minikube addons enable ingress

At any point, access a UI to view the state of the platform with::

    minikube dashboard

In the following, all commands should be run inside the ``deploy/k8s`` folder::

    cd deploy/k8s

Quickstart
----------

Launch the platform on k8s in 1 click::

    make all
