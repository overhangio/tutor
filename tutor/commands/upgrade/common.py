from tutor import fmt
from tutor import plugins
from tutor.types import Config


def upgrade_from_lilac(config: Config) -> None:
    if not plugins.is_installed("forum"):
        fmt.echo_alert(
            "The Open edX forum feature was moved to a separate plugin in Maple. To keep using this feature, "
            "you must install and enable the tutor-forum plugin: https://github.com/overhangio/tutor-forum"
        )
    elif not plugins.is_enabled(config, "forum"):
        fmt.echo_info(
            "The Open edX forum feature was moved to a separate plugin in Maple. To keep using this feature, "
            "we will now enable the 'forum' plugin. If you do not want to use this feature, you should disable the "
            "plugin with: `tutor plugins disable forum`."
        )
        plugins.enable(config, "forum")

    if not plugins.is_installed("mfe"):
        fmt.echo_alert(
            "In Maple the legacy courseware is no longer supported. You need to install and enable the 'mfe' plugin "
            "to make use of the new learning microfrontend: https://github.com/overhangio/tutor-mfe"
        )
    elif not plugins.is_enabled(config, "mfe"):
        fmt.echo_info(
            "In Maple the legacy courseware is no longer supported. To start using the new learning microfrontend, "
            "we will now enable the 'mfe' plugin. If you do not want to use this feature, you should disable the "
            "plugin with: `tutor plugins disable mfe`."
        )
        plugins.enable(config, "mfe")
