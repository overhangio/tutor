{% include "build/openedx/settings/partials/assets.py" %}

WEBPACK_LOADER['DEFAULT']['STATS_FILE'] = path(STATIC_ROOT) / "webpack-stats.json"

derive_settings(__name__)
