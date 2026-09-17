variable "image_name" {
  description = "Full Docker image name:tag to deploy"
  type        = string
  default     = "localhost:5000/bmi-calculator:latest"
}

variable "kubeconfig_path" {
  description = "Path to the K3s kubeconfig file"
  type        = string
  default     = "/etc/rancher/k3s/k3s.yaml"
}
