pipeline {
    agent {label "agent_docker"}
    tools {nodejs "NODEJS"}
    stages {
        stage('Build') {
            steps {
                sh 'npm install yarn -g'
                sh 'yarn install'
                sh 'yarn build'
            }
        }
    }
}