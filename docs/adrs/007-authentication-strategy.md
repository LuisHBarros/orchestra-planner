# ADR 007: Authentication Strategy — Magic Links

- **Date:** 2026-02-08
- **Author:** luishbarros
- **Status:** accepted

## Context
Orchestra Planner requires a secure, user-friendly authentication mechanism that minimizes friction and reduces backend complexity around credential management (such as storing password hashes and implementing reset policies).

Key requirements:
- Users must be uniquely identified by email (case-insensitive).
- Minimize friction for registration/login (especially for non-technical users).
- Avoid storing passwords to reduce security risks.
- Support auditing and integration with project roles/invitations.

## Decision
Implement a passwordless authentication strategy based on Magic Links. Session token issuance is not implemented yet.

Login:
- The user enters their email and receives a single-use link containing a short-lived token (15 minutes).
- Links are one-time use and invalidated after successful login.
- Email addresses are treated as case-insensitive unique identifiers.

Session:
- The `/auth/verify` endpoint returns the authenticated user details.
- No JWT or session token is currently issued by the API.

## Benefits
- Security: eliminates risks associated with password brute-force attacks or credential database leaks.
- UX: users do not need to remember another password.
- Simplicity: reduces boilerplate code related to password management in both the domain and infrastructure layers.

## Trade-offs
- Email dependency: login availability depends on email delivery reliability.
- Phishing awareness: users must be educated to trust only official links from the system.
- Limited offline access: users cannot authenticate without email access.

## Alternatives
### Traditional Password Authentication
Pros: Familiar pattern, works offline (no email needed), allows multi-factor authentication.
Cons: Requires secure storage and hashing of passwords, more friction during registration/login, higher risk of leaks.

### OAuth / Social Login (Google, GitHub, etc.)
Pros: Quick login, reduces password management, widely known.
Cons: Requires external provider integration, potential privacy concerns, dependency on third-party service availability.

## Consequences
- Email delivery reliability becomes a critical dependency for login.
- Magic links must be generated securely, stored temporarily, and invalidated after use.
- Users must be informed about the temporary nature of links and security practices.
- If session tokens are introduced later, expiration and revocation strategies must be handled in infrastructure.
- Future enhancements (MFA, OAuth integration) can be added as optional layers without changing the core authentication flow.

## References
- Passwordless Authentication (Magic Link) – https://auth0.com/blog/passwordless-authentication/
- OWASP Top Ten – https://owasp.org/www-project-top-ten/
