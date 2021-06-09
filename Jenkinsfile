@Library('ecdc-pipeline')
import ecdcpipeline.ContainerBuildNode
import ecdcpipeline.ConanPackageBuilder
import ecdcpipeline.PipelineBuilder

project = "conan-epics"

conan_user = "ess-dmsc"
conan_pkg_channel = "testing"

containerBuildNodes = [
  'centos': ContainerBuildNode.getDefaultContainerBuildNode('centos7-gcc8'),
  'debian': ContainerBuildNode.getDefaultContainerBuildNode('debian10'),
  'ubuntu': ContainerBuildNode.getDefaultContainerBuildNode('ubuntu1804-gcc8')
]
archivingBuildNodes = [
  'centos-archive': ContainerBuildNode.getDefaultContainerBuildNode('centos7-gcc8')
]

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

node('master') {
  checkout scm

  builders['macOS'] = get_macos_pipeline()
  builders['windows10'] = get_win10_pipeline()

  parallel builders
}

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
      mkdir epics
      cd epics
      conan install ../${pipelineBuilder.project}/archiving/conanfile.txt
      ls -la *
    """
  }  // stage
}

node('master') {
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

def get_win10_pipeline() {
  return {
    node ("windows10") {
      // Use custom location to avoid Win32 path length issues
    ws('c:\\jenkins\\') {
      cleanWs()
      dir("${project}") {
        stage("windows10: Checkout") {
          checkout scm
        }  // stage

        stage("windows10: Package") {
          bat """conan create . ${conan_user}/${conan_pkg_channel} \
            --build=outdated"""
        }  // stage
      }  // dir
      }  // ws
    }  // node
  }  // return
}  // def
