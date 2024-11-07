- 💥[Improvement] Rename Tutor's two branches (by @kdmccormick):
  * Rename **master** to **release**, as this branch runs the latest official Open edX release.
  * Rename **nightly** to **next**, as this branch runs the Open edX master branches, which are the basis fort the next Open edX release.
- [Feature] Add the `IS_NEXT` variable to the template context, which is set to True for users running Tutor Next (by @kdmccormick).
- [Bugfix] Use `IS_NEXT` rather than the edx-platform branch name in order to determine which patches to apply. This way, branches that are based off of edx-platform master will use Tutor Next patches rather than Tutor Release patches (by @kdmccormick).
