#!/bin/bash

NAMESPACE="monitoring"

helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install grafana grafana/enterprise-stack \
  -n $NAMESPACE -f observability/grafana/helm-values.yaml

helm upgrade --install loki grafana/loki \
  -n $NAMESPACE -f observability/loki/helm-values.yaml

helm upgrade --install promtail grafana/promtail \
  -n $NAMESPACE -f observability/promtail/helm-values.yaml

helm upgrade --install mimir grafana/mimir-distributed \
  -n $NAMESPACE -f observability/mimir/helm-values.yaml

helm upgrade --install tempo grafana/tempo-distributed \
  -n $NAMESPACE -f observability/tempo/helm-values.yaml
