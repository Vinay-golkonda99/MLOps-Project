# DevOps-Project
A DevOps Project to gradually evolve and adopt into MLOps


# 🤖 DevOps Project with Terraform, Docker, EKS, ArgoCD 

This project demonstrates a production-grade basic MLOps pipeline that deploys a HuggingFace LLM-based Flask API to AWS EKS using GitHub Actions, ArgoCD, and monitors it using Grafana, Loki, Tempo, and Mimir.

---

## 🔧 Tech Stack

| Component         | Purpose                                |
|------------------|----------------------------------------|
| **Flask + Transformers** | ML Model Serving (LLM API)       |
| **Docker**        | Containerize the ML API                |
| **EKS (AWS)**     | Kubernetes Cluster                     |
| **Terraform**     | Infrastructure as Code (EKS + IAM)     |
| **ArgoCD**        | GitOps-based Deployment                |
| **GitHub Actions**| CI/CD Pipeline                         |
