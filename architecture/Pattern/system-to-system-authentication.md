# Enterprise Architecture: System-to-System Asymmetric Authentication

## Business Architecture

### Stakeholders
Security, Platform, API Owners, DevOps.

### Business Goals
System-to-system trust model, Avoid sharing Secrets, Ensure compliance.

## Data Architecture
AWS Systems Manager Parameter Store for credentials as SecuredString

### **Data Flows**
* Client signs client_assertion JWT and POSTs to Authorization Server token endpoint.
* Authorization Server fetches/verifies public key from JWKS (cached).
* Authorization Server issues access token.
* Resource Server validates token and enforces scopes/audience. 

## Information Systems Architecture
JWT assertion format, audience (aud), exp, jti, and JWKS metadata.

## Technology Architecture
**Components**: Client (KMS private key), JWKS Provider (FastAPI), Authorization Server (Keycloak), API Gateway/Resource Server. 

## Opportunities & Solutions
* POC Keycloak + FastAPI JWKS
* Migrate existing clients in waves
* Decommission `client_credentials` flows

> **Optional**: Create Encryption Keys on both client and Authorization server.  This allows for additional security and tokenization of the payloads during transfer.

## Implementation Governance
* Policies for algorithms (RS256/ES256)
* Enforce minimum key sizes
* Define and implement Key rotation SLAs
* Implement robust logging and audit trails
* Perform periodical access reviews
* Setup compliance checks and revocation processes

## Risks, mitigations, and deterministic checklist
||Risk| Mitigation|
|--|--|--|
|1|Private key compromise|Use HSM/KMS, short rotation, immediate JWKS key removal and revocation|
|2|JWKS cache staleness|TTL policy + push notification for rotations|
|3|Algorithm weaknesses|Enforce strong algorithms (RS256/ES256)|
|4|Implementation bugs|Use well-tested libraries, code reviews, security testing|
|5|Operational complexity|Automate key management, provide clear documentation and training.|

## Conclusion
Implementing system-to-system asymmetric authentication enhances security by eliminating shared secrets and leveraging robust cryptographic methods. By following best practices in key management, algorithm selection, and operational governance, organizations can mitigate risks and ensure a secure, scalable authentication mechanism for their APIs and services.