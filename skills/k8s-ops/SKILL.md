---
name: k8s-ops
description: Work safely with Kubernetes clusters via kubectl (and helm). Use for inspecting workloads, debugging pods, reading logs, and applying manifests. Front-loads read-first/confirm-before-mutate norms and common diagnostic recipes.
---

# Kubernetes operations

Default to **read-only** investigation. Any mutating or destructive command
(`delete`, `apply`, `scale`, `rollout restart`, `cordon`, `drain`, `edit`)
requires explicit confirmation first — and confirm the active context/namespace
before running it.

## Always know where you are

```sh
kubectl config current-context
kubectl config get-contexts
kubectl config use-context CONTEXT          # switch cluster — confirm intent
kubectl config set-context --current --namespace NS
```

State the target context + namespace before any write.

## Inspect

```sh
kubectl get pods -A                          # or -n NS
kubectl get deploy,svc,ingress -n NS
kubectl describe pod POD -n NS
kubectl get events -n NS --sort-by=.lastTimestamp
kubectl get pod POD -n NS -o yaml
```

## Debug

```sh
kubectl logs POD -n NS                        # add -c CONTAINER for multi-container
kubectl logs POD -n NS --previous            # crashed/restarted container
kubectl logs -f deploy/NAME -n NS            # follow a deployment's pods
kubectl exec -it POD -n NS -- sh
kubectl port-forward svc/NAME -n NS 8080:80
kubectl top pod -n NS                         # needs metrics-server
```

## Mutations (confirm first)

```sh
kubectl apply -f FILE.yaml -n NS              # prefer: kubectl diff -f FILE first
kubectl rollout restart deploy/NAME -n NS
kubectl rollout status deploy/NAME -n NS
kubectl scale deploy/NAME --replicas=N -n NS
kubectl delete pod POD -n NS                  # destructive
kubectl drain NODE --ignore-daemonsets       # destructive — node maintenance
```

Preview before applying: `kubectl diff -f FILE.yaml -n NS`.

## Helm (if used)

```sh
helm list -n NS
helm get values RELEASE -n NS
helm diff upgrade RELEASE CHART -n NS         # needs helm-diff plugin
helm upgrade RELEASE CHART -n NS              # WRITE: confirm first
```

## ArgoCD (if used)

```sh
argocd app list
argocd --core --refresh app get APP_NAME
argocd --core --refresh app sync APP_NAME # WRITE: confirm first
```

## Safety notes

- Never run `delete`/`drain`/`apply` against a `prod` context without an explicit
  go-ahead naming the cluster.
- Prefer label selectors over bare names for bulk reads; never for bulk deletes
  without review.
- Avoid `kubectl edit` in agentic flows — prefer `apply` from a reviewed manifest
  so the change is diffable and reversible.
