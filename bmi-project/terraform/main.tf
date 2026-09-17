terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.31"
    }
  }
}

# Terraform talks to the K3s cluster through its kubeconfig,
# the same way kubectl does.
provider "kubernetes" {
  config_path = var.kubeconfig_path
}

resource "kubernetes_deployment" "bmi_calculator" {
  metadata {
    name = "bmi-calculator"
    labels = {
      app = "bmi-calculator"
    }
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "bmi-calculator"
      }
    }

    template {
      metadata {
        labels = {
          app = "bmi-calculator"
        }
      }

      spec {
        container {
          name  = "bmi-calculator"
          image = var.image_name

          port {
            container_port = 5000
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = 5000
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "bmi_calculator_svc" {
  metadata {
    name = "bmi-calculator-svc"
  }

  spec {
    type = "NodePort"

    selector = {
      app = "bmi-calculator"
    }

    port {
      port        = 80
      target_port = 5000
      node_port   = 30080
    }
  }
}

output "app_url" {
  value = "http://<your-k3s-node-ip>:30080"
}
