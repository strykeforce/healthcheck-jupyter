from __future__ import annotations


def test_df_copy_is_shallow(robot_health_check):
    hc_df = robot_health_check.df
    sd_df = robot_health_check.swerve_drive_health_check.df

    assert hc_df.index is sd_df.index

    assert hc_df["name"].iloc[0] == "DriveSubsystem"
    assert sd_df["name"].iloc[0] == "DriveSubsystem"

    expected = "IntakeSubsystem"
    sd_df["name"].iloc[0] = expected

    assert sd_df["name"].iloc[0] == expected
    assert hc_df["name"].iloc[0] == expected
