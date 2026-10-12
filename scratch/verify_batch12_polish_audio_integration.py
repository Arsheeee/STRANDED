#!/usr/bin/env python3
"""
STRANDED - Batch 12: Polish, Audio & Final Integration Verification Suite
Validates audio management, procedural synthesis, feedback hooks across all gameplay systems,
animation polish, in-engine compilation, and rule compliance.
"""

import os
import sys
import re
import subprocess

PROJECT_DIR = r"D:\Unity\Projects\STRANDED"
SCRIPTS_DIR = os.path.join(PROJECT_DIR, "Assets", "Scripts")

def run_step(step_name, fn):
    print(f"\n[CHECK] {step_name}...")
    try:
        fn()
        print(f"  -> PASS: {step_name}")
        return True
    except AssertionError as e:
        print(f"  -> FAIL: {e}")
        return False
    except Exception as e:
        print(f"  -> ERROR: {e}")
        return False

def check_compilation():
    cmd = ["dotnet", "build", os.path.join(PROJECT_DIR, "Assembly-CSharp.csproj")]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_DIR)
    assert res.returncode == 0, f"Runtime assembly build failed:\n{res.stdout[-500:]}"

    cmd_ed = ["dotnet", "build", os.path.join(PROJECT_DIR, "Assembly-CSharp-Editor.csproj")]
    res_ed = subprocess.run(cmd_ed, capture_output=True, text=True, cwd=PROJECT_DIR)
    assert res_ed.returncode == 0, f"Editor assembly build failed:\n{res_ed.stdout[-500:]}"

def check_scope_rules():
    forbidden = ["iron", "copper", "bronze", "steel", "smelter", "anvil", "furnace"]
    for root, _, files in os.walk(SCRIPTS_DIR):
        for f in files:
            if f.endswith(".cs"):
                with open(os.path.join(root, f), "r", encoding="utf-8") as fp:
                    content = fp.read().lower()
                    for term in forbidden:
                        assert f"itemtype.{term}" not in content and f"resourcetype.{term}" not in content, \
                            f"Prohibited metal/ore term '{term}' found in {f}"

def check_audio_manager():
    audio_path = os.path.join(SCRIPTS_DIR, "AudioManager.cs")
    assert os.path.exists(audio_path), "AudioManager.cs does not exist."
    with open(audio_path, "r", encoding="utf-8") as fp:
        code = fp.read()

    required_members = [
        "public class AudioManager",
        "Instance",
        "EnsureExists",
        "sfxSource",
        "footstepSource",
        "uiSource",
        "musicSource",
        "PlayFootstep",
        "PlayResourceGather",
        "PlayItemCollect",
        "PlayCraftSuccess",
        "PlayCraftFail",
        "PlayButtonClick",
        "PlayFishBite",
        "PlayFishCatch",
        "PlayBoatBuild",
        "PlayBoatLaunch",
        "PlayVictory",
        "PlaySaveSuccess",
        "PlayLoadSuccess",
        "PlayInventoryOpen",
        "PlayInventoryClose",
        "PlayConsume",
        "PlayObjectiveUpdate",
        "PlayToolEquip",
        "PlayToolUse",
        "GenerateFootstep",
        "GenerateWoodChop",
        "GenerateStoneMine",
        "GeneratePlantForage",
        "GenerateItemCollect",
        "GenerateCraftSuccess",
        "GenerateCraftFail",
        "GenerateButtonClick",
        "GenerateFishBite",
        "GenerateFishCatch",
        "GenerateBoatBuild",
        "GenerateBoatLaunch",
        "GenerateVictory",
        "GenerateSaveSuccess",
        "GenerateLoadSuccess"
    ]
    for mem in required_members:
        assert mem in code, f"Missing required member '{mem}' in AudioManager.cs"

def check_player_movement_polish():
    path = os.path.join(SCRIPTS_DIR, "PlayerMovement.cs")
    with open(path, "r", encoding="utf-8") as fp:
        code = fp.read()
    assert "PlayFootstep" in code, "Footstep audio hook missing in PlayerMovement.cs"
    assert "MoveX" in code and "MoveY" in code, "Directional animation parameters missing in PlayerMovement.cs"

def check_resource_node_audio():
    path = os.path.join(SCRIPTS_DIR, "ResourceNode.cs")
    with open(path, "r", encoding="utf-8") as fp:
        code = fp.read()
    assert "PlayResourceGather" in code, "PlayResourceGather hook missing in ResourceNode.cs"
    assert "PlayItemCollect" in code, "PlayItemCollect hook missing in ResourceNode.cs"
    assert "PlayCraftFail" in code, "Fail audio hook missing in ResourceNode.cs"

def check_crafting_audio():
    mgr_path = os.path.join(SCRIPTS_DIR, "CraftingManager.cs")
    with open(mgr_path, "r", encoding="utf-8") as fp:
        code = fp.read()
    assert "PlayCraftSuccess" in code, "PlayCraftSuccess hook missing in CraftingManager.cs"
    assert "PlayCraftFail" in code, "PlayCraftFail hook missing in CraftingManager.cs"

    ui_path = os.path.join(SCRIPTS_DIR, "CraftingUI.cs")
    with open(ui_path, "r", encoding="utf-8") as fp:
        code = fp.read()
    assert "PlayInventoryOpen" in code, "Menu open audio missing in CraftingUI.cs"
    assert "PlayButtonClick" in code, "Button click audio missing in CraftingUI.cs"

def check_fishing_audio():
    path = os.path.join(SCRIPTS_DIR, "FishingSpot.cs")
    with open(path, "r", encoding="utf-8") as fp:
        code = fp.read()
    assert "PlayFishBite" in code, "PlayFishBite hook missing in FishingSpot.cs"
    assert "PlayFishCatch" in code, "PlayFishCatch hook missing in FishingSpot.cs"
    assert "PlayCraftFail" in code, "Fail hook missing in FishingSpot.cs"

def check_boat_and_ending_audio():
    site_path = os.path.join(SCRIPTS_DIR, "BoatConstructionSite.cs")
    with open(site_path, "r", encoding="utf-8") as fp:
        code = fp.read()
    assert "PlayBoatBuild" in code, "PlayBoatBuild hook missing in BoatConstructionSite.cs"
    assert "PlayVictory" in code, "PlayVictory hook missing in BoatConstructionSite.cs"

    ending_path = os.path.join(SCRIPTS_DIR, "EscapeEndingController.cs")
    with open(ending_path, "r", encoding="utf-8") as fp:
        code = fp.read()
    assert "PlayBoatLaunch" in code, "PlayBoatLaunch hook missing in EscapeEndingController.cs"
    assert "PlayVictory" in code, "PlayVictory hook missing in EscapeEndingController.cs"
    assert "PlayButtonClick" in code, "PlayButtonClick hook missing in EscapeEndingController.cs"

def check_save_load_audio():
    mgr_path = os.path.join(SCRIPTS_DIR, "SaveManager.cs")
    with open(mgr_path, "r", encoding="utf-8") as fp:
        code = fp.read()
    assert "PlaySaveSuccess" in code, "PlaySaveSuccess hook missing in SaveManager.cs"
    assert "PlayLoadSuccess" in code, "PlayLoadSuccess hook missing in SaveManager.cs"

    inv_path = os.path.join(SCRIPTS_DIR, "InventoryUI.cs")
    with open(inv_path, "r", encoding="utf-8") as fp:
        code = fp.read()
    assert "PlayInventoryOpen" in code, "PlayInventoryOpen hook missing in InventoryUI.cs"
    assert "PlayButtonClick" in code, "PlayButtonClick hook missing in InventoryUI.cs"

def check_survival_and_objective_audio():
    surv_path = os.path.join(SCRIPTS_DIR, "SurvivalStats.cs")
    with open(surv_path, "r", encoding="utf-8") as fp:
        code = fp.read()
    assert "PlayConsume" in code, "PlayConsume hook missing in SurvivalStats.cs"

    obj_path = os.path.join(SCRIPTS_DIR, "ObjectiveManager.cs")
    with open(obj_path, "r", encoding="utf-8") as fp:
        code = fp.read()
    assert "PlayObjectiveUpdate" in code, "PlayObjectiveUpdate hook missing in ObjectiveManager.cs"

def check_git_clean():
    res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=PROJECT_DIR)
    assert res.returncode == 0, "Git status failed."
    assert len(res.stdout.strip()) > 0, "Working tree is completely clean, which implies unwanted automated commit."

def main():
    print("======================================================================")
    print("STRANDED: BATCH 12 POLISH, AUDIO & FINAL INTEGRATION VERIFICATION")
    print("======================================================================")

    steps = [
        ("Project Compilation (Assembly-CSharp & Editor)", check_compilation),
        ("Strict Scope Boundaries & Prohibited Metals", check_scope_rules),
        ("AudioManager Implementation & Procedural Synthesis", check_audio_manager),
        ("Player Movement & Directional Animation Polish", check_player_movement_polish),
        ("Resource Gathering Audio Feedback", check_resource_node_audio),
        ("Crafting Audio Feedback & Menu SFX", check_crafting_audio),
        ("Fishing Minigame Bite & Catch Audio", check_fishing_audio),
        ("Boat Construction & Departure Sequence Audio", check_boat_and_ending_audio),
        ("Save & Load System Audio Hooks", check_save_load_audio),
        ("Survival Consumption & Objective Progression Audio", check_survival_and_objective_audio),
        ("Rule Compliance: No Automatic Git Commits or Pushes", check_git_clean),
    ]

    passed = 0
    for name, fn in steps:
        if run_step(name, fn):
            passed += 1

    print("\n======================================================================")
    print(f"RESULT: {passed}/{len(steps)} BATCH 12 VERIFICATION CHECKS PASSED!")
    print("======================================================================")
    if passed == len(steps):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
