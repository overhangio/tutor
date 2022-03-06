.. _plugins_examples:

Examples of Tutor plugins
=========================

The following are simple examples of :ref:`Tutor plugins <plugins>` that can be used to modify the behaviour of Open edX.

Skip email validation for new users
-----------------------------------

::

    name: skipemailvalidation
    version: 0.1.0
    patches:
      common-env-features: |
        "SKIP_EMAIL_VALIDATION": true

Enable bulk enrollment view in the LMS
--------------------------------------

::

    name: enablebulkenrollmentview
    version: 0.1.0
    patches:
      lms-env-features: |
        "ENABLE_BULK_ENROLLMENT_VIEW": true

Enable Google Analytics
-----------------------

::

    name: googleanalytics
    version: 0.1.0
    patches:
      openedx-common-settings: |
        # googleanalytics special settings
        GOOGLE_ANALYTICS_ACCOUNT = "UA-your-account"
        GOOGLE_ANALYTICS_TRACKING_ID = "UA-your-tracking-id"

Enable SAML authentication
--------------------------

::

    name: saml
    version: 0.1.0
    patches:
      common-env-features: |
        "ENABLE_THIRD_PARTY_AUTH": true

      openedx-lms-common-settings: |
        # saml special settings
        THIRD_PARTY_AUTH_BACKENDS = ["third_party_auth.saml.SAMLAuthBackend"]

      openedx-auth: |
        "SOCIAL_AUTH_SAML_SP_PRIVATE_KEY": "yoursecretkey",
        "SOCIAL_AUTH_SAML_SP_PUBLIC_CERT": "yourpubliccert"

Do not forget to replace "yoursecretkey" and "yourpubliccert" with your own values.
