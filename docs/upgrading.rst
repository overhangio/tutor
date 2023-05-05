.. _upgrade:

Upgrading
=========

To upgrade Open edX or benefit from the latest features and bug fixes, you should simply upgrade Tutor. Start by upgrading the "tutor" package and its dependencies::

    pip install --upgrade "tutor[full]"

Then run the ``launch`` command again. Depending on your deployment target, run one of::

    tutor local launch # for local installations
    tutor dev launch   # for local development installations
    tutor k8s launch   # for Kubernetes installation

Upgrading with custom Docker images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you run :ref:`customised <configuration_customisation>` Docker images, you need to rebuild them before running ``launch``::

    tutor config save
    tutor images build all # specify here the images that you need to build
    tutor local launch

Upgrading to a new Open edX release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Major Open edX releases are published twice a year, in June and December, by the Open edX `Build/Test/Release working group <https://discuss.openedx.org/c/working-groups/build-test-release/30>`__. When a new Open edX release comes out, Tutor gets a major version bump (see :ref:`versioning`). Such an upgrade typically includes multiple breaking changes. Any upgrade is final because downgrading is not supported. Thus, when upgrading your platform from one major version to the next, it is strongly recommended to do the following:

1. Read the changes listed in the `CHANGELOG.md <https://github.com/overhangio/tutor/blob/master/CHANGELOG.md>`__ file. Breaking changes are identified by a "💥".
2. Perform a backup. On a local installation, this is typically done with::

    tutor local stop
    sudo rsync -avr "$(tutor config printroot)"/ /tmp/tutor-backup/

3. If you created custom plugins, make sure that they are compatible with the newer release.
4. Test the new release in a sandboxed environment.
5. If you are running edx-platform, or some other repository from a custom branch, then you should rebase (and test) your changes on top of the latest release tag (see :ref:`edx_platform_fork`).

The process for upgrading from one major release to the next works similarly to any other upgrade, with the ``launch`` command (see above). The single difference is that if the ``launch`` command detects that your tutor environment was generated with an older release, it will perform a few release-specific upgrade steps. These extra upgrade steps will be performed just once. But they will be ignored if you updated your local environment (for instance: with ``tutor config save``) before running ``launch``. This situation typically occurs if you need to re-build some Docker images (see above). In such a case, you should make use of the ``upgrade`` command. For instance, to upgrade a local installation from Nutmeg to Olive and rebuild some Docker images, run::

    tutor config save
    tutor images build all # list the images that should be rebuilt here
    tutor local upgrade --from=nutmeg
    tutor local launch