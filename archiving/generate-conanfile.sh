#!/bin/sh

# Generate a conanfile for archiving artifacts
#   Usage: generate-conanfile.sh <pkg_user> <pkg_channel>

pkg_user="$1"
pkg_channel="$2"

pkg_name=$(conan inspect .. --format text | grep '^name:' | awk '{print $2}')
pkg_version=$(conan inspect .. --format text | grep '^version:' | awk '{print $2}')

cat > conanfile.txt <<EOF
[requires]
${pkg_name}/${pkg_version}@${pkg_user}/${pkg_channel}

[imports]
bin, * -> ./bin
., LICENSE* -> ./licenses @ folder=True, ignore_case=True
EOF
