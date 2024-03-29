@Library('ecdc-pipeline')
import ecdcpipeline.ContainerBuildNode
import ecdcpipeline.ConanPackageBuilder
import ecdcpipeline.PipelineBuilder

project = "conan-epics"
conan_user = "ess-dmsc"
conan_pkg_channel = "stable"

def num_artifacts_to_keep
if (env.BRANCH_NAME == 'master') {
  num_artifacts_to_keep = '3'
} else {
  num_artifacts_to_keep = '1'
}

// Set number of old builds to keep.
properties([[
  $class: 'BuildDiscarderProperty',
  strategy: [
    $class: 'LogRotator',
    artifactDaysToKeepStr: '',
    artifactNumToKeepStr: num_artifacts_to_keep,
    daysToKeepStr: '',
    numToKeepStr: num_artifacts_to_keep
  ]
]]);

containerBuildNodes = [
  'centos': ContainerBuildNode.getDefaultContainerBuildNode('centos7-gcc11'),
  'debian': ContainerBuildNode.getDefaultContainerBuildNode('debian11'),
  'ubuntu': ContainerBuildNode.getDefaultContainerBuildNode('ubuntu2204')
]
archivingBuildNodes = [
  'centos-archive': ContainerBuildNode.getDefaultContainerBuildNode('centos7-gcc11')
]

// Main packaging pipeline
packageBuilder = new ConanPackageBuilder(this, containerBuildNodes, conan_pkg_channel)
packageBuilder.defineRemoteUploadNode('centos')
builders = packageBuilder.createPackageBuilders { container ->
  packageBuilder.addConfiguration(container)

  packageBuilder.addConfiguration(container, [
    'options': [
      'epics:shared': 'False'
    ]
  ])
}

// Archiving pipeline
pipelineBuilder = new PipelineBuilder(this, archivingBuildNodes)
archivingBuilders = pipelineBuilder.createBuilders { container ->
  pipelineBuilder.stage("${container.key}: Checkout") {
    dir(pipelineBuilder.project) {
      scmVars = checkout scm
    }
    container.copyTo(pipelineBuilder.project, pipelineBuilder.project)
  }  // stage

  pipelineBuilder.stage("${container.key}: Install") {
    container.sh """
      cd ${pipelineBuilder.project}/archiving
      ./generate-conanfile.sh ${conan_user} ${conan_pkg_channel}

      mkdir epics
      cd epics
      conan install ..
    """
  }  // stage

  pipelineBuilder.stage("${container.key}: Archive") {
    container.sh """
      # Create file with build information
      cd ${pipelineBuilder.project}/archiving/epics
      touch BUILD_INFO
      echo 'Repository: ${pipelineBuilder.project}/${env.BRANCH_NAME}' >> BUILD_INFO
      echo 'Commit: ${scmVars.GIT_COMMIT}' >> BUILD_INFO
      echo 'Jenkins build: ${env.BUILD_NUMBER}' >> BUILD_INFO

      # Remove additional files generated by Conan
      rm conan*
      rm graph_info.json

      cd ..
      tar czvf epics.tar.gz epics
    """
    container.copyFrom("${pipelineBuilder.project}/archiving/epics.tar.gz", ".")
    archiveArtifacts "epics.tar.gz"
  }  // stage
}


node('master') {
  checkout scm

  if (env.ENABLE_MACOS_BUILDS.toUpperCase() == 'TRUE') {
    builders['macOS'] = get_macos_pipeline()
  }

  parallel builders
  parallel archivingBuilders

  // Delete workspace when build is done.
  cleanWs()
}

def get_macos_pipeline() {
  return {
    node('macos') {
      cleanWs()
      dir("${project}") {
        stage("macOS: Checkout") {
          checkout scm
        }  // stage

        stage("macOS: Package") {
          sh "conan create . ${conan_user}/${conan_pkg_channel} \
            --build=outdated"
        }  // stage
      }  // dir
    }  // node
  }  // return
}  // def
