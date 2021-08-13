# conan-epics

Conan package for EPICS Base  and V4 (http://www.aps.anl.gov/epics/). Developed
and tested for linux-x86_64 (CentOS 7) and darwin-x86 (macOS). This package
contains a limited subset of the EPICS tools.

The test package requires readline on Linux. You can install it by running

```
sudo yum install readline-devel  # CentOS
sudo apt install libreadline-dev  # Debian
```

## For Windows

In EPICS base the file win32.bat is used for configuring the build system on Windows. In EPICS base it is found in base-3.1X.X.X\startup

The win32.bat file in this repository is intended to be a drop-in replacement to allow EPICS to be built on the DMSC's Jenkins system.

It requires the following items to be installed:

    GNU Make for Windows (version 4.2 or higher)
    Strawberry Perl (64-bit) (http://strawberryperl.com/)
    Visual Studio 2015 or 2017

And it expects make and perl to be in the path.

## Updating the conan package

Follow these instructions:

1. Edit line 6 of the *conanfile.py*-file to the version of EPICS base that you want to package.

2. Edit line 14 of the *conanfile.py*-file to set the version of the new conan package.

3. Edit line 40 of the *conanfile.py*-file to set the hash of the compressed file. The hash can be determined from running the command `shasum -a 256 base-x.y.z.tar.gz`.

4. When in the directory of the local copy of *conan-epics*, execute this command:

	```
	conan create . ess-dmsc/stable
	```
    *Note:* If the build stage fails, you might have to update to a more recent version of Perl.

5. Upload the new package to the relevant conan package repository by executing:

	```
	conan upload epics/x.y.z-dm1@ess-dmsc/stable --remote alias_of_repository
	```

	Where **x.y.z-dm1** is the version of the conan package as mentioned above and **alias\_of\_repository** is exactly what it says. You can list all the repositories that your local conan installation is aware of by running: `conan remote list`.

## Limitations

The `shared` option is only available on Linux.
