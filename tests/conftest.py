"""Test fixtures for understanding."""

import pytest
from pathlib import Path


SAMPLE_SPEC = """# Feature: User Authentication

## Functional Requirements

- **FR-001**: The system must allow users to register with email and password.
- **FR-002**: The system shall validate email format before creating an account.
- **FR-003**: The system must hash passwords using bcrypt with a minimum cost factor of 12.
- **FR-004**: The system should send a confirmation email within 30 seconds of registration.
- **FR-005**: The system must lock an account after 5 consecutive failed login attempts.

## Non-Functional Requirements

- **NFR-001**: Authentication responses must complete within 200 milliseconds.
- **NFR-002**: The system shall support at least 1000 concurrent authentication requests.
"""

SAMPLE_SPEC_2 = """# Feature: Payment Processing

## Functional Requirements

- **FR-001**: The system must process credit card payments via Stripe API.
- **FR-002**: The system shall validate card numbers using the Luhn algorithm.
- **FR-003**: The system must store transaction records for a minimum of 7 years.
"""


@pytest.fixture
def temp_spec_file(tmp_path: Path) -> Path:
    """Create a temporary spec file."""
    spec_file = tmp_path / "spec.md"
    spec_file.write_text(SAMPLE_SPEC)
    return spec_file


@pytest.fixture
def temp_specs_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with multiple spec files."""
    dir1 = tmp_path / "001-auth"
    dir1.mkdir()
    (dir1 / "spec.md").write_text(SAMPLE_SPEC)

    dir2 = tmp_path / "002-payment"
    dir2.mkdir()
    (dir2 / "spec.md").write_text(SAMPLE_SPEC_2)

    return tmp_path
