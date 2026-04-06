# ADR-1000: System-to-System Authentication approach

|| Description |
| --- | --- |
| Status | `Accepted` |
| Date | 2026-01-01 |
| Decision | Use Private Key JWT for OAuth2 System-to-System Authentication |

### Context
Existing system uses OAuth2 client_credentials with shared client secrets across services.  This is causing secret sprawl, rotation complexity, and audit gaps.

### Decision
Use private_key_jwt (asymmetric keypair) for client authentication to the Authorization Server. Publish client public keys via a JWKS endpoint. Require signed client_assertion JWTs per RFC 7521/7523.   

### Rationale
* No shared secrets reduce credential exposure
* Stateless verification at Authorization Server via JWKS
* Supports inheritent key rotation
* Non‑repudiation via asymmetric signatures

### Alternatives considered
1. Keep client_credentials (shared secret): Shared Secrets 
2. mTLS: Requires cert management and sharing
3. OAuth2 Mutual TLS + PKJWT hybrid: introduces higher complexity

### Consequences
* Requires client key management and secure private key storage
* Authorization Server must support JWKS and private_key_jwt
* Adds operational complexity (key provisioning, rotation, KMS integration)

#### Operational requirements 
* Implement JWKS endpoint
* Implement caching/TTL for JWKS
* Enable rotation automation
* Define incident revocation procedures