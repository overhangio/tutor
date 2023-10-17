- 💥[Feature] The `openedx-assets` command is replaced with `npm run` subcommands.
  This will slightly reduce the build time for edx-platform assets and comprehensive themes.
  It will also open up the door for more significant build time reductions in the future.
  Here is a migration guide, where each command is to be run in the `lms` or `cms` container.

  **Before**                               | **After**                                                                           
  -----------------------------------------|-------------------------------------------------------------------------------------
  `openedx-assets build --env=prod ARGS`   | `npm run build -- ARGS`                                                             
  `openedx-assets build --env=dev ARGS`    | `npm run build-dev -- ARGS`                                                         
  `openedx-assets common --env=prod ARGS`  | `npm run compile-sass -- --skip-themes ARGS`                                    
  `openedx-assets common --env=dev ARGS`   | `npm run compile-sass-dev -- --skip-themes ARGS`                                    
  `openedx-assets webpack --env=prod ARGS` | `npm run webpack -- ARGS`                                                           
  `openedx-assets webpack --env=dev ARGS`  | `npm run webpack-dev -- ARGS`                                                       
  `openedx-assets npm`                     | `npm run postinstall` (`npm clean-install` runs this automatically)                 
  `openedx-assets xmodule`                 | (no longer necessary)                                                               
  `openedx-assets collect ARGS`            | `./manage.py lms collectstatic --noinput ARGS && ./manage.py cms collectstatic ARGS` 
  `openedx-assets watch-themes ARGS`       | `npm run watch-themes -- ARGS`                                                      

  For more details, see the [deprecation notice for paver](https://github.com/openedx/edx-platform/issues/34467)
  and the [static assets reference](https://github.com/openedx/edx-platform/tree/open-release/redwood.master/docs/references/static-assets.rst)
  in edx-platform.
