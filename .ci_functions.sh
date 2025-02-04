# Functions for GitLab CI

# Sets up Conan by adding a remote path and authenticating the user
setup_conan() {
    local conan_name=$1
    local conan_url=$2

    echo 'Setting up Conan...'
    conan remote add "$conan_name" "$conan_url" --force
    conan user --password "$ESS_ARTIFACTORY_ECDC_CONAN_TOKEN" --remote "$conan_name" "$ESS_ARTIFACTORY_ECDC_CONAN_USER"
}

# Creates a Conan package from the specified path
conan_package_creation() {
    local conan_path=$1
    local conan_options=${2:-""}

    echo 'Creating Conan package...'
    conan create $conan_path ${CONAN_USER}/${CONAN_PKG_CHANNEL} --build=outdated --options $conan_options
}

# Installs Conan dependencies from the specified path
conan_installation() {
    local conan_path=$1

    echo 'Conan installation...'
    conan install $conan_path --build=missing
}

# Uploads packages to the external Conan repository
upload_packages_to_conan_external() {
  local conan_file_path=$1

  echo 'Uploading packages to Conan External Artifactory...'
  packageNameAndVersion=$(conan inspect --attribute name --attribute version $conan_file_path | awk -F': ' '{print $2}' | paste -sd'/')
  conan upload --all --no-overwrite --remote ecdc-conan-external ${packageNameAndVersion}@${CONAN_USER}/${CONAN_PKG_CHANNEL}
}

# Uploads packages to the release Conan repository
upload_packages_to_conan_release() {
  local conan_file_path=$1

  echo 'Uploading packages to Conan Release Artifactory...'
  packageNameAndVersion=$(conan inspect --attribute name --attribute version $conan_file_path | awk -F': ' '{print $2}' | paste -sd'/')
  conan upload --no-overwrite --remote ecdc-conan-release ${packageNameAndVersion}@${CONAN_USER}/${CONAN_PKG_CHANNEL}
}

# Creates a build info file with repository, commit, and pipeline details
create_build_info() {
    echo 'Creating build info...'
    touch BUILD_INFO
    echo "Repository: ${CI_PROJECT_PATH}/${CI_COMMIT_REF_NAME}" >> BUILD_INFO
    echo "Commit: ${CI_COMMIT_SHA}" >> BUILD_INFO
    echo "GitLab build: ${CI_PIPELINE_ID}" >> BUILD_INFO
}
