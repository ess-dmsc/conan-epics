import os
import shutil
from conans import ConanFile, AutoToolsBuildEnvironment, tools


EPICS_BASE_VERSION = "7.0.6"
EPICS_BASE_DIR = "base-" + EPICS_BASE_VERSION
# Binaries to include in package
EPICS_BASE_BINS = ("caRepeater", "caget", "cainfo", "camonitor", "caput", "pvget", "pvinfo", "pvlist", "pvput")


class EpicsbaseConan(ConanFile):
    name = "epics"
    version = "7.0.6"
    license = "EPICS Open license"
    url = "https://github.com/ess-dmsc/conan-epics-base"
    description = "EPICS Base version 7"
    exports = ["files/*", "FindEPICS.cmake"]
    settings = "os", "compiler"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"
    # For Windows use short paths (ignored for other OS's)
    short_paths=True

    def configure(self):
        if not tools.os_info.is_linux:
            self.output.warn('Removing "shared" option (only available on Linux)')
            self.options.remove("shared")

    def source(self):
        self._get_epics_base_src()

    def _get_epics_base_src(self):
        tools.download(
            f"https://epics-controls.org/download/base/{EPICS_BASE_DIR}.tar.gz",
            f"{EPICS_BASE_DIR}.tar.gz"
        )
        tools.check_sha256(
            f"{EPICS_BASE_DIR}.tar.gz",
            "bc1d9edd0624542870424b90baafebe16af17a317b01aec577757e96830deee0"
        )
        tools.unzip(f"{EPICS_BASE_DIR}.tar.gz")
        os.unlink(f"{EPICS_BASE_DIR}.tar.gz")

    def build(self):
        # Build EPICS Base
        if tools.os_info.is_linux:
            self._add_linux_config()
        elif tools.os_info.is_macos:
            self._add_darwin_config()
        elif tools.os_info.is_windows:
            self._add_windows_config()

        with tools.chdir(EPICS_BASE_DIR):
            if tools.os_info.is_windows:
                self.run("build_win32.bat")
            else:
                base_build = AutoToolsBuildEnvironment(self)
                base_build.make()

        os.rename(os.path.join(EPICS_BASE_DIR, "LICENSE"), "LICENSE.EPICSBase")

    def _using_devtoolset(self):
        gcc_path = tools.which("gcc")
        if gcc_path is not None:
            return 'devtoolset' in gcc_path
        else:
            return False

    def _add_darwin_config(self):
        shutil.copyfile(
            os.path.join(self.source_folder, "files", "CONFIG_SITE.local.darwin"),
            os.path.join(EPICS_BASE_DIR, "configure", "CONFIG_SITE.local")
        )
        os.remove(os.path.join(EPICS_BASE_DIR, "configure", "os", "CONFIG_SITE.darwinCommon.darwinCommon"))
        shutil.copyfile(
            os.path.join(self.source_folder, "files", "CONFIG_SITE.darwinCommon.darwinCommon"),
            os.path.join(EPICS_BASE_DIR, "configure", "os", "CONFIG_SITE.darwinCommon.darwinCommon")
        )

    def _add_windows_config(self):
        shutil.copyfile(
            os.path.join(self.source_folder, "files", "CONFIG_SITE.local.win32"),
            os.path.join(EPICS_BASE_DIR, "configure", "CONFIG_SITE.local")
        )

        shutil.copyfile(
            os.path.join(self.source_folder, "files", "win32.bat"),
            os.path.join(EPICS_BASE_DIR, "../", "win32.bat")
        )

        shutil.copyfile(
            os.path.join(self.source_folder, "files", "build_win32.bat"),
            os.path.join(EPICS_BASE_DIR, "build_win32.bat")
        )
    
    def _add_linux_config(self):
        if self.settings.compiler == "gcc" and self._using_devtoolset():
            self._set_path_to_devtoolset_gnu()
            # Disable readline, as not all our build node images have it.
            tools.replace_in_file(
                os.path.join(EPICS_BASE_DIR, "configure", "os", "CONFIG_SITE.Common.linux-x86_64"),
                "#COMMANDLINE_LIBRARY = EPICS",
                "COMMANDLINE_LIBRARY = EPICS"
            )
        if not self.options.shared:
            tools.replace_in_file(
                os.path.join(EPICS_BASE_DIR, "configure", "CONFIG_SITE"),
                "SHARED_LIBRARIES=YES",
                "SHARED_LIBRARIES=NO"
            )
            tools.replace_in_file(
                os.path.join(EPICS_BASE_DIR, "configure", "CONFIG_SITE"),
                "STATIC_BUILD=NO",
                "STATIC_BUILD=YES"
            )

    def _using_devtoolset(self):
        gcc_path = tools.which("gcc")
        if gcc_path is not None:
            return 'devtoolset' in gcc_path
        else:
            return False

    def _set_path_to_devtoolset_gnu(self):
        gcc_path = tools.which("gcc")
        path_to_gnu_bin = os.path.split(gcc_path)[0]
        path_to_gnu = os.path.split(path_to_gnu_bin)[0]
        tools.replace_in_file(
            os.path.join(EPICS_BASE_DIR, "configure", "CONFIG.gnuCommon"),
            "GNU_BIN = $(GNU_DIR)/bin",
            f"GNU_BIN = {path_to_gnu}/bin"
        )
        tools.replace_in_file(
            os.path.join(EPICS_BASE_DIR, "configure", "CONFIG.gnuCommon"),
            "GNU_LIB = $(GNU_DIR)/lib",
            f"GNU_LIB = {path_to_gnu}/lib"
        )

    def package(self):
        if tools.os_info.is_linux:
            arch = "linux-x86_64"
        elif tools.os_info.is_macos:
            arch = "darwin-x86"
        elif tools.os_info.is_windows:
            arch = "windows-x64"

        # Package EPICS Base
        base_bin_dir = os.path.join(EPICS_BASE_DIR, "bin", arch)
        for b in EPICS_BASE_BINS:
            self.copy(b, dst="bin", src=base_bin_dir)
        self.copy("*.dll", dst="bin", src=base_bin_dir)
        self.copy("*", dst="include", src=os.path.join(EPICS_BASE_DIR, "include"),
                  excludes="valgrind/*", keep_path=True)
        self.copy("*", dst="lib", src=os.path.join(EPICS_BASE_DIR, "lib", arch))
        self.copy("pkgconfig/*", dst="lib", src=os.path.join(EPICS_BASE_DIR, "lib"))

        self.copy("LICENSE.*")
        
        self.copy("FindEPICS.cmake", ".", ".")

    def package_info(self):
        self.cpp_info.libs = [
            "Com",
            "ca",
            "dbCore",
            "dbRecStd",
            "nt",
            "pvAccess",
            "pvAccessCA",
            "pvAccessIOC",
            "pvData",
            "pvDatabase",
            "pvaClient",
            "qsrv",
        ]
