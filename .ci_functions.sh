# Functions for GitLab CI
setup_conan() {
    echo 'Setting up Conan...'
    conan remote add "$conan_remote_name" "$conan_remote_url" --force
    conan user --password "$ESS_ARTIFACTORY_ECDC_CONAN_TOKEN" --remote ecdc-conan-external "$ESS_ARTIFACTORY_ECDC_CONAN_USER"
}

upload_packages_if_target_container() {
  local current_container=$1
  local target_container=$2
  local conan_user=$3
  local conan_pkg_channel=$4
  local conan_file_path=$5

  if [[ "$current_container" == "$target_container" ]]; then
    packageNameAndVersion=$(conan inspect --attribute name --attribute "$conan_file_path" | awk -F': ' '{print $2}' | paste -sd'/')
    conan upload --all --no-overwrite --remote ecdc-conan-external ${packageNameAndVersion}@${conan_user}/${conan_pkg_channel}
  fi
}

create_build_info() {
    echo 'Creating build info...'
    touch BUILD_INFO
    echo "Repository: ${CI_PROJECT_PATH}/${CI_COMMIT_REF_NAME}" >> BUILD_INFO
    echo "Commit: ${CI_COMMIT_SHA}" >> BUILD_INFO
    echo "GitLab build: ${CI_PIPELINE_ID}" >> BUILD_INFO
}
