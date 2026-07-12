# B2 Governance Cohort DER Records

This directory contains Derived Evidence Records (DER) for the B2 governance cohort.

## Completed DER Executions

- `aws-iam.der.json` derives the AWS IAM request-context policy-evaluation boundary from its canonical SRF.
- `cedar-amazon-verified-permissions.der.json` derives the Cedar / Amazon Verified Permissions policy-store evaluation boundary from its canonical SRF.
- `envoy-ext-authz.der.json` derives the Envoy ext_authz external authorization delegation boundary from its canonical SRF.
- `google-zanzibar.der.json` derives the Google Zanzibar relation-tuple Check boundary from its canonical SRF.
- `hashicorp-vault.der.json` derives the HashiCorp Vault authenticated path-policy boundary from its canonical SRF.
- `istio-authorizationpolicy.der.json` derives the Istio AuthorizationPolicy workload action-order boundary from its canonical SRF.
- `kubernetes-rbac-admission.der.json` derives the Kubernetes RBAC and admission API-server admission boundary from its canonical SRF.
- `open-policy-agent-gatekeeper.der.json` derives the Open Policy Agent Gatekeeper admission and audit enforcement boundary from its canonical SRF.
- `openfga.der.json` derives the OpenFGA authorization-model version boundary from its canonical SRF.

Each DER is constrained to direct SRF-derived evidence and BOR observation references. These records do not perform MSR measurement, comparative dataset construction, analysis, or retained classification.
