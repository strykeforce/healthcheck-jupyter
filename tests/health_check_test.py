from __future__ import annotations


def test_subsystems(health_check):
    assert ["DriveSubsystem", "IntakeSubsystem"] == health_check.subsystems
