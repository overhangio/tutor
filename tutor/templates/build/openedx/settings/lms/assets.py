{% include "build/openedx/settings/partials/assets.py" %}

STATIC_ROOT = path(STATIC_ROOT_BASE)
WEBPACK_LOADER['DEFAULT']['STATS_FILE'] = STATIC_ROOT / "webpack-stats.json"

derive_settings(__name__)

LOCALE_PATHS.append("/openedx/locale/contrib/locale")
LOCALE_PATHS.append("/openedx/locale/user/locale")
