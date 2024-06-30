# DevOps Orchestration assessment

The repo containes:
- Backend Api dummy application
- Data Api dummy application
- Health check dummy script

## Objective:
Update the backend and orchestrate migrating the 2 apps and script to kubernetes clusters following best practices using the technologies in the instructions

### Tasks:
- Add a new backend api:
  - ```/download_external_logs``` makes a call to external service's api.
  - The external download API is dummy api, _you may leave it blank,_ however it requires $EXTERNAL_INTGERATION_KEY to authenticate
  - the external api has multiple enviroments so the integration key varies by enviroment
- Update the health check to fit the new archeticture
- Create helmchart for the stack
- Deployment via Ansible
- Monitoring Kubernetes Applications - Demonstrate how to monitor the node and Pod and containers resource utilization
- How to display only resource utilization for Pods with specific label (k8s-app=kube-Devops)


#### Submission Guidelines:
- Add the nessasory folder(s) and file(s).
- If needed you may change the code structure or content or add technolgies, but its **not** part of the assessment
- Ensure you include the necessary documentations with the relevant commands used.
- Use Git


Good Luck!
