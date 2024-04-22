Using Google Mail as an SMTP server
===================================

By default, Tutor comes with a simple SMTP server for sending emails. Such a server has an important limitation: it does not implement mailing good practices, such as DKIM or SPF. As a consequence. the emails you send might be flagged as spam by their recipients. Thus, you might want to disable the SMTP server and run your own, for instance using your Google Mail account.

.. warning::
  Google Mail SMTP servers come with their own set of limitations. For instance, you are limited to sending 500 emails a day. Reference: https://support.google.com/mail/answer/22839

Authorization for Third-Party Access :

Google has deprecated the "Less Secure App Access." Instead, it is recommended to use "Application-Specific Passwords" for more secure access:

1. Ensure 2-Step Verification is enabled on your Google Account.
2. Visit Google Account Security.
3. Under "Signing in to Google," choose "App passwords."
4. You might need to sign in again. Once you do, select "Select app" and choose "Other (Custom name)" from the dropdown.
5. Enter a name that helps you remember the purpose of this password, like "Tutor SMTP".
6. Generate and note your 16-character app-specific password.

Reference: https://support.google.com/mail/answer/185833

Then, check that you can reach the Google Mail SMTP service from your own server::

    $ telnet smtp.gmail.com 587

If you get ``Connected to smtp.gmail.com.`` then it means that you can successfully reach the Google Mail SMTP servers. If not, you will have to reconfigure your firewall.

To exit the ``telnet`` shell, type ``ctrl+]``, then ``ctrl+d``.

Then, disable the SMTP server that comes with Tutor::

    $ tutor config save --set RUN_SMTP=false

Configure credentials to access your SMTP server::

    $ tutor config save \
      --set SMTP_HOST=smtp.gmail.com \
      --set SMTP_PORT=587 \
      --set SMTP_USE_SSL=false  \
      --set SMTP_USE_TLS=true \
      --set SMTP_USERNAME=YOURUSERNAME@gmail.com \
      --set SMTP_PASSWORD='YOURPASSWORD'

Don't forget to replace your email address and password in the prompt above. If your email password contains special characters, you might have to escape them.

Then, restart your platform::

    $ tutor local launch

That's it! You can send a test email with the following command::

    $ tutor local run --no-deps lms ./manage.py lms shell -c \
      "from django.core.mail import send_mail; send_mail('test subject', 'test message', 'YOURUSERNAME@gmail.com', ['YOURRECIPIENT@domain.com'])"
