# Flask System Monitor on EKS

A real-time system monitoring dashboard built with Flask, psutil and Plotly.
CPU and memory gauges refresh automatically every 5 seconds, with an alert
banner when usage goes above 80%. The app is containerized with Docker, the
image is stored in Amazon ECR, and it runs on Amazon EKS.

## Features

- Live CPU and memory gauges (Plotly) with no page reload
- JSON endpoint at `/metrics` polled by the browser every 5 seconds
- Alert message when CPU or memory exceeds the threshold
- Configurable refresh interval and threshold
- Deployed to Kubernetes with a Python script

## Project structure

```
.
├── app.py              # Flask app and /metrics endpoint
├── templates/
│   └── index.html      # Dashboard with auto-refreshing gauges
├── requirements.txt
├── Dockerfile
├── ecr.py              # Creates the ECR repository (boto3)
├── k8s.py              # Creates the Deployment and Service on EKS
└── README.md
```

## Run locally

```bash
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000.

## Configuration

| Setting | Where | Default |
|---|---|---|
| Refresh interval | `REFRESH_INTERVAL_MS` in `templates/index.html` | `5000` (ms) |
| Alert threshold | `THRESHOLD` in `app.py` | `80` (%) |

## Run with Docker

```bash
docker build -t monitoring-app .
docker run -p 5000:5000 --memory=500m monitoring-app
```

## Prerequisites

- Python 3.10+, Docker, `kubectl`, and the AWS CLI
- AWS credentials configured locally:

  ```bash
  aws configure   # access key, secret key, region (us-east-1)
  aws sts get-caller-identity   # confirm it works
  ```

- An IAM user or role with permissions for ECR and EKS

## Deploy to AWS

### 1. Create the ECR repository and push the image

```bash
python ecr.py

aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker tag monitoring-app:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/<repo-name>:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/<repo-name>:latest
```

### 2. Create the EKS cluster

Created in the AWS console with two IAM roles:

- **Cluster role** (`eks.amazonaws.com`): `AmazonEKSClusterPolicy`
- **Node group role** (`ec2.amazonaws.com`): `AmazonEKSWorkerNodePolicy`,
  `AmazonEKS_CNI_Policy`, `AmazonEC2ContainerRegistryReadOnly` (lets nodes pull from ECR)

### 3. Connect kubectl

```bash
aws eks update-kubeconfig --region us-east-1 --name <cluster-name>
kubectl get nodes
```

### 4. Deploy

Update the image URI in `k8s.py`, then:

```bash
python k8s.py
kubectl get svc my-flask-service -w
```

When `EXTERNAL-IP` shows a hostname, open `http://<hostname>`.

For quick testing without a load balancer:

```bash
kubectl port-forward svc/my-flask-service 5000:80
```

## Cleanup

Delete the service first so the AWS load balancer is removed, then the cluster:

```bash
kubectl delete svc my-flask-service
kubectl delete deployment my-flask-app
```

Then delete the node group and the cluster in the EKS console.
To remove the local kubeconfig entry:

```bash
kubectl config delete-context <context-name>
kubectl config delete-cluster <context-name>
```

## Notes

- `psutil` inside a container or pod reports the host or node's usage, not the
  container's memory limit.
- EKS and load balancers are billed hourly. Tear everything down when finished.

## Tech stack

Python, Flask, psutil, Plotly.js, Docker, Amazon ECR, Amazon EKS, Kubernetes Python client
