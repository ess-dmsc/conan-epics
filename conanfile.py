import os
import shutil
from conans import ConanFile, AutoToolsBuildEnvironment, tools


EPICS_BASE_VERSION = "3.16.1"
EPICS_BASE_DIR = "base-" + EPICS_BASE_VERSION
# Binaries to include in package
EPICS_BASE_BINS = ("caget", "cainfo", "camonitor", "caput")

EPICS_V4_VERSION = "4.6.0"
EPICS_V4_DIR = "EPICS-CPP-" + EPICS_V4_VERSION
EPICS_V4_SUBDIRS = ("normativeTypesCPP", "pvAccessCPP", "pvCommonCPP",
                    "pvDataCPP", "pvDatabaseCPP", "pvaClientCPP", "pvaSrv")
EPICS_V4_BINS = ("eget", "pvget", "pvinfo", "pvlist", "pvput")


class EpicsbaseConan(ConanFile):
    name = "epics"
    version = "{}-{}".format(EPICS_BASE_VERSION, EPICS_V4_VERSION)
    license = "BSD 2-Clause"
    url = "https://github.com/ess-dmsc/conan-epics-base"
    description = "EPICS Base and V4"
    exports = "files/*"
    settings = "os", "compiler"
    generators = "cmake"

    def source(self):
        self._get_epics_base_src()
        self._get_epics_v4_src()

    def _get_epics_base_src(self):
        tools.download(
            "https://www.aps.anl.gov/epics/download/base/{}.tar.gz".format(EPICS_BASE_DIR),
            "{}.tar.gz".format(EPICS_BASE_DIR)
        )
        tools.check_sha256(
            "{}.tar.gz".format(EPICS_BASE_DIR),
            "fc01ff8505871b9fa7693a4d5585667587105f34ec5e16a207d07b704d1dc5ed"
        )
        tools.unzip("{}.tar.gz".format(EPICS_BASE_DIR))
        os.unlink("{}.tar.gz".format(EPICS_BASE_DIR))

    def _get_epics_v4_src(self):
        tools.download(
            "https://sourceforge.net/projects/epics-pvdata/files/{}/{}.tar.gz/download".format(EPICS_V4_VERSION, EPICS_V4_DIR),
            "{}.tar.gz".format(EPICS_V4_DIR)
        )
        tools.check_sha256(
            "{}.tar.gz".format(EPICS_V4_DIR),
            "fc369a1663b197cce23b47762bf3e1aadc49677e01be5063885160de79df6d9c"
        )
        tools.unzip("{}.tar.gz".format(EPICS_V4_DIR))
        os.unlink("{}.tar.gz".format(EPICS_V4_DIR))

    def build(self):
        # Build EPICS Base
        if tools.os_info.is_linux:
            self._add_linux_config()
        elif tools.os_info.is_macos:
            self._add_darwin_config()

        with tools.chdir(EPICS_BASE_DIR):
            base_build = AutoToolsBuildEnvironment(self)
            base_build.make()

        # Build EPICS V4
        self._edit_epics_v4_makefile()
        os.environ["EPICS_BASE"] = os.path.join(os.getcwd(), EPICS_BASE_DIR)
        with tools.chdir(EPICS_V4_DIR):
            v4_build = AutoToolsBuildEnvironment(self)
            v4_build.make()

    def _add_linux_config(self):
        shutil.copyfile(
            os.path.join(self.conanfile_directory, "files", "CONFIG_SITE.local.linux"),
            os.path.join(EPICS_BASE_DIR, "configure", "CONFIG_SITE.local")
        )
        tools.replace_in_file(
            os.path.join(EPICS_BASE_DIR, "configure", "os", "CONFIG_SITE.Common.linux-x86_64"),
            "COMMANDLINE_LIBRARY = READLINE",
            "COMMANDLINE_LIBRARY = EPICS"
        )

    def _add_darwin_config(self):
        shutil.copyfile(
            os.path.join(self.conanfile_directory, "files", "CONFIG_SITE.local.darwin"),
            os.path.join(EPICS_BASE_DIR, "configure", "CONFIG_SITE.local")
        )
        os.remove(os.path.join(EPICS_BASE_DIR, "configure", "os", "CONFIG_SITE.darwinCommon.darwinCommon"))
        shutil.copyfile(
            os.path.join(self.conanfile_directory, "files", "CONFIG_SITE.darwinCommon.darwinCommon"),
            os.path.join(EPICS_BASE_DIR, "configure", "os", "CONFIG_SITE.darwinCommon.darwinCommon")
        )

    def _edit_epics_v4_makefile(self):
        tools.replace_in_file(
            os.path.join(EPICS_V4_DIR, "Makefile"),
            "MODULES += exampleCPP",
            "#MODULES += exampleCPP"
        )

    def package(self):
        if tools.os_info.is_linux:
            arch = "linux-x86_64"
        elif tools.os_info.is_macos:
            arch = "darwin-x86"

        # Package EPICS Base
        base_bin_dir = os.path.join(EPICS_BASE_DIR, "bin", arch)
        for b in EPICS_BASE_BINS:
            self.copy(b, dst="bin", src=base_bin_dir)
        self.copy("*", dst="include", src=os.path.join(EPICS_BASE_DIR, "include"),
                  excludes="valgrind/*", keep_path=False)
        self.copy("*", dst="lib", src=os.path.join(EPICS_BASE_DIR, "lib", arch))
        self.copy("pkgconfig/*", dst="lib", src=os.path.join(EPICS_BASE_DIR, "lib"))

        # Package EPICS V4
        for d in EPICS_V4_SUBDIRS:
            self.copy("*", dst="include", src=os.path.join(EPICS_V4_DIR, d, "include"))
            self.copy("*", dst="lib", src=os.path.join(EPICS_V4_DIR, d, "lib", arch))
        v4_bin_dir = os.path.join(EPICS_V4_DIR, "pvAccessCPP", "bin", arch)
        for b in EPICS_V4_BINS:
            self.copy(b, dst="bin", src=v4_bin_dir)

    def package_info(self):
        self.cpp_info.libs = [
            "Com",
            "ca",
            "cas",
            "dbCore",
            "dbRecStd",
            "gdd",
            "nt",
            "pvAccess",
            "pvaClient",
            "pvaSrv",
            "pvMB",
            "pvDatabase",
            "pvData"
        ]
