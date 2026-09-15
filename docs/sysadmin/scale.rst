.. _scale:

Running Open edX at scale
=========================

Does Open edX scale? This is the $10⁶ question when it comes to Tutor and Open edX deployments. The short answer is "yes". The longer answer is also "yes", but the details will very much depend on what we mean by "scaling".

Depending on the context, "scaling" can imply different things:

1. `Vertical scaling <https://en.wikipedia.org/wiki/Scalability#VERTICAL-SCALING>`__: increasing platform capacity by allocating more resources to a single server.
2. `Horizontal scaling <https://en.wikipedia.org/wiki/Scalability#HORIZONTAL-SCALING>`__: the ability to serve an infinitely increasing number of users with consistent performance and linear costs.
3. `High availability (HA) <https://en.wikipedia.org/wiki/High_availability>`__: the ability of the platform to remain fully functional despite one or more components being unavailable.

All of these can be achieved with Tutor and Open edX, but the method to attain either differs greatly. First of all, the range of available solutions will depend on which deployment target is used. Tutor supports installations of Open edX on a single server with the :ref:`"local" <local>` deployment target, where Docker containers are orchestrated by docker-compose. On a single server, by definition, the server is a single point of failure (`SPOF <https://en.wikipedia.org/wiki/Single_point_of_failure>`__). Thus, high availability is out of the question with a single server. To achieve high availability, it is necessary to deploy to a cluster of multiple servers. But while docker-compose is a great tool for managing single-server deployments, it is simply inappropriate for deploying to a cluster. Tutor also supports deploying to a Kubernetes cluster (see :ref:`k8s`). This is the recommended solution to deploy Open edX "at scale".

Scaling with a single server
----------------------------

Options are limited when it comes to scaling an Open edX platform deployed on a single-server. High availability is out of the question and the number of users that your platform can serve simultaneously will be limited by the server capacity.

Fortunately, Open edX was designed to run at scale -- most notably at `edX.org <edx.org>`__, but also on large national education platforms. Thus, performance will not be limited by the backend software, but only by the hardware.

Increasing web server capacity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As the server CPU and memory are increased, the request throughput can be increased by adjusting the number of Granian workers (see :ref:`configuration docs <openedx_configuration>`). By default, the "lms" and "cms" containers each spawn 2 Granian workers. The number of workers should be increased if you observe an increase in the latency of user requests but CPU usage remains below 100%. To increase the number of workers for the LMS and the CMS, run for example::

    tutor config save \
      --set OPENEDX_LMS_GRANIAN_WORKERS=8 \
      --set OPENEDX_CMS_GRANIAN_WORKERS=4
    tutor local restart lms cms

The right values will very much depend on your server's available memory and CPU performance, as well as the maximum number of simultaneous users who use your platform. As an example data point, it was reported that a large Open edX platform can serve up to 500k unique users per week on a virtual server with 8 vCPU and 16 GB memory.

Offloading data storage
~~~~~~~~~~~~~~~~~~~~~~~

Aside from web workers, the most resource-intensive services are in the data persistence layer. They are, by decreasing resource usage:

- `MySQL <https://www.mysql.com>`__: structured, consistent data storage which is the default destination of all data.
- `MongoDB <https://www.mongodb.com>`__: structured storage of course data.
- `Redis <https://redis.io/>`__: caching and asynchronous task management.
- `MinIO <https://min.io>`__: S3-like object storage for user-uploaded files, which is enabled by the `tutor-minio <https://github.com/overhangio/tutor-minio>`__ plugin. It is possible to replace MinIO by direct filesystem storage (the default), but scaling will then become much more difficult down the road.
- `Meilisearch <https://www.meilisearch.com>`__: indexing of course contents and forum topics, mostly for search. Meilisearch is never a source of truth in Open edX, and the data can thus be trashed and re-created safely.

When attempting to scale a single-server deployment, we recommend starting by offloading some of these stateful data storage components, in the same order of priority. There are multiple benefits:

1. It will free up some resources both for the web workers and the data storage components.
2. It is the first step towards horizontal scaling of the web workers.
3. It becomes possible to either install every component as a separate service or rely on 3rd-party SaaS with high availability.

Moving each of the data storage components is a fairly straightforward process, although details vary for every component. For instance, for the MySQL database, start by disabling the locally running MySQL instance::

    tutor config save --set RUN_MYSQL=false

Then, migrate the data located at ``$(tutor config printroot)/data/mysql`` to the new MySQL instance. Configure the Open edX platform to point at the new database::

    tutor config save \
      --set MYSQL_HOST=yourdb.com \
      --set MYSQL_PORT=3306 \
      --set MYSQL_ROOT_USERNAME=root \
      --set MYSQL_ROOT_PASSWORD=p4ssw0rd

The changes will be taken into account the next time the platform is restarted.

Beware that moving the data components to dedicated servers has the potential of creating new single points of failure (`SPOF <https://en.wikipedia.org/wiki/Single_point_of_failure>`__). To avoid this situation, each component should be installed as a highly available service (or as a highly available SaaS).

Scaling with multiple servers
-----------------------------

Horizontally scaling web services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As the number of users of a web platform increases, they put increased pressure on the web workers that respond to their requests. Thus, in most cases, web worker performance is the first bottleneck that system administrators have to face when their service becomes more popular. Initially, any given Kubernetes-based Tutor platform ships with one replica for each deployment. To increase (or reduce) the number of replicas for any given service, run ``tutor k8s scale <name> <number of replicas>``. Behind the scenes, this command will trigger a ``kubectl scale --replicas=...`` command that will seamlessly increase the number of pods for that deployment.

In Open edX multiple web services are exposed to the outside world. The ones that usually receive the most traffic are, in decreasing order, the LMS, the CMS, and the forum (assuming the `tutor-forum <https://github.com/overhangio/tutor-forum>`__ plugin was enabled). As an example, all three deployment replicas can be scaled by running::

    tutor k8s scale lms 8
    tutor k8s scale cms 4
    tutor k8s scale forum 2

Highly-available architecture, autoscaling, ...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is only so much that Tutor can do for you, and scaling some components falls beyond the scope of Tutor. For instance, it is your responsibility to make sure that your Kubernetes cluster has a `highly available control plane <https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/high-availability/>`__ and `topology <https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/ha-topology/>`__. Also, it is possible to achieve `autoscaling <https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/>`__; but it is your responsibility to setup latency metrics collection and to configure the scaling policies.
