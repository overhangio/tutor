.. _mobile:

Mobile Android application
==========================

With Tutor, you can build an Android mobile application for your platform. First, generate the required environment::

    tutor android env

Then, build the app in debug mode::

    tutor android build debug

The ``.apk`` file will then be available in ``$TUTOR_ROOT/data/android``. Transfer it to an Android phone to install the application. You should be able to sign in and view available courses.

Releasing an Android app
------------------------

**Note**: this is an untested feature.

Releasing an Android app on the Play Store requires to build the app in release mode. To do so, edit the ``$TUTOR_ROOT/config.yml`` configuration file and define the following variables::
    
    ANDROID_RELEASE_STORE_PASSWORD
    ANDROID_RELEASE_KEY_PASSWORD
    ANDROID_RELEASE_KEY_ALIAS

Then, place your keystore file in ``$TUTOR_ROOT/env/android/app.keystore``. Finally, build the application with::

    tutor android build release

Customising the Android app
---------------------------

Customising the application, such as the logo or the background image, is currently not supported. If you are interested by this feature, please tell us about it in the Tutor `discussion forums <https://discuss.overhang.io>`_.
