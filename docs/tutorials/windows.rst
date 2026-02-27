.. _windows:

Running on Windows/WSL
----------------------

Tutor is not officially supported on Windows. However, some people have managed to run Tutor on Windows using the Windows Subsystem for Linux (WSL) or even natively on Windows.

If you only want to run an instance of Tutor on Windows, simply running `tutor local launch` should ideally work. This is because `tutor local` does everything in Docker and doesn't interact with the Windows filesystem, which is the root cause of most issues. `tutor` simply launches the Docker containers, and the containers do the rest, which run on Ubuntu's base images.

However, if you want to develop on Open edX via Tutor on Windows, the following are the recommendations:

1. **Use WSL**: Running Tutor or Open edX natively on Windows will cause issues, so avoid it as much as possible. Even Docker itself recommends using WSL. Check out this guide from Docker for best practices regarding WSL: [Docker Desktop WSL 2 Best Practices](https://www.docker.com/blog/docker-desktop-wsl-2-best-practices/).
2. When using WSL, do everything inside WSL (as pointed out by the Docker guide above). This means you should install Docker Desktop on Windows but run all your commands inside WSL. Clone and keep the code inside WSL and add the mount points from inside WSL. If you want to do active development on Open edX, use an editor that supports remote execution and integrates well with WSL (e.g., VSCode).
3. If you really want to keep the code on the Windows filesystem, you can do it, but make sure you still use WSL to build the images. This is because building images directly from Windows can cause issues due to symlinks (which are used in the edX repo). Follow these steps to get it working with WSL:
    1. Clone the edx-platform repo on Windows.
    2. Install Tutor on both Windows and WSL. These installations are separate from each other.
    3. Run `tutor images build openedx-dev` inside WSL (from the above directory, mounted inside WSL).
    4. Run `tutor mounts add <path-to-edx-platform-repo>` on Windows (as mounting the Windows paths to Docker from WSL doesn't work for some reason).
    5. Run `tutor dev launch --skip-build` or after the first time `tutor dev start` from Windows (this will use the images already built in WSL, but the mounts are from Windows).
    6. You can now develop on Windows, and the changes will be reflected in the running instance. Always build the images from WSL, and run `tutor dev <command>` from Windows.

Note: This is an additional guide that might be helpful to people using Windows, but Windows isn't officially supported, and the above steps are not guaranteed to work. The best way to run Tutor is on a Unix-based system.

