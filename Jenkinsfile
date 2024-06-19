pipeline {
    agent {label "agent-1"}
    tools {nodejs "NODEJS"}
    stages {
        stage('Build') {
            steps {
                sh 'npm install yarn -g'
                sh 'yarn install'
                sh 'yarn build'
            }
        }

        stage("Zip") {
            steps {
                sh 'zip -r build.zip build'
            }
        }
    }
}
