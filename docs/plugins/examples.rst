.. _plugins_examples:

========
Examples
========

The following are simple examples of :ref:`Tutor plugins <plugins>` that can be used to modify the behaviour of Open edX.

Skip email validation for new users
===================================

::

    from tutor import hooks

    hooks.Filters.ENV_PATCHES.add_item(
        (
            "common-env-features",
            """
    "SKIP_EMAIL_VALIDATION": true
    """
        )
    )

Enable bulk enrollment view in the LMS
======================================

::

    from tutor import hooks

    hooks.Filters.ENV_PATCHES.add_item(
        (
            "lms-env-features",
            """
    "ENABLE_BULK_ENROLLMENT_VIEW": true
    """
        )
    )

Enable Google Analytics
=======================

::

  from tutor import hooks

  hooks.Filters.ENV_PATCHES.add_items([
      (
          "openedx-common-settings",
          "GOOGLE_ANALYTICS_4_ID = 'MY-MEASUREMENT-ID'"
      ),
      (
          "mfe-lms-common-settings",
          "MFE_CONFIG['GOOGLE_ANALYTICS_4_ID'] = 'MY-MEASUREMENT-ID'"
      ),
  ])

.. note::
    Please be aware that as of May 2023 Google Analytics support has been upgraded from Google Universal Analytics to Google Analytics 4 and you may need to update your configuration as mentioned in the `Open edX docs <https://docs.openedx.org/en/latest/site_ops/how-tos/google-analytics.html>`__.



Enable SAML authentication
==========================

::

    from tutor import hooks

    hooks.Filters.ENV_PATCHES.add_items([
        (
            "common-env-features",
            '"ENABLE_THIRD_PARTY_AUTH": true',
        ),
        (
            "openedx-lms-common-settings",
            """
    # saml special settings
    AUTHENTICATION_BACKENDS += ["common.djangoapps.third_party_auth.saml.SAMLAuthBackend", "django.contrib.auth.backends.ModelBackend"]
    """
        ),
        (
            "openedx-auth",
            """
    "SOCIAL_AUTH_SAML_SP_PRIVATE_KEY": "yoursecretkey",
    "SOCIAL_AUTH_SAML_SP_PUBLIC_CERT": "yourpubliccert"
            """
        ),
    ])

Do not forget to replace "yoursecretkey" and "yourpubliccert" with your own values.
