## ABN Technical assesment solution implementation

## First impressions

When running the API's I've experienced an incompatibility between pytorch cpu only libraris with Apple M3 processor.

I've checked the official documentation and I could not find the specific **torch**+cpu ([PyTorch](https://pytorch.org)) packages for ARM architecture. Then I've used a **GPU** package with the same version to run the API's locally. I've tested in and64 VM and the +CPU packages are running fine. I will continue the solution using the GPU packages.

When installing the +cpu package it could not be found on the public index, then I've used the Pytorch repository to download the specific versions(https://download.pytorch.org/whl/cpu).

To run the backend API I've added two new files to be easier to manage multiple indexes dependencies, as it's not recommended to add the "--extra-index-urls" to prevent malicious code from packages on public source with the same name and version of packages on private soruce, I've spllited thre requirements in two files, and the script will help to manage the installation:

- build.sh - Install dependencies from multiple sources.

- run.sh - Install dependencies and start the API.

To run locally I've used Python3.10 due some dependencies limitations.

## New Backend API

### EXTERNAL_INTEGRATION_KEY

I've changed a small typo on the EXTERNAL_INTEGRATION_KEY - It was EXTERNAL_INTGERATION_KEY before.

I've added a new dependency **gunicorn==22.0.0** that is WSGI server to run the Flask API.

To run the backend_api using python3.10:

- Create a python virtual environment - only 1 time needed
```bash
python3.10 -m venv venv
```

- Activate the environment and configure
```bash
source venv/bin/activate
chmod +x ./build.sh
chmod +x ./run.sh
export EXTERNAL_INTEGRATION_KEY=MY_INTEGRATION_KEY
```

- Run the Application
```bash
./run.sh
```

### Dockerizing the Api's

#### Backend API

I've created a new docker file with two stages, the first one to build and prepare the dependencies and then the second stage to get the dependencies and run the application, to remove possible unnecessary build artifacts. 

```bash
cd backend-api
docker buildx build -t backend-api:latest . 
```


I've found small issues due requirements.txt provided for this application:

- PyTorch packages are not compatible with alpine linux  - Honestly speaking I did not went trough this issue deeper to check if there is any way to use alpine images and install those dependencies.
- Pytorch docker images are too big( +3GB)
- python-slim images uses debian, even the small image after installing pytorch the size stills 1.05GB.


###### Vulnerabilities 

After running a small vulnerability check on the generated docker image I could see some vulnerabilities:

```
30 vulnerabilities found in 15 packages
  UNSPECIFIED  3   
  LOW          4   
  MEDIUM       14  
  HIGH         9   
  CRITICAL     0
```

 I've update some dependencies making sure the applications stills running and improved the overall score.

```
6 vulnerabilities found in 2 packages
  LOW       4  
  MEDIUM    2  
  HIGH      0  
  CRITICAL  0 
```

Stills there some work to remediate Medium and Low vulnerabilites, but I would like to add this step as it's a important check when containerizing applications.

To build and check the vunerabilities I've used docker locally. There is some tools like [trivy](https://trivy.dev) that has more scan capabilities.


To get an overview of the vulnerabilites: 

``` bash
docker scout quickview --only-fixed
```

To get the analisys: 

``` bash
docker scout cves local://backend-api:latest 
```

After remediating and building the image I could see the size is too big, inpecting the installation most of the size is coming from the Pytorch packages, I did not removed them but they are not being used by the appications.

I would recommend to revisit the list of requirements for the application to reduce the dependencies and reduce the image size as well.


### Data API

Implemented the same changes regarding requirements and using gunicorn as backend-api. 

Changed the log folders path to: /var/data/logs - it will help when running in containers, I can added a volume to save the logs.

To run the Data Api the same **build.sh** and **run.sh** are available:

- Create a python virtual environment - only 1 time needed
```bash
python3.10 -m venv venv
```

- Activate the environment and configure
```bash
source venv/bin/activate
chmod +x ./build.sh
chmod +x ./run.sh
```

- Run the Application
```bash
./run.sh
```


Similiar vulnerabilities and the size issues are present on the data-api docker image as they are on backend-api.


Before updating dependencies:
```
27 vulnerabilities found in 13 packages
  UNSPECIFIED  2   
  LOW          4   
  MEDIUM       13  
  HIGH         8   
  CRITICAL     0
```

After updating dependencies:

```
10 vulnerabilities found in 5 packages
  LOW       4  
  MEDIUM    6  
  HIGH      0  
  CRITICAL  0 
```



## Deploying to Kubernetes

After containerize the applications I've created 3 helm charts:

 - abn-stack - Combination of data-api and backend-api helm charts.
 - backend-api 
 - data-api

 On **backend-api** helm chart there is only one mandatory configuration: **integrationKeySecretName**. As the **EXTERNAL_INTEGRATION_KEY** is mandatory to authenticate the external API, each environment must have a secret. Using a secret reference is a simple and secure way to store and use sensitive data. 

 For both API's I've implemented a dummy healthz and readyz endpoing to provide information to the liveness and readiness probes. 

 The final abn-stack value.yaml file for development environment:

 ``` yaml
 backendapi:
    integrationKeySecretName: "backend-api-integration-key"
    service:
        type: ClusterIP
        port: 80        
    livenessProbe:
        httpGet:
            path: /healthz
            port: 5000
    readinessProbe:        
        httpGet:
            path: /readyz
            port: 5000
            initialDelaySeconds: 5
dataapi:
    # Mount point to /var/data/logs
    persistence:
        enabled: true
        size: 1Gi
        storageClass: standard
    service:
        type: ClusterIP
        port: 80
        targetPort: 5000
    livenessProbe:
        httpGet:
            path: /healthz
            port: 5000
    readinessProbe:
        httpGet:
            path: /readyz
            port: 5000
 ```

 For the chart creation I've used the *helm create* command, it provides a complete chart template, then changed only small necessary configuration for each application, like adding the secret reference requirement for backend-api and the volume mounts for data-api.

 The abn-stack chart has the reference for data and backend api's:

 ```yaml
 apiVersion: v2
name: abn-stack
description: A Helm chart for the ABN technical assesment
type: application
version: 0.1.0
appVersion: "1.16.0"

dependencies:
  - name: backendapi
    version: "1.0.0"
    repository: "file://../backend-api"
  - name: dataapi
    version: "1.0.0"
    repository: "file://../data-api"
 ```


 When using this repository is important to build the abn-stack repository, as it's referencing the charts in the same repository, to guarantee that all the dependencies are up to date, go to the /deployment/helm/abn-stack folder and run:

 ```bash
 helm dependencies build
```

My local result: 
``` bash
 Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "awx-operator" chart repository
...Successfully got an update from the "jetstack" chart repository
...Successfully got an update from the "clickhouse-operator" chart repository
...Successfully got an update from the "prometheus-community" chart repository
Update Complete. ⎈Happy Helming!⎈
Saving 2 charts
Deleting outdated charts
 ```

 after the dependencies build a Chart.lock file is created:

 ``` yaml
 dependencies:
- name: backendapi
  repository: file://../backend-api
  version: 1.0.0
- name: dataapi
  repository: file://../data-api
  version: 1.0.0
digest: sha256:5fee329e7655031bde384d83ad458954848fd39dea9ee0d7366271ec5508f7c7
generated: "2024-06-30T14:24:52.173332+02:00"
 ```


 Before installing the release one step is needed: Create a new secret to store the EXTERNAL_INTEGRATION_KEY : 

``` yaml
apiVersion: v1
kind: Secret
metadata:
  name: backend-api-integration-key
type: Opaque
data:
  integrationKey: <<MY SECRET VALUE>> 
```

``` bash
kubectl apply -f secret.yaml -n dev
```
PS: I'm using a dev namespace to install this environment, if the namespace doesn't exists, create one:

```
kubectl create namespace dev
```

To install the release:

``` bash

helm install abn-stack-dev ./deployment/helm/abn-stack -e ./deployment/configuration/dev/values.yaml
```


## Deploying using Ansible

I've created a new playbook and variable files to support the ansible deployment.

The playbook is:

```yaml
---
- name: Deploy Helm Chart
  hosts: localhost
  
  tasks:    
    - name: Include common variables
      include_vars:
        file: ../vars/common.yaml

    - name: Include environment-specific variables
      include_vars:
        file: "../vars/{{ app_env | default('dev') }}.yaml"

    - name: Ensure helm is installed
      ansible.builtin.command:
        cmd: helm version
      register: helm_version
      failed_when: "'Version' not in helm_version.stdout"

    - name: Make sure the namespace is present in k8s cluster
      k8s:
        name: "{{ k8s_namespace }}"
        kubeconfig: "{{ kubeconfig_path }}"
        api_version: v1
        kind: Namespace
        state: present

    - name: Deploy the Helm chart
      command: >
        helm upgrade --install
        abn-app-{{ helm_release_suffix }}
        {{ abn_app_chart }}
        --namespace {{ k8s_namespace }}
        --create-namespace
        --values {{ valueFilesPath }}
      environment:
        KUBECONFIG: "{{ kubeconfig_path }}"
      register: helm_result

    - name: Display Installation Helm result
      ansible.builtin.debug:
        var: helm_result

```



The common.yaml file:

```yaml
abn_app_chart: absolutepath/abn-app
helm_version: 3.14.0
helm_release_suffix: "{{ environment_name }}"
k8s_namespace: "{{ environment_name }}"
```

I'm using the environment name as suffix for the release and aldo as namespace on k8s cluster. The abn_app_chart is looking to an absolute path. In the ideal scenario it could point direcly to a git repository or a private helm repository for the team that is using this chart.


The dev.yaml file:

```yaml
environment_name: dev 
kubeconfig_path: "/Users/myuser/.kube/config"
valueFilesPath: "../../configuration/dev.yaml"
k8s_context: minikube
```

The environment name is set here, the values.yaml relative path and also the kubeconfig relative path. This value about kubernetes authentication should be stored in a secure location, like a remote vault for non development environments. In case of a remote vault the kubernetes authentication strategy could be changed.


To deploy the helm chart using ansible run the command:

```
ansible-playbook ./deployment/ansible/playbooks/app-deploy.yaml -e app_env=dev
```

the app_env will point the playbook to the dev/prod variable files. 