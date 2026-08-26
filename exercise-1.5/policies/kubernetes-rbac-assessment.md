# Kubernetes RBAC Security Assessment

**Exercise 1.5** | Date: August 26, 2026

---

## Current RBAC Configuration

```yaml
# Current: Overly permissive ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: app-developer
rules:
  - apiGroups: ["*"]
    resources: ["*"]
    verbs: ["*"]
---
# Current: ClusterRoleBinding to all developers
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: developer-binding
subjects:
  - kind: Group
    name: developers
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: app-developer
  apiGroup: rbac.authorization.k8s.io
```

---

## Security Findings

| # | Severity | Finding | Description | Recommendation |
|---|----------|---------|-------------|----------------|
| 1 | 🔴 Critical | Wildcard resources | `resources: ["*"]` allows access to all K8s resources | Use specific resource names |
| 2 | 🔴 Critical | Wildcard verbs | `verbs: ["*"]` allows create, delete, modify | Use only required verbs |
| 3 | 🔴 Critical | Cluster-wide scope | ClusterRole gives access to all namespaces | Use namespace-scoped Role |
| 4 | ⚠️ High | No resource names | Can access all secrets in cluster | Add `resourceNames` where possible |
| 5 | ⚠️ High | No namespace restriction | Developers can access production | Use RoleBinding with namespace |
| 6 | ⚠️ Medium | No API group restriction | Access to all API groups | Specify required apiGroups |
| 7 | ⚠️ Medium | No label selectors | Cannot restrict by resource labels | Add label-based conditions |

---

## Remediation: Namespace-Scoped Roles

```yaml
# Improved: Namespace-scoped Role for development
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer
  namespace: development
rules:
  - apiGroups: ["", "apps", "batch"]
    resources:
      - pods
      - pods/log
      - pods/exec
      - services
      - deployments
      - replicasets
      - configmaps
      - secrets
      - jobs
      - cronjobs
    verbs:
      - get
      - list
      - watch
      - create
      - update
      - patch
      - delete
    resourceNames: []  # Add specific resource names if needed
---
# Improved: Namespace-scoped RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: developer-binding
  namespace: development
subjects:
  - kind: Group
    name: developers
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: developer
  apiGroup: rbac.authorization.k8s.io
```

```yaml
# Read-only Role for production namespace
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer-readonly
  namespace: production
rules:
  - apiGroups: ["", "apps"]
    resources:
      - pods
      - pods/log
      - services
      - deployments
      - configmaps
    verbs:
      - get
      - list
      - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: developer-readonly-binding
  namespace: production
subjects:
  - kind: Group
    name: developers
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: developer-readonly
  apiGroup: rbac.authorization.k8s.io
```

```yaml
# CI/CD Service Account Role (minimal permissions)
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: cicd-deployer
  namespace: production
rules:
  - apiGroups: ["apps"]
    resources:
      - deployments
    verbs:
      - get
      - update
      - patch
  - apiGroups: [""]
    resources:
      - services
      - configmaps
    verbs:
      - get
      - list
      - watch
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: cicd-deployer-binding
  namespace: production
subjects:
  - kind: ServiceAccount
    name: cicd-sa
    namespace: cicd
roleRef:
  kind: Role
  name: cicd-deployer
  apiGroup: rbac.authorization.k8s.io
```

---

## Network Policy Recommendations

```yaml
# Deny all ingress by default
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
---
# Allow only from specific namespaces
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-frontend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: production
          podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 5000
---
# Deny egress to internet except DNS
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-egress-except-dns
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to: []
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

---

## Pod Security Standards

```yaml
# Pod Security Policy
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  runAsUser:
    rule: MustRunAsNonRoot
  seLinux:
    rule: RunAsAny
  fsGroup:
    rule: RunAsAny
  supplementalGroups:
    rule: RunAsAny
  volumes:
    - configMap
    - emptyDir
    - persistentVolumeClaim
    - secret
  hostNetwork: false
  hostIPC: false
  hostPID: false
```

---

## Audit Commands

```bash
# Find all ClusterRoleBindings
kubectl get clusterrolebindings -o json | jq -r '.items[] | select(.roleRef.name=="cluster-admin") | .subjects'

# Find all ClusterRoles with wildcard permissions
kubectl get clusterroles -o json | jq -r '.items[] | select(.rules[] | .resources[]=="*" or .verbs[]=="*") | .metadata.name'

# Check for pods running as root
kubectl get pods --all-namespaces -o json | jq -r '.items[] | select(.spec.containers[].securityContext.runAsUser==0 or .spec.securityContext.runAsUser==0) | "\(.metadata.namespace)/\(.metadata.name)"'

# Find secrets access
kubectl get roles,clusterroles -o json | jq -r '.items[] | select(.rules[] | .resources[] | contains("secrets")) | .metadata.name'
```

---

## Summary

| Category | Current State | Target State | Gap |
|----------|---------------|--------------|-----|
| RBAC Scope | Cluster-wide | Namespace-scoped | Critical |
| Permissions | Wildcard | Least-privilege | Critical |
| Network | No policies | Default deny | High |
| Pod Security | None | Restricted | High |
| Secret Access | Unrestricted | Scoped | Medium |
