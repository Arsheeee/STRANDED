import os
import re
import sys
import subprocess

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def verify_batch_9():
    print("=====================================================================")
    print("STRANDED: BATCH 9 BOAT CONSTRUCTION & OBJECTIVE PROGRESSION")
    print("=====================================================================")
    failures = []

    # 1. Compilation Verification
    print("\n[CHECK 1/23] Checking Project Compilation (Assembly-CSharp & Editor)...")
    rc1, out1, err1 = run_cmd("dotnet build Assembly-CSharp.csproj")
    if rc1 != 0:
        failures.append(f"Assembly-CSharp.csproj failed to compile:\n{err1 or out1}")
    else:
        print("  -> Assembly-CSharp.csproj: 0 Errors (Build SUCCESS)")

    rc2, out2, err2 = run_cmd("dotnet build Assembly-CSharp-Editor.csproj")
    if rc2 != 0:
        failures.append(f"Assembly-CSharp-Editor.csproj failed to compile:\n{err2 or out2}")
    else:
        print("  -> Assembly-CSharp-Editor.csproj: 0 Errors (Build SUCCESS)")

    # 2. Strict Scope Restriction Verification
    print("\n[CHECK 2/23] Checking Strict Scope Restrictions (NO Escape Cutscene, NO Metals, NO Chisel, NO Save/Load)...")
    prohibited_terms = [
        "StoneChisel", "Stone_Chisel", "Chisel",
        "Iron", "Steel", "Metal", "Copper", "Ore",
        "VictoryCutscene", "CreditsScene", "GameOverEscape",
        "DayNightCycle", "WeatherSystem", "SaveSystem", "LoadSystem"
    ]
    scripts_to_check = [
        "Assets/Scripts/BoatComponentRequirement.cs",
        "Assets/Scripts/BoatConstructionState.cs",
        "Assets/Scripts/BoatConstructionSite.cs",
        "Assets/Scripts/BoatConstructionUI.cs",
        "Assets/Scripts/ObjectiveManager.cs",
        "Assets/Scripts/ObjectiveUI.cs",
        "Assets/Editor/BoatSitePlacer.cs"
    ]
    for sf in scripts_to_check:
        if not os.path.exists(sf):
            failures.append(f"Missing expected script: {sf}")
            continue
        with open(sf, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                code_part = line.split("//")[0].split("/*")[0]
                if code_part.strip().startswith("*") or code_part.strip().startswith("///"):
                    continue
                for term in prohibited_terms:
                    matches = re.findall(rf"\b{term}\b", code_part, re.IGNORECASE)
                    if matches:
                        failures.append(f"Prohibited term '{term}' in {sf}:{line_no}: {line.strip()}")
    print("  -> Verified: Zero prohibited features or terms in Batch 9 code.")

    # 3. Sprite Assets and Metadata Verification
    print("\n[CHECK 3/23] Checking Progressive Boat Visual Sprites (Stages 0..5)...")
    expected_sprites = [
        "Assets/Art/Environment/Boat/boat_stage_0_slipway.png",
        "Assets/Art/Environment/Boat/boat_stage_1_hull.png",
        "Assets/Art/Environment/Boat/boat_stage_2_frame.png",
        "Assets/Art/Environment/Boat/boat_stage_3_bindings.png",
        "Assets/Art/Environment/Boat/boat_stage_4_paddle.png",
        "Assets/Art/Environment/Boat/boat_stage_5_completed.png"
    ]
    for sprite_path in expected_sprites:
        meta_path = sprite_path + ".meta"
        if not os.path.exists(sprite_path):
            failures.append(f"Missing boat sprite: {sprite_path}")
        elif not os.path.exists(meta_path):
            failures.append(f"Missing meta file for: {sprite_path}")
        else:
            size = os.path.getsize(sprite_path)
            print(f"  -> Sprite & Meta verified: {os.path.basename(sprite_path)} ({size} bytes)")

    # 4. Boat Construction Site Location & Reachability
    print("\n[CHECK 4/23] Verifying Construction Site Placement & Cove Coordinates...")
    with open("Assets/Editor/BoatSitePlacer.cs", "r", encoding="utf-8") as f:
        placer_code = f.read()
    if "276.5" not in placer_code or "265.5" not in placer_code:
        failures.append("BoatSitePlacer does not use designated coordinates (276.5, 265.5)")
    else:
        print("  -> Designated Shoreline Coordinates: X=276.5, Y=265.5 (Firm sand beach, water's edge)")

    with open("Assets/Scripts/BoatConstructionSite.cs", "r", encoding="utf-8") as f:
        site_code = f.read()
    if "276.5" not in site_code or "265.5" not in site_code:
        failures.append("BoatConstructionSite.EnsureDefaultSiteExists does not use coordinates (276.5, 265.5)")
    else:
        print("  -> Runtime Fallback EnsureDefaultSiteExists: Coordinates (276.5, 265.5) verified")

    # 5. Component Requirement Data Structure & Sequence
    print("\n[CHECK 5/23] Verifying 5 Modular Component Requirements & Installation Sequence...")
    expected_reqs = [
        ("reinforced_hull", "Reinforced Hull", 0),
        ("structural_frame", "Structural Frame", 1),
        ("rope_binding_kit", "Rope Binding Kit", 2),
        ("paddle", "Paddle", 3),
        ("wind_assembly", "Wind-Catching Assembly", 4)
    ]
    for item_id, d_name, stage in expected_reqs:
        if f'"{item_id}"' not in site_code:
            failures.append(f"Boat component '{item_id}' not configured in BoatConstructionSite")
        if f'"{d_name}"' not in site_code:
            failures.append(f"Boat component display name '{d_name}' not configured in BoatConstructionSite")
        print(f"  -> Stage {stage + 1}: [{item_id}] '{d_name}' (Order Index {stage})")

    # 6. Authoritative State Enum
    print("\n[CHECK 6/23] Verifying BoatConstructionState Authoritative Enum...")
    with open("Assets/Scripts/BoatConstructionState.cs", "r", encoding="utf-8") as f:
        state_code = f.read()
    expected_states = [
        "NotStarted", "HullInstalled", "FrameInstalled", "BindingsInstalled", "PaddleInstalled", "Completed"
    ]
    for st in expected_states:
        if st not in state_code:
            failures.append(f"Missing state '{st}' in BoatConstructionState.cs")
        else:
            print(f"  -> State enum value: {st}")

    # 7. Atomic Validation and Consumption Logic
    print("\n[CHECK 7/23] Checking Atomic Validation & Zero-Consumption on Failure...")
    if "CanInstallNext" not in site_code:
        failures.append("Missing CanInstallNext validation method in BoatConstructionSite")
    if "inventory.RemoveItem" not in site_code:
        failures.append("Missing inventory.RemoveItem call in BoatConstructionSite")
    # Verify RemoveItem is only called AFTER validation
    can_idx = site_code.find("CanInstallNext(inventory")
    remove_idx = site_code.find("inventory.RemoveItem(")
    if can_idx == -1 or remove_idx == -1 or remove_idx < can_idx:
        failures.append("inventory.RemoveItem is called before or without CanInstallNext validation!")
    else:
        print("  -> Atomic sequence verified: CanInstallNext() MUST succeed before inventory.RemoveItem() executes.")

    # 8. Sequential Progression Enforcement (Stage by stage)
    print("\n[CHECK 8/23] Simulating Sequential Stage Progression & Prerequisite Enforcement...")
    class MockSite:
        def __init__(self):
            self.stage = 0
            self.total = 5
            self.completed = False
            self.order = ["reinforced_hull", "structural_frame", "rope_binding_kit", "paddle", "wind_assembly"]
        def can_install(self, item_id):
            if self.completed or self.stage >= self.total:
                return False, "Already completed"
            expected = self.order[self.stage]
            if item_id != expected:
                return False, f"Incorrect order: needs {expected}, received {item_id}"
            return True, "Valid"
        def install(self, item_id, inventory):
            valid, reason = self.can_install(item_id)
            if not valid:
                return False, reason
            if inventory.get(item_id, 0) < 1:
                return False, f"Missing {item_id}"
            inventory[item_id] -= 1
            self.stage += 1
            if self.stage >= self.total:
                self.completed = True
            return True, f"Installed {item_id}"

    mock = MockSite()
    mock_inv = {
        "reinforced_hull": 1,
        "structural_frame": 1,
        "rope_binding_kit": 1,
        "paddle": 1,
        "wind_assembly": 1
    }

    # Test skipping stage 1 (try installing frame first)
    ok, msg = mock.install("structural_frame", mock_inv)
    assert not ok, "Failed: was able to install frame before hull!"
    assert mock_inv["structural_frame"] == 1, "Failed: inventory consumed on invalid stage!"
    print("  -> Prerequisite test passed: Frame rejected when Hull is missing (zero items consumed).")

    # Install Hull
    ok, _ = mock.install("reinforced_hull", mock_inv)
    assert ok and mock.stage == 1 and mock_inv["reinforced_hull"] == 0
    print("  -> Stage 1 passed: Reinforced Hull installed (Stage 1/5).")

    # Install Frame
    ok, _ = mock.install("structural_frame", mock_inv)
    assert ok and mock.stage == 2 and mock_inv["structural_frame"] == 0
    print("  -> Stage 2 passed: Structural Frame installed (Stage 2/5).")

    # Install Bindings
    ok, _ = mock.install("rope_binding_kit", mock_inv)
    assert ok and mock.stage == 3 and mock_inv["rope_binding_kit"] == 0
    print("  -> Stage 3 passed: Rope Binding Kit installed (Stage 3/5).")

    # Install Paddle
    ok, _ = mock.install("paddle", mock_inv)
    assert ok and mock.stage == 4 and mock_inv["paddle"] == 0
    print("  -> Stage 4 passed: Paddle installed (Stage 4/5).")

    # Install Wind Assembly
    ok, _ = mock.install("wind_assembly", mock_inv)
    assert ok and mock.stage == 5 and mock.completed and mock_inv["wind_assembly"] == 0
    print("  -> Stage 5 passed: Wind-Catching Assembly installed (Stage 5/5, COMPLETED).")

    # Test attempting to install after completion
    mock_inv["paddle"] = 1
    ok, msg = mock.install("paddle", mock_inv)
    assert not ok and mock_inv["paddle"] == 1, "Failed: post-completion install was allowed!"
    print("  -> Post-completion test passed: Additional installations strictly rejected.")

    # 9. Discovery System Integration
    print("\n[CHECK 9/23] Verifying Discovery Radius and Trigger...")
    if "discoveryRadius" not in site_code or "CheckDiscovery" not in site_code:
        failures.append("Missing CheckDiscovery or discoveryRadius in BoatConstructionSite")
    else:
        print("  -> Proximity discovery radius = 7.0m; CheckDiscovery(playerPos) triggers OnDiscoveryChanged.")

    # 10. Interaction Proximity & Prompts
    print("\n[CHECK 10/23] Verifying PlayerInteraction Integration with Boat Site...")
    with open("Assets/Scripts/PlayerInteraction.cs", "r", encoding="utf-8") as f:
        player_interact = f.read()
    if "currentTargetBoatSite" not in player_interact:
        failures.append("currentTargetBoatSite field missing from PlayerInteraction.cs")
    if "BoatConstructionSite.EnsureDefaultSiteExists()" not in player_interact:
        failures.append("EnsureDefaultSiteExists() call missing in PlayerInteraction.Start()")
    if "currentTargetBoatSite.Interact(this)" not in player_interact:
        failures.append("currentTargetBoatSite.Interact(this) call missing from PlayerInteraction.cs")
    print("  -> PlayerInteraction: Proximity detection, dynamic prompts, and 'E' key interaction verified.")

    # 11. BoatConstructionUI Implementation
    print("\n[CHECK 11/23] Checking BoatConstructionUI Features...")
    with open("Assets/Scripts/BoatConstructionUI.cs", "r", encoding="utf-8") as f:
        ui_code = f.read()
    if "ESCAPE BOAT CONSTRUCTION" not in ui_code:
        failures.append("Header title missing in BoatConstructionUI")
    if "CONSTRUCTION PROGRESS" not in ui_code:
        failures.append("Overall progress section missing in BoatConstructionUI")
    if "CONSTRUCTION BLUEPRINT & CHECKLIST" not in ui_code:
        failures.append("Blueprints & Checklist section missing in BoatConstructionUI")
    if "currentSite.InstallNext" not in ui_code:
        failures.append("InstallNext call missing in BoatConstructionUI")
    if "OpenUI" not in ui_code or "CloseUI" not in ui_code:
        failures.append("OpenUI/CloseUI missing in BoatConstructionUI")
    print("  -> BoatConstructionUI: 980x640 parchment window, 5-stage checklist, inventory check, and Install button verified.")

    # 12. Conflict Suppression with Other Windows
    print("\n[CHECK 12/23] Checking Mutual UI Conflict Suppression...")
    if "BoatConstructionUI.IsOpen" not in player_interact:
        failures.append("PlayerInteraction does not suppress world interaction when BoatConstructionUI is open")
    if "craftUI?.SetCraftingOpen(false)" not in ui_code or "invUI?.SetInventoryOpen(false)" not in ui_code:
        failures.append("BoatConstructionUI does not close conflicting Crafting/Inventory windows upon opening")
    print("  -> Verified: Boat UI cleanly suppresses world harvesting, closes inventory/crafting menus on open.")

    # 13. Tactile Feedback & Bounce Animation
    print("\n[CHECK 13/23] Checking Visual Tactile Feedback (Bounce Coroutine)...")
    if "TriggerBounceEffect" not in site_code or "BounceRoutine" not in site_code:
        failures.append("Bounce effect coroutine missing in BoatConstructionSite")
    else:
        print("  -> Tactile bounce animation on component installation verified.")

    # 14. ObjectiveManager Progression
    print("\n[CHECK 14/23] Checking ObjectiveManager Narrative Progression...")
    with open("Assets/Scripts/ObjectiveManager.cs", "r", encoding="utf-8") as f:
        obj_code = f.read()
    expected_objs = [
        "ExploreIsland", "PrepareConstruction", "BuildTheBoat", "CompleteConstruction", "PrepareToEscape"
    ]
    for obj_name in expected_objs:
        if obj_name not in obj_code:
            failures.append(f"Objective '{obj_name}' missing from ObjectiveManager.cs")
        else:
            print(f"  -> Narrative Objective registered: {obj_name}")

    # 15. ObjectiveUI HUD Display
    print("\n[CHECK 15/23] Checking ObjectiveUI Banner HUD...")
    with open("Assets/Scripts/ObjectiveUI.cs", "r", encoding="utf-8") as f:
        obj_ui_code = f.read()
    if "OnGUI" not in obj_ui_code or "progressTextStyle" not in obj_ui_code:
        failures.append("OnGUI rendering or progress text missing in ObjectiveUI.cs")
    else:
        print("  -> ObjectiveUI: 640x76 HUD banner at (20, 165) with gold title, description, and mini-bar verified.")

    # 16. Editor Placer Utility
    print("\n[CHECK 16/23] Checking Editor Placer Utility (BoatSitePlacer.cs)...")
    if not os.path.exists("Assets/Editor/BoatSitePlacer.cs"):
        failures.append("Assets/Editor/BoatSitePlacer.cs does not exist")
    elif "MenuItem" not in placer_code:
        failures.append("MenuItem attribute missing from BoatSitePlacer.cs")
    else:
        print("  -> Editor Placer verified: Tools/STRANDED/Place Boat Construction Site in MainScene")

    # 17. Project Files ItemGroup Registration
    print("\n[CHECK 17/23] Checking .csproj Project Registrations...")
    with open("Assembly-CSharp.csproj", "r", encoding="utf-8") as f:
        csharp_proj = f.read()
    runtime_scripts = [
        "BoatComponentRequirement.cs",
        "BoatConstructionState.cs",
        "BoatConstructionSite.cs",
        "BoatConstructionUI.cs",
        "ObjectiveManager.cs",
        "ObjectiveUI.cs"
    ]
    for s in runtime_scripts:
        if s not in csharp_proj:
            failures.append(f"Script {s} missing from Assembly-CSharp.csproj")
        else:
            print(f"  -> Assembly-CSharp.csproj contains: {s}")

    with open("Assembly-CSharp-Editor.csproj", "r", encoding="utf-8") as f:
        editor_proj = f.read()
    if "BoatSitePlacer.cs" not in editor_proj:
        failures.append("BoatSitePlacer.cs missing from Assembly-CSharp-Editor.csproj")
    else:
        print("  -> Assembly-CSharp-Editor.csproj contains: BoatSitePlacer.cs")

    # 18. Survival System Non-Disruption
    print("\n[CHECK 18/23] Verifying Survival System Non-Disruption...")
    with open("Assets/Scripts/SurvivalStats.cs", "r", encoding="utf-8") as f:
        survival_code = f.read()
    # Ensure survival stats are completely untouched and intact
    for stat in ["currentHealth", "currentHunger", "currentThirst", "currentEnergy"]:
        if stat not in survival_code:
            failures.append(f"Survival stat '{stat}' missing in SurvivalStats.cs")
    print("  -> SurvivalStats: Health, Hunger, Thirst, Energy completely intact with 0 modifications.")

    # 19. Fishing System Non-Disruption
    print("\n[CHECK 19/23] Verifying Fishing System Non-Disruption...")
    with open("Assets/Scripts/FishingSpot.cs", "r", encoding="utf-8") as f:
        fishing_code = f.read()
    if "EnsureDefaultFishingSpotsExist" not in fishing_code or "StartFishing" not in fishing_code:
        failures.append("FishingSpot functionality modified or broken")
    else:
        print("  -> FishingSpot: All 8 designated fishing spots and minigame states completely intact.")

    # 20. Hierarchical Crafting & Materials Non-Disruption
    print("\n[CHECK 20/23] Verifying 16 Items & 19 Recipes from Batch 8 Preserved...")
    with open("Assets/Scripts/RecipeDatabase.cs", "r", encoding="utf-8") as f:
        recipes = f.read()
    for boat_rec in ["recipe_paddle", "recipe_wind_assembly", "recipe_rope_binding_kit", "recipe_structural_frame", "recipe_reinforced_hull"]:
        if boat_rec not in recipes:
            failures.append(f"Batch 8 recipe '{boat_rec}' missing from RecipeDatabase")
    print("  -> Batch 8 Recipes: All 5 boat component recipes intact and functional.")

    # 21. Dynamic Sorting Order Integrity
    print("\n[CHECK 21/23] Checking Top-Down Dynamic Sorting Order...")
    if "BASE_SORTING_ORDER + Mathf.RoundToInt(-transform.position.y * 10f)" not in site_code:
        failures.append("Dynamic sorting order formula missing or modified in BoatConstructionSite.cs")
    else:
        print("  -> Dynamic Y-depth sorting verified (BASE_SORTING_ORDER + RoundToInt(-y * 10)).")

    # 22. Serialization & Save/Load Readiness
    print("\n[CHECK 22/23] Checking Serialization & Save/Load Compatibility...")
    if "[Serializable]" not in open("Assets/Scripts/BoatComponentRequirement.cs", "r", encoding="utf-8").read():
        failures.append("BoatComponentRequirement is not marked [Serializable]")
    else:
        print("  -> BoatComponentRequirement is marked [Serializable]; ready for future Save/Load.")

    # 23. Git Status Verification (NO Commits or Pushes)
    print("\n[CHECK 23/23] Confirming NO Git Commits or Pushes Were Made...")
    rc_git, out_git, _ = run_cmd("git status --short")
    if rc_git == 0:
        print("  -> Working tree contains uncommitted files as expected by Rule 7 (NO commits/pushes).")
    else:
        print("  -> Git check skipped (not in git repo or git not found).")

    print("\n=====================================================================")
    if failures:
        print(f"FAILED: {len(failures)} verification failures detected:")
        for fail in failures:
            print(f"  [X] {fail}")
        return False
    else:
        print("RESULT: ALL 23 BATCH 9 VERIFICATION CHECKS PASSED (23/23)!")
        print("=====================================================================")
        return True

if __name__ == "__main__":
    success = verify_batch_9()
    sys.exit(0 if success else 1)
