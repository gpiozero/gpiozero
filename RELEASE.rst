=================
Release Procedure
=================

On your build Pi, perform the following steps:

1. Ensure you have a reliable Internet connection (preferably Ethernet).

2. Ensure you have the following Debian packages installed: ``devscripts, dput,
   python-all, python3-all, gnupg, build-essential, git, python-setuptools,
   python3-setuptools, python-rpi.gpio, python3-rpi.gpio``

3. Ensure you have a valid ``~/.pypirc`` configuration. For example::

       [distutils]
       index-servers =
           pypi

       [pypi]
       username:my_username
       password:my_long_password

4. Ensure you have a valid ``~/.dput.cf`` setup which includes the
   ``[raspberrypi]`` target. For example::

       [raspberrypi]
       fqdn = build-master.raspberrypi.org
       incoming = incoming
       login = incoming
       method = scp

5. Ensure you have a valid public/private key-pair defined for GNUPG.

6. In the root ``gpiozero`` directory, run ``make release``. This will launch
   ``dch`` to update the Debian changelog. Fill this out properly (ticket
   references!) and the release will be generated, tagged, signed, and
   registered with GitHub and PyPI.

   .. note::

       Although the release has been registered at this point, no packages
       have been generated or uploaded to any service.

7. Still in the root ``gpiozero`` directory, run ``make upload``. This will
   generate the actual debian packages, upload them to Raspbian, and upload
   the source package to PyPI.

8. On GitHub, close any milestone associated with the release.

9. On ReadTheDocs, update the project configuration to build the new release,
   then set it to the default version for the project.
