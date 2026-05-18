.. _custom-translations:

Customizing and Overriding Translations
========================================

This tutorial covers two advanced translation scenarios:

* :ref:`Overriding strings from a custom Tutor theme <custom_translations_theme>`
* :ref:`Managing translations across forked repositories, custom plugins, and additional MFEs <custom_translations_repos>`

.. _custom_translations_theme:

Overriding Theme Translations (e.g. Indigo)
--------------------------------------------

Atlas-managed translations do not automatically include custom theme-level overrides.
If you need to override strings coming specifically from a Tutor theme (for example,
the Indigo theme), you must provide additional locale paths and patch the Open edX image.

A possible approach is:

1. Create a ``django.po`` file inside the theme repository:

   ``tutor-plugins/tutor-indigo/tutorindigo/locale/<lang>/LC_Messages/django.po``

   Example::

      msgid ""
      msgstr ""
      "Content-Type: text/plain; charset=utf-8\n"
      "Content-Transfer-Encoding: 8bit\n"

      msgid "Discover courses"
      msgstr "Kurse suchen"

   The header with charset specification is required. Without it, ``msgfmt`` compilation
   will fail for non-ASCII characters.

2. Compile the file using gettext::

      msgfmt django.po -o django.mo

3. Patch the Open edX Dockerfile (using a Tutor plugin) to copy the locale folder into the image::

      hooks.Filters.ENV_PATCHES.add_item((
      "openedx-dockerfile-pre-assets",
      """
      COPY --chown=app:app ./locale /openedx/extra_locale
      """
      ))

4. Register the additional locale path in both LMS and CMS::

      hooks.Filters.ENV_PATCHES.add_item((
      "lms-env",
      """
      LOCALE_PATHS: ["/openedx/extra_locale"]
      """
      ))
      hooks.Filters.ENV_PATCHES.add_item((
      "cms-env",
      """
      LOCALE_PATHS: ["/openedx/extra_locale"]
      """
      ))

5. Rebuild and restart::

      tutor images build openedx
      tutor local reboot

This ensures Django loads your theme-specific overrides alongside Atlas-pulled translations.

.. _custom_translations_repos:

Handling Translations in Custom or Forked Repositories
-------------------------------------------------------

If your deployment includes forked repositories, custom plugins, or additional MFEs alongside
upstream Open edX components, fork `openedx-translations
<https://github.com/openedx/openedx-translations>`_ and populate its ``translations/``
directory with your custom files.

The exact location depends on the repository type:

**Custom MFEs (new, not in upstream)**

For a brand-new MFE such as ``frontend-app-custom``, create one JSON file per language::

    translations/
    └── frontend-app-custom/
        └── src/i18n/messages/
            ├── ar.json
            ├── fr.json
            └── ...

Each file is a flat key/value JSON object where values are the translated strings (empty
string if not yet translated).

**Forked core MFEs (e.g. frontend-app-authoring, frontend-app-learning)**

Add or replace translation files at the same path used upstream::

    translations/
    └── frontend-app-authoring/
        └── src/i18n/messages/
            ├── ar.json
            └── ...

Keys that already exist in the upstream file will be overridden; new keys will be added.

**Custom plugins (Python / Django)**

Use the standard locale directory layout::

    translations/
    └── openedx-custom-plugin/
        └── conf/locale/
            ├── ar/LC_MESSAGES/django.po
            └── fr/LC_MESSAGES/django.po

**Theme repositories (e.g. a custom Indigo fork)**

Theme translations do not have their own folder. Merge them into ``edx-platform`` instead,
because Open edX loads theme strings from the platform's own locale directory at runtime::

    translations/
    └── edx-platform/
        └── conf/locale/
            ├── ar/LC_MESSAGES/django.po
            └── fr/LC_MESSAGES/django.po

.. note::
   You can write scripts to automate the steps of extracting strings from your repositories,
   isolating the ones that are unique to your fork, and merging them into the ``translations/``
   directory. What matters is that the final output follows the layout described above.

Once your ``translations/`` directory is ready, point Tutor at your fork::

    tutor config save \
        --set ATLAS_REPOSITORY=your-org/openedx-translations \
        --set ATLAS_REVISION=your-branch

Then rebuild and restart::

    tutor images build openedx mfe
    tutor local reboot
