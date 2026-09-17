#!/usr/bin/env bash
# ==============================================================================
# One-Click Setup and Execution Script for BMI Project Pipeline
# Target OS: Ubuntu / Debian / WSL2
# Automates:
#   1. Local registry setup
#   2. Trivy vulnerability scanner check
#   3. Docker image build
#   4. Ansible playbook execution (Trivy scan gate)
#   5. Docker push to local registry
#   6. K3s cluster kubeconfig verification
#   7. Terraform deployment to K3s
# ==============================================================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}   BMI CALCULATOR CI/CD PIPELINE - ONE-CLICK RUNNER         ${NC}"
echo -e "${BLUE}============================================================${NC}"

# 1. Environment & Prerequisites Check
echo -e "\n${YELLOW}[Stage 0] Checking System Prerequisites...${NC}"
for cmd in docker terraform ansible; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "${RED}Error: '$cmd' is not installed. Please install it first.${NC}"
        echo "Refer to GUIDE.md for step-by-step installation instructions."
        exit 1
    else
        echo -e "  ${GREEN}✓ Found $cmd${NC}"
    fi
done

# Check if Trivy is installed, install if not
if ! command -v trivy &> /dev/null; then
    echo -e "  ${YELLOW}Trivy not found. Installing Trivy to /usr/local/bin...${NC}"
    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sudo sh -s -- -b /usr/local/bin
fi
echo -e "  ${GREEN}✓ Trivy is ready${NC}"

# Check K3s
if ! command -v k3s &> /dev/null && [ ! -f "/etc/rancher/k3s/k3s.yaml" ]; then
    echo -e "${YELLOW}Warning: K3s not detected. If running without K3s, make sure your kubeconfig is valid.${NC}"
fi

# Ensure local Docker registry is running on port 5000
echo -e "\n${YELLOW}[Stage 1] Setting up Local Docker Registry (localhost:5000)...${NC}"
if [ ! "$(docker ps -q -f name=registry)" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=registry)" ]; then
        echo "Starting existing stopped registry container..."
        docker start registry
    else
        echo "Running new local registry on port 5000..."
        docker run -d -p 5000:5000 --name registry registry:2
    fi
fi
echo -e "${GREEN}✓ Local Docker registry is running on localhost:5000${NC}"

IMAGE_NAME="localhost:5000/bmi-calculator:v1"

# Stage 2: Build Docker Image
echo -e "\n${YELLOW}[Stage 2] Building Docker Image: ${IMAGE_NAME}...${NC}"
docker build -t "${IMAGE_NAME}" ./app
echo -e "${GREEN}✓ Docker image built successfully.${NC}"

# Stage 3: Vulnerability Scan using Ansible & Trivy
echo -e "\n${YELLOW}[Stage 3] Running Security Scan via Ansible Playbook...${NC}"
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml --extra-vars "image_name=${IMAGE_NAME}"
echo -e "${GREEN}✓ Security scan passed! No CRITICAL or HIGH CVEs found.${NC}"

# Stage 4: Push to Local Registry
echo -e "\n${YELLOW}[Stage 4] Pushing Scanned Image to Registry...${NC}"
docker push "${IMAGE_NAME}"
echo -e "${GREEN}✓ Image pushed to ${IMAGE_NAME}${NC}"

# Stage 5: Deploy to K3s using Terraform
echo -e "\n${YELLOW}[Stage 5] Deploying App to K3s with Terraform...${NC}"
cd terraform

# Ensure kubeconfig file permissions
if [ -f "/etc/rancher/k3s/k3s.yaml" ]; then
    sudo chmod 644 /etc/rancher/k3s/k3s.yaml || true
fi

terraform init
terraform apply -auto-approve -var="image_name=${IMAGE_NAME}"
cd ..

echo -e "\n${BLUE}============================================================${NC}"
echo -e "${GREEN} PIPELINE DEPLOYMENT COMPLETE! ${NC}"
echo -e " Access your BMI Calculator application at:"
echo -e "   ${YELLOW}http://<node-ip>:30080${NC} (or http://localhost:30080)"
echo -e "${BLUE}============================================================${NC}"
