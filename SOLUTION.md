## ABN Technical assesment solution implementation

## First impressions

During the initial API run, I encountered an incompatibility issue between PyTorch +CPU libraries and the Apple M3 processor. Upon consulting the official documentation, I discovered that there were no specific Torch+CPU packages available for the ARM architecture. Therefore, I opted to use GPU packages of the same version for local API testing. Subsequently, I confirmed that the +CPU packages function correctly on an x86_64 VM. Henceforth, I will proceed with the solution using the GPU packages.

When attempting to install the +CPU package from the public index, it was not available. As an alternative, I downloaded the specific versions directly from the PyTorch repository (https://download.pytorch.org/whl/cpu).

To facilitate the installation of backend APIs, I introduced two new files for managing multiple index dependencies. It's advisable not to use "--extra-index-urls" to avoid potential risks of including malicious code from public sources with identical package names and versions as those from private sources. Consequently, I divided the requirements into two files. Below are the scripts to aid installation:

- build.sh - Install dependencies from multiple sources.
- run.sh - Call the ./build.sh and start the API.

To run locally, I've used Python 3.10 due to some limitations in the dependencies.

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

### Containerize the Api's

#### Backend API

I've created a new docker file with two stages to avoid to transport unnecessary files to the final image:

- The first one to build and prepare the dependencies
- The second stage to get the dependencies and run the application

```bash
cd backend-api
docker buildx build -t backend-api:latest . 
```

I've found minor issues due requirements.txt provided for this application:

PyTorch packages are not compatible with Alpine Linux. Honestly, I did not investigate this issue further to check if there is any way to use Alpine images and install those dependencies.
- Pytorch docker images are too big( +3GB)
- python-slim images use Debian; even the tiny image after installing Pytorch, the size stills 1.05GB.


###### Vulnerabilities 

After conducting a vulnerability check on the Docker image, I identified:

```
30 vulnerabilities found in 15 packages
  UNSPECIFIED  3   
  LOW          4   
  MEDIUM       14  
  HIGH         9   
  CRITICAL     0
```

I updated some dependencies to ensure the applications continue to run and to improve the overall security posture:

```
6 vulnerabilities found in 2 packages
  LOW       4  
  MEDIUM    2  
  HIGH      0  
  CRITICAL  0 
```

There is ongoing work to remediate Medium and Low vulnerabilities, underscoring the importance of this step in containerizing applications.

To build and check vulnerabilities, I utilized Docker locally. Tools like [trivy](https://trivy.dev) offer more extensive scanning capabilities.
 


To get an overview of the vulnerabilites: 

``` bash
docker scout quickview --only-fixed
```

To get the analisys: 

``` bash
docker scout cves local://backend-api:latest 
```

Upon remediation and image building, the size was noted to be excessively large. A significant portion of this size stemmed from unused PyTorch packages. I recommend revisiting the application's requirements to minimize dependencies and reduce image size.


### Data API

Similar steps were implemented for the Data API regarding requirements updates, and gunicorn was adopted as the backend API.

Log folder paths were adjusted to /var/data/logs to facilitate logging within containers. Volume mounts were added to save logs.

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

PS: Here I'm not using a remote container registry. I'm loading all the images to the Cluster, then My chart is configured to never donwload the image. But in a real scenario I would push the image to the registry and configure the cluster to download from there.

To load the minikube:

```bash
minikube image load <<image>>
```

on values.yaml for the stack:

```yaml
backendApi:
  replicaCount: 1  
  image:
    repository: backend-api
    pullPolicy: Never    
    tag: "latest"
 
dataApi:
  replicaCount: 1  
  image:
    repository: data-api
    pullPolicy: Never    
    tag: "latest"  

```

After containerizing the applications, I created three Helm charts:

- abn-stack: Combination of Data API and Backend API Helm charts.
- backend-api
- data-api

The backend-api Helm chart requires configuration for **integrationKeySecretName**. As **EXTERNAL_INTEGRATION_KEY** is crucial for authenticating the external API, each environment necessitates a corresponding secret. Using a secret reference offers a straightforward and secure method for storing and utilizing sensitive data.

For both APIs, I implemented dummy healthz and readyz endpoints to facilitate liveness and readiness probes.

The abn-stack values.yaml for the development environment:

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

 To create these charts, I used helm create to generate a complete chart template, making minimal adjustments to specific configurations such as adding the secret reference requirement for backend-api and volume mounts for data-api.

The abn-stack chart references the backend-api and data-api charts from the same repository:

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


After defining this repository, it's crucial to build the abn-stack repository to ensure all dependencies are up-to-date. Navigate to /deployment/helm/abn-stack and execute:

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


 Before releasing the installation, create a new secret to store EXTERNAL_INTEGRATION_KEY:

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

I developed a new playbook and variable files to support the Ansible deployment.

The playbook app-deploy.yaml:

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

In this setup, the environment name serves as a suffix for the release and namespace on the Kubernetes cluster. The abn_app_chart points to an absolute path, which ideally should reference a Git repository or private Helm repository for team use.

The dev.yaml file:

```yaml
environment_name: dev 
kubeconfig_path: "/Users/myuser/.kube/config"
valueFilesPath: "../../configuration/dev.yaml"
k8s_context: minikube
```

Here, environment_name defines the environment, valueFilesPath points to the relative path of values.yaml, and kubeconfig_path specifies the Kubernetes configuration path. Secure storage of Kubernetes authentication details, like in a remote vault for non-development environments, is recommended.


To deploy the helm chart using ansible run the command:

```
ansible-playbook ./deployment/ansible/playbooks/app-deploy.yaml -e app_env=dev
```

the app_env will point the playbook to the dev/prod variable files. 

After the deployment I can see the pods:

```
kubectl get pods -n dev
```

```
NAME                                      READY   STATUS    RESTARTS   AGE
abn-app-dev-backendapi-59d985857c-qssmb   1/1     Running   0          113s
abn-app-dev-dataapi-746c7cbfc5-xmrxg      1/1     Running   0          113s
```

## Monitoring 


#### Demonstrating Node, Pod, and Container Resource Utilization Monitoring

A common approach to monitor resources is using the Metrics API. Begin by installing the Metrics Server ([see official documentation](https://github.com/kubernetes-sigs/metrics-server)):

```
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

- To retrieve resource utilization from all nodes:

``` 
kubectl top node
```

- For pod resource utilization:

``` 
kubectl top pod -n <NAMESPACE>
```


- To obtain container resource utilization within a specific pod:

``` 
kubectl top pod <POD_NAME> --container=true -n <NAMESPACE>
```


- Display resource utilization for Pods with a specific label (e.g., k8s-app=kube-Devops):

```
kubectl top pod -l=k8s-app=kube-Devops
```

While Metrics Server primarily serves autoscaling purposes, it can provide basic resource utilization data. For more extensive monitoring, consider Prometheus, a powerful tool commonly used for Kubernetes cluster monitoring.

### Health_check.sh script changes

Regarding the Health Script, multiple alternatives exist, each with its merits. Two options worth considering include:

Implementing a script executed by the Liveness Probe.
Using a CronJob for external health checks, saving results into a volume.
I opted for the second option and created four files within the health_check folder:

- pv.yaml
- pvc.yaml
- job.yaml
- health_check.yaml

Additionally, I added a script to a ConfigMap utilized by a Job for performing health checks:

``` bash
kubectl create configmap health-check-script --from-file=health_check.sh -n dev
```

And then applied all the 3 yaml files:

``` bash
kubectl apply -f job.yaml -n dev
kubectl apply -f pv.yaml -n dev
kubectl apply -f pvc.yaml -n dev

```

Before applying I've adjusted the SERVICE_URL environment variable at the job.yaml file. This is one of the usage for this halth_check.sh script. 

I hope to have the opportunity to dicuss these decisions, this one about the halth_check is one that I believe that I have no full understanding about the expectations. 
