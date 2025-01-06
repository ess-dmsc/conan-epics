# Functions for GitLab CI
setup_conan() {
    echo 'Setting up Conan...'
    conan remote add "$conan_remote_name" "$conan_remote_url" --force
    conan user --password "$ESS_ARTIFACTORY_ECDC_CONAN_TOKEN" --remote ecdc-conan-external "$ESS_ARTIFACTORY_ECDC_CONAN_USER"
}

create_build_info() {
    echo 'Creating build info...'
    touch BUILD_INFO
    echo "Repository: ${CI_PROJECT_PATH}/${CI_COMMIT_REF_NAME}" >> BUILD_INFO
    echo "Commit: ${CI_COMMIT_SHA}" >> BUILD_INFO
    echo "GitLab build: ${CI_PIPELINE_ID}" >> BUILD_INFO
}
