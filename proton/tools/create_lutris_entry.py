#!/usr/bin/env python3
import os
import sys

if len(sys.argv) != 5:
    raise SystemExit("Usage: create_lutris_entry.py ENTRY_NAME RUNNER_NAME PREFIX_DIR GAME_DIR")

entry_name, runner_name, prefix_dir, game_dir = sys.argv[1:5]

from lutris import settings
from lutris.config import LutrisConfig, write_game_config
from lutris.database import schema
from lutris.database.games import add_game, get_game_by_field, get_games_by_slug, update_existing
from lutris.util.strings import slugify

os.makedirs(os.path.dirname(settings.DB_PATH), exist_ok=True)
os.makedirs(settings.GAME_CONFIG_DIR, exist_ok=True)
os.makedirs(settings.RUNNERS_CONFIG_DIR, exist_ok=True)
schema.syncdb()

wine_dir = getattr(settings, "WINE_DIR", None) or os.path.join(settings.RUNNER_DIR, "wine")
runner_dir = os.path.join(wine_dir, runner_name)
if not os.path.isfile(os.path.join(runner_dir, "proton")):
    raise SystemExit(f"Runner '{runner_name}' was not found in Lutris: {runner_dir}")

slug = slugify(entry_name)
existing = get_game_by_field(entry_name, field="name")
if not existing:
    matches = get_games_by_slug(slug)
    existing = matches[0] if matches else None

if existing and existing.get("configpath"):
    cfg = LutrisConfig(runner_slug="wine", game_config_id=existing["configpath"])
    # Keep paths a user may already have configured.
    cfg.raw_game_config["prefix"] = prefix_dir
    cfg.raw_game_config["arch"] = "win64"
    cfg.raw_game_config.setdefault("exe", "")
    cfg.raw_game_config.setdefault("working_dir", "")
    cfg.raw_runner_config["version"] = runner_name
    cfg.raw_runner_config["show_debug"] = "-all"
    cfg.save()

    update_existing(
        id=existing["id"],
        name=entry_name,
        slug=slug,
        runner="wine",
        platform="Windows",
        installed=1,
        directory=existing.get("directory") or game_dir,
        configpath=existing["configpath"],
    )
    action = "updated"
    configpath = existing["configpath"]
else:
    config = {
        "game": {
            "arch": "win64",
            "exe": "",
            "prefix": prefix_dir,
            "working_dir": "",
        },
        "wine": {
            "show_debug": "-all",
            "version": runner_name,
        },
        "system": {},
    }
    configpath = write_game_config(slug, config)
    add_game(
        name=entry_name,
        slug=slug,
        runner="wine",
        platform="Windows",
        installed=1,
        directory=game_dir,
        configpath=configpath,
    )
    action = "created"

print(f"Lutris entry {action}: {entry_name}")
print(f"  config: {configpath}")
print(f"  runner: {runner_name}")
print(f"  prefix: {prefix_dir}")