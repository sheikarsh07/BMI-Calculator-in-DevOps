# BMI Calculator — Jenkins → Docker → Ansible → Terraform → K3s Pipeline
### Full guide: what everything is, why it's used, how to run it, and viva prep

---

## 1. The Big Picture (say this first in your viva)

You are building a **CI/CD pipeline** — a fully automated path from "code change" to
"running application," with a security check in the middle. One tool per job:

| Stage | Tool | Job | Why this tool |
|---|---|---|---|
| 1. Orchestration | **Jenkins** | Watches your code repo, runs every stage below in order, stops the pipeline if a stage fails | It's the "conductor" — nothing forces it to be Jenkins, but it's the industry-standard free CI/CD server |
| 2. Packaging | **Docker** | Packages the app + all its dependencies into one portable image | Guarantees the app runs identically on your laptop, the Jenkins server, and the K3s cluster ("works on my machine" problem solved) |
| 3. Security check | **Ansible** | Runs a vulnerability scanner (Trivy) against the image and fails the pipeline if serious CVEs are found | Ansible is a config-management/automation tool — here it automates running a security tool and interpreting the result, so a human doesn't have to |
| 4. Provisioning/Deployment | **Terraform** | Declares "I want 2 replicas of this image running as a Service" and pushes that desired state to the cluster | Infrastructure-as-Code: your deployment is a version-controlled file, not a manual `kubectl` command someone typed once |
| 5. Runtime | **K3s (Kubernetes)** | Actually runs and manages the containers — restarts crashed ones, load-balances traffic, exposes the app on a port | Kubernetes is the standard for running containers in production; K3s is a lightweight distribution of it, perfect for a laptop/VM/student project |

**One-sentence answer if asked "explain your architecture":**
"Jenkins automates the pipeline: it builds a Docker image of my Flask BMI app, uses Ansible to scan that image for vulnerabilities with Trivy, and if it passes, uses Terraform to declare the deployment to a K3s Kubernetes cluster, which actually runs the containers."

---

## 2. What each tool actually is (for the viva, go one level deeper)

### Docker — containerization
- A **container** is a lightweight, isolated unit that packages your app's code, runtime (Python), libraries, and config together.
- Difference from a VM: a VM virtualizes an entire OS (heavy, slow to boot). A container shares the host's OS kernel and only isolates the process — much lighter and starts in seconds.
- **Dockerfile** = the recipe to build an image. **Image** = the immutable packaged app. **Container** = a running instance of an image.
- Key Dockerfile concepts used in your project:
  - `FROM python:3.11-slim` — base image (small Linux + Python preinstalled)
  - `WORKDIR` — sets the working directory inside the container
  - `COPY requirements.txt .` then `RUN pip install` *before* copying the rest of the code — this is **layer caching**: Docker only re-runs `pip install` if `requirements.txt` changes, making rebuilds faster
  - `EXPOSE 5000` — documents which port the app listens on
  - `USER appuser` — security best practice: don't run the app as root inside the container

### Jenkins — CI/CD orchestration
- Jenkins runs a **pipeline**, defined in a `Jenkinsfile` (this is "Pipeline as Code" — the build process itself is version-controlled, not clicked together in a UI).
- A **Declarative Pipeline** (what we used) has `stages`, each with `steps`. If any step fails, the pipeline stops (fail-fast) — that's exactly how the vulnerability gate works: if Ansible/Trivy finds a critical CVE, Terraform never runs, so a vulnerable image never reaches your cluster.
- Jenkins needs a **Jenkins agent** with docker, ansible, terraform, and kubectl CLIs installed to actually run these commands (see setup steps below).

### Ansible — configuration management & automation
- Ansible automates running commands/configuration across machines using **playbooks** (YAML files describing tasks) and an **inventory** (list of hosts to run against).
- It's "agentless" — no software needs to be pre-installed on target machines, it just uses SSH (or, for localhost as in our case, a local connection).
- In our project we use it to automate a **Trivy** vulnerability scan of the built image and turn the scan's exit code into a pass/fail decision for the pipeline. This is the piece answering "runs Ansible scripts to check container vulnerabilities."
- If asked "why Ansible and not just a shell script?" — answer: Ansible is idempotent, human-readable, and scales to many hosts; here it's a simple demonstration of that pattern on one host.

### Terraform — Infrastructure as Code (IaC)
- You describe your **desired end state** (e.g., "2 replicas of this image, exposed via NodePort 30080") in `.tf` files, and Terraform figures out what API calls are needed to make reality match that description.
- Core workflow: `terraform init` (downloads the provider plugin) → `terraform plan` (shows what will change) → `terraform apply` (makes the change).
- We use the **Kubernetes provider** for Terraform, so instead of Terraform provisioning cloud VMs, it's talking directly to the K3s cluster's API (same API `kubectl` uses) and creating a `Deployment` and a `Service` resource.
- **State file** (`terraform.tfstate`): Terraform's record of what it created, so next time you run `apply` it knows what already exists vs. what needs to change.

### K3s / Kubernetes — container orchestration
- **Kubernetes** manages containers across a cluster: it restarts crashed containers, can scale them, load-balances traffic between replicas, and exposes them to the network.
- **K3s** is a certified, lightweight Kubernetes distribution (single binary, low memory footprint) made by Rancher — ideal for edge devices, CI pipelines, and student laptops, unlike full Kubernetes which needs a heavier multi-node setup.
- Key objects you're using:
  - **Deployment** — describes how many replicas (copies) of your app's Pod should run, and which image to use. Kubernetes constantly checks reality against this and self-heals (e.g., restarts a crashed pod).
  - **Pod** — the smallest deployable unit; one or more containers sharing storage/network.
  - **Service** — a stable network endpoint in front of your pods (pods get recreated with new IPs; the Service address stays constant). We use **NodePort**, which opens a fixed port (30080) on every cluster node so you can access the app from outside.
  - **Liveness/Readiness probes** — Kubernetes hits your `/health` endpoint to know if a pod is alive and ready to receive traffic.

---

## 3. How to actually run this (step by step)

You'll want a Linux machine or VM (Ubuntu recommended) — a cloud VM, VirtualBox VM, or WSL2 on Windows all work.

### Step 1 — Install Docker
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER   # then log out/in
docker --version
```

### Step 2 — Install K3s (this gives you a working Kubernetes cluster in one command)
```bash
curl -sfL https://get.k3s.io | sh -
sudo k3s kubectl get nodes        # confirm the node is "Ready"
# Copy kubeconfig so kubectl/terraform outside root can use it:
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER ~/.kube/config
```

### Step 3 — Install Ansible
```bash
sudo apt update && sudo apt install -y ansible
ansible --version
```

### Step 4 — Install Trivy (the vulnerability scanner Ansible calls)
```bash
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
```

### Step 5 — Install Terraform
```bash
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

### Step 6 — Install Jenkins
```bash
sudo apt update
sudo apt install -y openjdk-17-jre
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee /usr/share/keyrings/jenkins-keyring.asc
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" | sudo tee /etc/apt/sources.list.d/jenkins.list
sudo apt update && sudo apt install -y jenkins
sudo systemctl start jenkins
# Visit http://<your-ip>:8080 and follow setup wizard
# Give the 'jenkins' user permission to run docker:
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Step 7 — Set up your Git repo
Push this whole `bmi-project/` folder to a GitHub repo. Jenkins pulls from there.

### Step 8 — Create the Jenkins Pipeline job
1. Jenkins dashboard → New Item → Pipeline
2. Under "Pipeline" section → "Pipeline script from SCM" → Git → paste your repo URL
3. Script Path: `Jenkinsfile`
4. Save → Build Now

### Step 9 — Run a local Docker registry (so Jenkins can push/K3s can pull images without Docker Hub)
```bash
docker run -d -p 5000:5000 --name registry registry:2
```

### Step 10 — Watch it run
Jenkins console output will show each stage. If Trivy finds a CRITICAL CVE, the pipeline stops before Terraform runs. If it passes, visit:
```
http://<your-node-ip>:30080
```
and you should see your BMI Calculator.

---

## 4. Files in this project and what each does

```
bmi-project/
├── app/
│   ├── app.py              # Flask BMI calculator (business logic)
│   ├── templates/index.html# Web form UI
│   ├── requirements.txt    # Python deps (Flask)
│   └── Dockerfile          # Recipe to package the app into an image
├── Jenkinsfile              # Defines the CI/CD pipeline stages
├── ansible/
│   ├── inventory.ini        # Tells Ansible which host(s) to run against
│   └── playbook.yml         # Runs Trivy scan, fails build on critical CVEs
├── k8s/
│   ├── deployment.yaml      # (reference) raw Kubernetes manifest for the app
│   └── service.yaml         # (reference) raw Kubernetes manifest for networking
└── terraform/
    ├── main.tf               # Declares Deployment + Service via Kubernetes provider
    └── variables.tf          # Configurable inputs (image name, kubeconfig path)
```

> Note: `k8s/*.yaml` files are included as a **reference** showing what "plain Kubernetes" deployment looks like — in your actual pipeline, **Terraform** creates the equivalent resources directly via its Kubernetes provider (that's the "deploy to K3s using Terraform scripts" requirement). You can mention in your viva that you understand both approaches and chose Terraform to satisfy the IaC requirement.

---

## 5. Likely viva questions and how to answer them

**Q: Why use Docker instead of just deploying the Python app directly?**
A: Docker guarantees the exact same runtime environment everywhere — dependencies, Python version, OS libraries — eliminating "it worked on my machine" issues, and it's the format Kubernetes expects to run.

**Q: What's the difference between Docker and Kubernetes?**
A: Docker builds and runs a single container. Kubernetes orchestrates many containers across a cluster — restarting, scaling, and networking them. You'd use Docker without Kubernetes for a single small app, but Kubernetes for anything needing resilience/scale.

**Q: Why Ansible for vulnerability scanning instead of just running Trivy directly in Jenkins?**
A: You *could* run Trivy directly with a shell step. Ansible is used here to demonstrate configuration-management-style automation (idempotent, declarative YAML tasks) — in a larger setup, Ansible could also configure the scanning host itself, install Trivy if missing, and manage several scan targets consistently.

**Q: What does Terraform actually add over `kubectl apply -f deployment.yaml`?**
A: Terraform tracks **state** — it knows exactly what it created and can show a `plan` (diff) before applying changes, detect drift, and manage the full lifecycle (create/update/destroy) declaratively, versus `kubectl apply` which just pushes a file with no dependency graph or state tracking.

**Q: Why K3s instead of full Kubernetes (kubeadm)?**
A: K3s is a single lightweight binary (<100MB), needs less memory/CPU, and installs in one command — ideal for a single-node student/dev setup, while still being a fully conformant Kubernetes distribution.

**Q: What happens if the vulnerability scan fails?**
A: The Ansible playbook's `fail` task triggers based on Trivy's exit code, which makes the Jenkins step exit non-zero, which stops the pipeline before the "Push Image" and "Deploy to K3s" stages — so a vulnerable image never reaches production.

**Q: What is idempotency, and where does it show up here?**
A: An idempotent operation gives the same result no matter how many times you run it. Both Ansible playbooks and `terraform apply` are idempotent — running them twice with no changes made in between does nothing the second time, which is what makes automation safe to re-run.

**Q: How does Kubernetes know if your app is healthy?**
A: Via the liveness/readiness probes hitting your `/health` endpoint — if it stops responding, Kubernetes restarts the pod (liveness) or stops sending it traffic (readiness) until it's healthy again.

---

## 6. Suggested order to actually learn this (if you have time before the viva)

1. Docker basics — build/run/tag/push an image manually first, understand it before automating it
2. Kubernetes/K3s basics — install K3s, manually `kubectl apply` the `k8s/*.yaml` files, see the app running
3. Terraform basics — replace the manual `kubectl apply` with `terraform apply` using the Kubernetes provider
4. Ansible basics — write a tiny playbook that just prints "hello", then build up to running Trivy
5. Jenkins — wire all the above into one pipeline last, since it just calls the tools you already understand individually
