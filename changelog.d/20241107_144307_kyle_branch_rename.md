- 💥[Improvement] Rename Tutor's two branches (by @kdmccormick):
  * Rename **master** to **release**, as this branch runs the latest official Open edX release.
  * Rename **nightly** to **main**, as this branch runs the Open edX master (a.k.a. main) branches, which are the basis fort the next Open edX release.
  * Tutor Nightly users who do not set a TUTOR_ROOT must rename their project root folder from tutor-nightly to tutor-main in order to continue using their local data in Tutor Main.
  * Tutor Nightly users who do not set a TUTOR_PLUGINS_ROOT must rename their project root folder from tutor-nightly-plugins to tutor-main-plugins in order to continue using their local Nightly plugins in Tutor Main.
