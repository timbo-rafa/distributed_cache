pipeline {
  agent {
    docker { image 'timborafa/couchbase-python-sdk:2' }
  }
  stages {
    stage('Test') {
      steps {
        sh 'python --version'
      }
    }
  }
}
