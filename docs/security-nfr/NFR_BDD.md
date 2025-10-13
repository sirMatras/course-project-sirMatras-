# BDD Scenarios for Security NFR

## Feature: Secure password storage

  Scenario: System hashes password with Argon2id
    Given a user registers with email "test@example.com" and password "SecurePass123!"
    When the registration request is processed
    Then the stored password hash must use Argon2id with t=3, m=64MB, p=4

  Scenario: System rejects weak hashing algorithm
    Given the auth module is misconfigured to use SHA1
    When a security audit runs
    Then the CI pipeline must fail with error "Weak hashing algorithm detected"

## Feature: Rate limiting protection

  Scenario: Legitimate user stays within rate limit
    Given a client sends 90 requests in 60 seconds
    When each request is valid
    Then all requests receive HTTP 200

  Scenario: Brute-force attacker is blocked
    Given a client sends 150 login requests in 60 seconds
    When the requests contain invalid credentials
    Then responses 101–150 must return HTTP 429

## Feature: JWT token expiration

  Scenario: Access token expires after 15 minutes
    Given a user logs in and receives an access token
    When 16 minutes pass
    And the user uses the token to access /profile
    Then the response must be HTTP 401 Unauthorized
