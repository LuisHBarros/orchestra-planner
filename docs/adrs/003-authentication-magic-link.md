# ADR 003: Authentication Method - Magic Link

- **Date:** 2026-01-31
- **Author:** luishbarros
- **Status:** accepted

## Context
The Orchestra Planner requires a secure and user-friendly authentication mechanism.  
Key requirements:
- Users must be uniquely identified by email.
- Minimize friction for registration/login (especially for non-technical users).
- Avoid storing passwords to reduce security risks.
- Support for auditing and integration with project roles.

## Decision
Use **Magic Link authentication** (email-based, one-time login links) as the primary method for user authentication.

Key points:
- Upon registration or login, the system sends a unique, time-limited link to the user's email.
- The link is valid for **one-time use** and expires after **3 hours**.
- No passwords are stored or required.
- Email addresses are **case-insensitive unique identifiers**.

## Benefits
- **User-friendly:** Eliminates the need for passwords, reducing login friction.
- **Security:** No password storage reduces risk of leaks.
- **Fast onboarding:** Users can join projects immediately via email link.
- **Integration with Roles:** Magic Links can carry project/role context for seamless invitation acceptance.

## Trade-offs
- **Email Dependency:** Users must have access to their email to log in.
- **Link Expiration:** Expired links require generating a new one, which could frustrate some users.
- **Phishing Awareness:** Users must be educated to trust only official links from the system.
- **Limited Offline Access:** Users cannot authenticate without email access.

## Alternatives
- **Traditional Password Authentication**
  - **Pros:** Familiar pattern, works offline (no email needed), allows multi-factor authentication.
  - **Cons:** Requires secure storage and hashing of passwords, more friction during registration/login, higher risk of leaks.

- **OAuth / Social Login (Google, GitHub, etc.)**
  - **Pros:** Quick login, reduces password management, widely known.
  - **Cons:** Requires external provider integration, potential privacy concerns, dependency on third-party service availability.

## Consequences
- The system requires **robust email delivery** infrastructure and monitoring.
- Magic Links need to be generated securely, stored temporarily, and invalidated after use.
- Users must be informed about the temporary nature of links and security practices.
- The authentication system can scale easily without password management complexity.
- Future enhancements (MFA, OAuth integration) can be added as optional layers without changing core authentication flow.

## References
- Passwordless Authentication (Magic Link) – https://auth0.com/blog/passwordless-authentication/
- Best Practices for Email Authentication – https://owasp.org/www-project-top-ten/  
- JWT (JSON Web Tokens) for session management – https://jwt.io/
