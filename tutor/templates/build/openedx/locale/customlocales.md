Add your custom translations to this folder, with the following filesystem structure:

    languagecode/
        LC_MESSAGES/
            django.po
            djangojs.po

Where "languagecode" is one of "fr", "de_DE", "zh_CN", etc.        

The localized string in the *.po file should have the following format:

    msgid "String to translate"
    msgstr "Your custom translation 你发音的东西 le bidule que vous voulez traduire"
