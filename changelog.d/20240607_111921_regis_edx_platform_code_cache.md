- 💥[Improvement] Ensure that the edx-platform repository git checkout is cached by Docker during image build. This means that the cache will automatically be cleared any time there is an upstream change. Thus, it is no longer necessary to run `tutor images build --no-cache` just to fetch the latest edx-platform changes. For this to work, any GitHub repository referenced by `EDX_PLATFORM_REPOSITORY` needs to end with ".git". Make sure that this is the case if you have modified the value of this setting in the past. (by @regisb)