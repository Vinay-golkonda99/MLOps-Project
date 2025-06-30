#!/bin/bash

NAMESPACE="monitoring"

helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install grafana grafana/enterprise-stack \
  -n $NAMESPACE -f values/grafana-values.yaml

helm upgrade --install loki grafana/loki \
  -n $NAMESPACE -f values/loki-values.yaml

helm upgrade --install promtail grafana/promtail \
  -n $NAMESPACE -f values/promtail-values.yaml

helm upgrade --install mimir grafana/mimir-distributed \
  -n $NAMESPACE -f values/mimir-values.yaml

helm upgrade --install tempo grafana/tempo-distributed \
  -n $NAMESPACE -f values/tempo-values.yaml
