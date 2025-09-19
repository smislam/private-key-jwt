# Private Key JWT Authentication for Enterprise Security

In this project, we implement the OIDC `Private Key JWT` for System To System Authentication.  The Private Key JWT authentication method enhances OAuth 2.0 security by requiring clients to generate a signed JSON Web Token (JWT) using an asymmetric private key.  This approach eliminates the need to store or transmit client secrets, dramatically reducing the risk of credential exposure, and aligns with high security requirements for the [Financial-grade API (FAPI)](https://openid.net/specs/fapi-security-profile-2_0-final.html) Security Profile defined by the OpenID Foundation.

[Read the Medium article on this topic.](https://medium.com/@smislam_53676/level-up-your-api-security-with-private-key-jwt-75f12297b605)

This example uses [RFC 7521 - Assertion Framework](https://www.rfc-editor.org/rfc/rfc7521.html) and [RFC 7523 - JWT Profile for Client Authentication](https://www.rfc-editor.org/rfc/rfc7523.html) implementation.

> *If you are still using `Client_Credentials` grant flow, please see my Github project on how you can [Securly Shrare Secrets](https://github.com/smislam/securely-share-secrets).*

## Problems with Traditional Client Authentication

```mermaid
graph TB
    subgraph Traditional["Client Credentials"]
        A[Client App] -->|sends client_secret| B[Auth Server]
    end

    classDef ccStyle fill:#ffebee,stroke:#c62828,stroke-width:2px    
    class A,B ccStyle
``` 
- Uses Client_Credentials grant flows
- API provider shares Secrets with Client
- Client sends Secrets to Auth Server
- Secrets Transmitted over network
- Secrets Stored in multiple places
- No Secret Rotation or is complex
- No non-repudiation

### Security Vulnerabilities in Traditional Approach
- **Secret Exposure**: Client secrets in logs, configuration files, memory dumps
- **Credential Stuffing**: Compromised secrets used across multiple systems  
- **Rotation Complexity**: Coordinated updates across distributed systems
- **Network Interception**: Secrets transmitted in requests


## Why Private Key JWT authentication?

```mermaid
graph TB
    subgraph Modern["Private Key JWT"]
        A[Client App] -->|sends signed JWT| B[Auth Server]
        B -->|fetches public key| C[JWKS Endpoint]
    end
    
    classDef pkjStyle fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    class A,B,C pkjStyle
```

- Enhanced Security using RFC 7521/7523 to enhance OAuth 2.0 security
- No shared secrets
- Cryptographic proof
- Stateless verification
- Non-repudiation

### RFC 7521: JWT Assertions for OAuth 2.0
- Defines how JWTs can be used as authorization grants
- Establishes client assertion framework
- Security considerations for JWT-based authentication

### RFC 7523: JWT Profile for Client Authentication  
- Specific implementation for `private_key_jwt`
- JWKS integration requirements
- Signature algorithm specifications

## Private Key JWT Architecture
![image](pkj-architecture.png "Private Key JWT Architecture")


## Sequence Diagram (How do we do it?) 

```mermaid
sequenceDiagram
    participant Client as Client Application
    participant JWKS as Client JWKS Endpoint
    participant AS as Authorization Server
    participant API as Service Provider API

    Note over Client,API: Setup

    Note over Client: 1. Generate Key Pair
    Client->>Client: Generate RSA/EC Private Key
    Client->>Client: Extract Public Key
    
    Note over Client,JWKS: 2. Host Public Key
    Client->>JWKS: Deploy Public Key as JWKS
    Note right of JWKS: JWKS Format:<br/>{<br/>  "keys": [{<br/>    "kty": "RSA",<br/>    "use": "sig",<br/>    "kid": "key-1",<br/>    "n": "...",<br/>    "e": "AQAB"<br/>  }]<br/>}

    Note over Client,API: Start Secure Communication with Authorization Server

    Note over Client: 3. Create Client Assertion
    Client->>Client: Create JWT with claims:<br/>iss: client_id<br/>sub: client_id<br/>aud: token_endpoint<br/>exp: current + 5min<br/>iat: current<br/>jti: unique_id
    Client->>Client: Sign JWT with Private Key

    Note over Client,AS: 4. Token Request
    Client->>AS: POST /token<br/>grant_type=client_credentials<br/>client_assertion_type=<br/>urn:ietf:params:oauth:<br/>client-assertion-type:<br/>jwt-bearer<br/>client_assertion={signed_jwt}

    Note over AS: 5. Validate Client
    AS->>AS: Extract 'iss' from JWT
    AS->>AS: Lookup client config<br/>Find JWKS endpoint URL

    Note over AS,JWKS: 6. Fetch Public Key
    AS->>JWKS: GET /jwks
    JWKS-->>AS: Return JWKS with public key(s)

    Note over AS: 7. Verify JWT
    AS->>AS: Verify JWT signature<br/>Validate claims (exp, aud, iss)
    AS->>AS: Generate access token

    AS-->>Client: Return access token<br/>{<br/>  "access_token": "...",<br/>  "token_type": "Bearer",<br/>  "expires_in": 3600<br/>}

    Note over Client,API: 8. API Request
    Client->>API: GET /resource<br/>Authorization: Bearer {access_token}
    API->>API: Validate access token
    API-->>Client: Return protected resource

    Note over Client,API: Authentication Complete
```

# Steps to run and test
 * Run KeyCloak on Docker Desktop:
 
     `docker run -p 127.0.0.1:8080:8080 -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:26.3.2 start-dev`
     * Keycloak : http://localhost:8080/
* Setup Keycloak
    * login as admin/admin
    ![image](keycloak-login.png "Login")
    * Create Client
    ![image](create-client.png "Create Client")
    * Add Client Capability    
    ![image](client-capability.png "Create Client")
    * Setup JWKS.  Use the Client's JWKS URL.  Make sure you use `http://host.docker.internal:8000/jwks` URL.  This is becasue we are making host call from Docker.
    ![image](client-jwks-setup.png "Setup JWKS")
    * Setup Private Key JWT and Algorithm.  KeyCloak calls this Signed JWT.  Click Save
    ![image](client-signed-jwt-alg.png "Setup Signed JWT")
    * Accept the change
    ![image](accept-client-jwt.png "Accept Client change")
    * Click on Client Scope Menu on left and Create Client Scope
    ![image](create-client-scope.png "Create Client Scope")
    * On the Mappers tab, Map Client Audience
    ![image](create-audience-mapper.png "Audience Mapper")
    * Click to add a new Audience.  Click Save.
    ![image](client_audience-setup.png "Create Audience")
    * Go back to Client.  Add the Scope
    ![image](add-client-scope-button.png "add Scope")
    * Attach the scope to the client.
    ![image](client_audience-add.png "Attach Scope to Client")    

* Setup virtual environment and install requirements.
* Start the Python FastAPI server that hosts:

    `fastapi dev main.py --host 0.0.0.0 --port 8000`
    * Use the Swagger UI on http://localhost:8000/docs
    * APIs 
        * Keypair Rotation API
        * JWKS endpoint API
        * Client API
        * JWT Protected API integrated with KeyCloak
* Create the Keypairs by clicking on `rotate`, or http://localhost:8000/rotate
* Check if the JWKS endpoint Works. Click on `JWKS`, or http://localhost:8000/jwks
* If keycloak is already configured for `private_key_jwt`, then click on the client api, or http://localhost:8000/client
    * You should get a successful response:
    ![image](success.png "Private Key JWT Complete") 
---

# References
- [KeyCloak](https://www.keycloak.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Financial-grade API (FAPI) spec](https://openid.net/specs/fapi-security-profile-2_0-final.html)
- [RFC 7521 - Assertion Framework](https://www.rfc-editor.org/rfc/rfc7521.html)
- [RFC 7523 - JWT Profile for Client Authentication](https://www.rfc-editor.org/rfc/rfc7523.html)