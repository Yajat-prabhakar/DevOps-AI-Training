# Exercise 2.5: Multi-Service Debugging Challenge

## Overview

10 intentionally broken Kubernetes manifests with common deployment issues. Your task is to identify and fix each bug.

## How to Use

1. Try to apply each broken manifest: `kubectl apply -f broken/01-broken-image.yaml`
2. Observe the error or unexpected behavior
3. Debug the issue
4. Check the fixed version in `fixed/` directory
5. Read the explanation below

## Bugs and Solutions

### 01: Broken Image Tag

**File:** `broken/01-broken-image.yaml`

**Symptom:** `ImagePullBackOff` or `ErrImagePull`

**Root Cause:** Typo in image tag (`latset` instead of `latest`)

**Fix:** Correct the image tag spelling

**Debug Commands:**
```bash
kubectl describe pod <pod-name>
kubectl get events --field-selector reason=Failed
```

---

### 02: No Resource Limits

**File:** `broken/02-no-resources.yaml`

**Symptom:** Pod uses unlimited resources, causes OOMKilled or node exhaustion

**Root Cause:** No `resources` section defined

**Fix:** Add resource requests and limits

**Debug Commands:**
```bash
kubectl top pods
kubectl describe node <node-name> | grep -A 5 "Allocated resources"
```

---

### 03: Network Policy Blocks All Traffic

**File:** `broken/03-network-policy.yaml`

**Symptom:** Pods can't resolve DNS, can't communicate

**Root Cause:** Network policy has no egress rules, blocks DNS

**Fix:** Add egress rules for DNS (port 53) and internal communication

**Debug Commands:**
```bash
kubectl get networkpolicy
kubectl describe networkpolicy deny-all-broken
kubectl exec <pod> -- nslookup kubernetes.default
```

---

### 04: Broken Probes

**File:** `broken/04-broken-probes.yaml`

**Symptom:** Pod constantly restarting, never becomes ready

**Root Cause:** Wrong probe paths and ports

**Fix:** Use correct path (`/api/health`) and port (`5000`)

**Debug Commands:**
```bash
kubectl describe pod <pod-name> | grep -A 10 "Liveness"
kubectl logs <pod-name> --previous
```

---

### 05: Missing Secrets

**File:** `broken/05-missing-secrets.yaml`

**Symptom:** `CreateContainerConfigError`

**Root Cause:** References non-existent secrets/configmaps

**Fix:** Create secrets first or reference existing ones

**Debug Commands:**
```bash
kubectl get secrets
kubectl get configmaps
kubectl describe pod <pod-name>
```

---

### 06: Scheduling Conflict

**File:** `broken/06-scheduling-conflict.yaml`

**Symptom:** Pod stuck in `Pending` state

**Root Cause:** Node affinity requires GPU nodes, but tolerations don't match

**Fix:** Remove conflicting affinity or use correct tolerations

**Debug Commands:**
```bash
kubectl get pods -o wide
kubectl describe pod <pod-name> | grep -A 10 "Events"
kubectl get nodes --show-labels
```

---

### 07: Config Mismatch

**File:** `broken/07-config-mismatch.yaml`

**Symptom:** App crashes on startup with config errors

**Root Cause:** Environment variable names don't match what app expects

**Fix:** Use correct variable names and values

**Debug Commands:**
```bash
kubectl logs <pod-name>
kubectl exec <pod-name> -- env | grep DATABASE
```

---

### 08: RBAC Denied

**File:** `broken/08-rbac-denied.yaml`

**Symptom:** App can't access Kubernetes API

**Root Cause:** No service account or RBAC permissions

**Fix:** Create service account with proper Role and RoleBinding

**Debug Commands:**
```bash
kubectl get serviceaccount
kubectl get rolebinding
kubectl auth can-i get pods --as=system:serviceaccount:app:backend-sa
```

---

### 09: PVC Pending

**File:** `broken/09-pvc-pending.yaml`

**Symptom:** Pod stuck in `Pending`, PVC in `Pending`

**Root Cause:** Storage class doesn't exist

**Fix:** Use valid storage class name

**Debug Commands:**
```bash
kubectl get pvc
kubectl describe pvc app-data-pvc
kubectl get storageclass
```

---

### 10: Startup Failure

**File:** `broken/10-startup-failure.yaml`

**Symptom:** App crashes immediately after starting

**Root Cause:** No init container to wait for database

**Fix:** Add init container to wait for DB, increase startupProbe failureThreshold

**Debug Commands:**
```bash
kubectl logs <pod-name> --previous
kubectl logs <pod-name> -c wait-for-db
kubectl get pods -o wide
```

---

## Using Cursor for Debugging

### Step 1: Analyze the Error
```
Cmd/Ctrl + L: "I'm getting this error when applying the manifest: [paste error]
What's wrong with this Kubernetes manifest?"
```

### Step 2: Get Fix Suggestions
```
Cmd/Ctrl + L: "How do I fix this ImagePullBackOff error?
@file:broken/01-broken-image.yaml"
```

### Step 3: Apply and Verify
```bash
kubectl apply -f fixed/01-broken-image.yaml
kubectl get pods -w
```

## Common Debugging Patterns

1. **Check events:** `kubectl describe pod <name>`
2. **Check logs:** `kubectl logs <name> --previous`
3. **Check YAML:** `kubectl apply -f manifest.yaml --dry-run=client`
4. **Check RBAC:** `kubectl auth can-i <verb> <resource>`
5. **Check network:** `kubectl exec <pod> -- wget -qO- http://service:port/health`
