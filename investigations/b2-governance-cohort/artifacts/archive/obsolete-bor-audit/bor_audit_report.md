# B2.07 Baseline Observation Records (BOR) — Completion Audit (Governance Systems Cohort)

## Scope and protocol constraints

- Protocol dependency order (must hold): BOR → SRF → DER → MSR.
- This audit evaluates **B2.07 only**. It does **not** populate SRF, DER, or MSR.
- A BOR is considered **complete** only if each protocol-required baseline field is covered by at least one **factual** observation and each observation has a **primary-source evidence pointer**.

## Cohort systems (as instantiated in B2.07)

1. OPA + Gatekeeper
2. Kubernetes RBAC / Admission
3. AWS IAM
4. HashiCorp Vault
5. Envoy `ext_authz`
6. Istio `AuthorizationPolicy`
7. OpenFGA
8. Cedar / Amazon Verified Permissions (AVP)
9. Google Zanzibar

## Protocol-required baseline observation categories (from B2.07 completeness note)

For each system, the BOR must contain primary-source, factual observations (with evidence pointers) covering:

- **System identity** (what the system is; product/project identification)
- **Interfaces** (where and how it is configured/queried/invoked)
- **Policy representation** (what form policy takes, as described)
- **Decision/evaluation locus** (where authorization decisions are evaluated)
- **Enforcement locus** (where decisions are enforced / requests are permitted or denied)
- **Audit/logging surfaces** (what audit/log outputs exist and where)
- **Versioning** (version identifiers and/or configuration versions relevant to the observations)

## Findings: BOR completion classification

### Summary table

| System | BOR entries present in B2.07 | Classification | Notes |
|---|---:|---|---|
| OPA + Gatekeeper | 2 placeholder rows (`BOR-OPA-001..002`) | **Missing** | No factual observations; no evidence pointers. |
| Kubernetes RBAC / Admission | 2 placeholder rows (`BOR-K8S-001..002`) | **Missing** | No factual observations; no evidence pointers. |
| AWS IAM | 2 placeholder rows (`BOR-IAM-001..002`) | **Missing** | No factual observations; no evidence pointers. |
| HashiCorp Vault | 2 placeholder rows (`BOR-VAULT-001..002`) | **Missing** | No factual observations; no evidence pointers. |
| Envoy `ext_authz` | 2 placeholder rows (`BOR-ENVOY-001..002`) | **Missing** | No factual observations; no evidence pointers. |
| Istio `AuthorizationPolicy` | 2 placeholder rows (`BOR-ISTIO-001..002`) | **Missing** | No factual observations; no evidence pointers. |
| OpenFGA | 2 placeholder rows (`BOR-FGA-001..002`) | **Missing** | No factual observations; no evidence pointers. |
| Cedar / AVP | 2 placeholder rows (`BOR-CEDAR-001..002`) | **Missing** | No factual observations; no evidence pointers. |
| Google Zanzibar | 2 placeholder rows (`BOR-ZANZ-001..002`) | **Missing** | No factual observations; no evidence pointers. |

### Interpretation of “Missing” vs “missing evidence”

- **Missing observations**: The BOR “Observation” cells are placeholders (`TODO(...)`), so the factual content itself is absent.
- **Missing evidence**: The BOR “Evidence pointer” cells are also placeholders (`TODO(EVID-...)`).
- In the current manuscript state, **both the observation text and the evidence pointers are missing for every BOR row**.

## Required primary-source observations (exactly what must be collected)

For each system, collect and record **factual statements** (no interpretation) with evidence pointers to primary sources (e.g., official documentation pages, specs, API references, or authoritative repos) that directly support the statement.

### Minimum observation checklist per system (must be evidenced)

1. **System identity**
   - Product/project name as stated by the primary source
   - Governance/authorization function as stated (descriptive)
2. **Interfaces**
   - Configuration interface(s) (e.g., API/CLI/CRD/config file) as stated
   - Runtime request interface(s) (e.g., admission webhook, proxy callout, policy evaluation API) as stated
3. **Policy representation**
   - Policy artifact type(s) (documents, resources, rules, tuples, etc.) as named by the primary source
   - How policy is supplied/updated (endpoint/CLI/resource) as stated
4. **Decision/evaluation locus**
   - Where evaluation occurs (component/service/library) as stated
5. **Enforcement locus**
   - Where allow/deny is enforced (component/hook) as stated
6. **Audit/logging surfaces**
   - What audit/log outputs are described (and where they appear) as stated
7. **Versioning**
   - System version(s) relevant to the above observations (release/version string, API version, etc.)
   - Retrieval date of sources and (if applicable) commit/tag identifiers

## Prioritized checklist (cohort-wide)

Priority is defined by what unblocks the next protocol step (SRF generation requires BOR-backed interface and surface facts).

### P0 — Unblock SRF surface enumeration (highest priority)

For **each system**, add evidenced BOR observations for:

- Interfaces
- Decision/evaluation locus
- Enforcement locus

### P1 — Support policy/identity surfaces without interpretation

For **each system**, add evidenced BOR observations for:

- Policy representation (policy artifact types; how authored/loaded)
- Identity/principal representation and identity integration points (only if explicitly described by sources)

### P2 — Support later auditability and reproducibility

For **each system**, add evidenced BOR observations for:

- Audit/logging surfaces
- Versioning + retrieval metadata (versions, dates, hashes/commits where applicable)

## Blocking condition (explicit)

Until at least P0 observations are present (with evidence pointers) for every system, **SRF generation is blocked**, and therefore **DER/MSR are blocked**.
