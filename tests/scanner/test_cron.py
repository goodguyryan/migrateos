"""Tests for cron.py: cron files and systemd timer scanning."""

from src.scanner.cron import scan_cron_dirs, scan_systemd_timers

def test_scan_cron_dirs_with_files(temp_dir):
    """Verify temp_dir with cron scripts → files found with correct metadata."""
    d = temp_dir / "cron.daily"
    d.mkdir(parents=True)
    (d / "backup.sh").write_text("#!/bin/bash\necho backup\n")

    result = scan_cron_dirs(temp_dir)
    assert len(result) == 1
    assert result[0]["src"] == str(d / "backup.sh")
    assert result[0]["dest"] == "cron.daily/backup.sh"
    assert result[0]["content"] == "#!/bin/bash\necho backup\n"

def test_scan_cron_dirs_empty_dirs(temp_dir):
    """Verify empty cron directories → empty list, no crash."""
    for name in ("cron.d", "cron.hourly", "cron.daily"):
        (temp_dir / name).mkdir(parents=True)

    result = scan_cron_dirs(temp_dir)
    assert result == []

def test_scan_systemd_timers(temp_dir):
    """Verify temp_dir with .timer files → timers detected."""
    (temp_dir / "myapp.timer").write_text("[Timer]\nOnCalendar=daily\n")
    (temp_dir / "cleanup.timer").write_text("[Timer]\n")

    result = scan_systemd_timers(temp_dir)
    assert len(result) == 2
    names = {t["name"] for t in result}
    assert names == {"myapp", "cleanup"}
    for t in result:
        assert "enabled" in t
