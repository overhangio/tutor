.. _arm64:

Running Tutor on ARM-based systems
==================================

Tutor can be used on ARM64 systems, and official ARM64 docker images are available starting from Tutor v16.

For older versions of Tutor (v14 or v15), there are several options:

* Use emulation (via qemu or Rosetta 2) to run x86_64 images. Just make sure your installation of Docker supports emulation and use Tutor as normal. This may be 20%-100% slower than native images, depending on the emulation method.
* Use the `unofficial community-maintained ARM64 plugin <https://github.com/open-craft/tutor-contrib-arm64>`_ which will set the required settings for you and which includes unofficial docker images.
* Build your own ARM64 images, e.g. using ``tutor images build openedx permissions`` and/or ``tutor images build openedx-dev`` before launching the LMS.
