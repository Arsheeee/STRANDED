# STRANDED — Project Status & Handoff Checkpoint

**Repository:** `https://github.com/Arsheeee/STRANDED.git`  
**Latest Checkpoint Commit:** `9133ff5` ("inventory and hot-tool bar added")  
**Engine:** Unity 6000.5.3f1 (Unity 2D)  
**Input System:** Unity New Input System (with legacy fallbacks)  
**Visual Style:** Warm Stardew Valley pixel-art aesthetic (16x16 tiles/sprites, 44px slots, parchment UI panels)

---

## 1. Completed Batches Summary

### Batch 1: Island Generation, Terrain & Player
* Island procedural generation, autotiling, water animated layers, cliff edges.
* Player movement (WASD/Gamepad), 2D Rigidbody physics, Cinemachine follow camera with bounding clamp.
* Dynamic Y-depth sprite sorting.

### Batch 2: Environmental Resources
* Natural biome placement of environmental resources:
  * Tropical Trees (Wood)
  * Island Rocks / Boulders (Stone)
  * Green Fiber Plants / Vines (Fiber)
  * Berry Bushes (Berries)
  * Coconut Palms / Fallen Coconuts (Coconut)
* `ResourceNode.cs` with interaction triggers, depletion visual states, respawn cooldowns.

### Batch 3: Tool System & Requirements
* `ToolType.cs` enum: `None`, `StoneKnife`, `StoneAxe`, `StonePickaxe`, `FishingRod`.
* Tool requirement validation:
  * Trees require Stone Axe.
  * Rocks require Stone Pickaxe.
  * Fiber requires Stone Knife.
  * Berries & Coconuts gathered with bare hands (`ToolType.None`).
* Rejection feedback toasts ("Requires: Stone Axe").
* Action event hooks `PlayerInteraction.OnToolUsed`.

### Batch 4: Inventory System & Hotbar (COMPLETED)
* **Authoritative Inventory (`Inventory.cs`)**:
  * 36 total slots (12 hotbar slots: indices `0..11`; 24 backpack slots: indices `12..35`).
  * Maximum stack: **99** for primitive resources; **1** for tools (non-stackable).
  * Safe atomic harvesting: `CanAddItem` checked before node depletion. If inventory is full, harvest is cleanly rejected with an "Inventory Full" toast and zero resources lost.
  * Starting test equipment: Slots 0..3 pre-equipped with Stone Axe, Stone Knife, Stone Pickaxe, Fishing Rod.
* **Primitive Items Supported (`ItemDatabase.cs`)**:
  * 6 Resources: `Wood`, `Stone`, `Fiber`, `Berries`, `Coconut`, `Fish`. (Strictly NO metals/iron/ore).
  * 4 Tools: `Stone Knife`, `Stone Axe`, `Stone Pickaxe`, `Fishing Rod`.
* **Hotbar (`HotbarUI.cs`)**:
  * 12 bottom slots with keys `1-9, 0, -, =` and mouse selection.
  * Red/orange highlight on active slot.
  * Clickable `[BAG (I)]` button next to slot 12.
  * Synchronized 1:1 with `PlayerInteraction.EquipTool`.
* **Inventory UI (`InventoryUI.cs`)**:
  * 36-slot window toggled with `I`, `Tab`, or `B`; closes with `Escape` or `[X]` button.
  * Pauses player movement and frees cursor while open.
  * Click-to-pick-up & click-to-swap/merge slots between backpack and hotbar.
  * Hover tooltips with item names and descriptions.
* **Compilation**: `Assembly-CSharp.csproj` builds with **0 errors**.

---

### Batch 5: Crafting System & UI (COMPLETED)
* **Primitive Crafting Engine (`CraftingManager.cs`, `RecipeDatabase.cs`)**:
  * 4 primitive tool recipes: Stone Knife (Stone x2, Fiber x1), Stone Axe (Stone x3, Wood x2, Fiber x1), Stone Pickaxe (Stone x3, Wood x2, Fiber x2), Fishing Rod (Wood x3, Fiber x2).
  * Strictly primitive materials (NO metal/iron/steel/ore).
  * Authoritative, atomic transaction validation (`CanCraft` & `CanFitOutput`). Zero materials consumed if requirements fail.
* **Large Crafting Bench UI (`CraftingUI.cs`)**:
  * 1120x720px warm parchment window toggled with `C` or clicking `[CRAFT [C]]` on hotbar.
  * Recipe list on left with status badges, detailed inspection with live `have / need` material counters on right.
  * Mutual window switching via top tabs with `InventoryUI.cs`.

### Batch 6: Survival System (COMPLETED)
* **Authoritative Survival Stats (`SurvivalStats.cs`)**:
  * 4 primary statistics: Health (100), Hunger (100), Thirst (100), Energy (100).
  * Gradual metabolic depletion over gameplay time (Hunger ~1pt/60s, Thirst ~1pt/45s).
  * Starvation grace period (20s) and dehydration grace period (15s) with interval-based damage (not per frame).
  * Energy consumption on tool harvesting (-8 Energy) with exhaustion safeguards when energy is depleted.
  * Simple resting mechanic (`R` key) recovering +15 energy/sec with auto-stop on full and movement interruption.
* **Food & Drinking System**:
  * Berries: Restores +15 Hunger.
  * Coconut: Restores +20 Hunger, +15 Thirst (coconut water).
  * Raw Fish vs Cooked Fish architecture: Raw fish restores small hunger (+8) with penalty; Cooked Fish architecture prepared.
  * Right-click to consume directly from Hotbar or Inventory; quick consume via `F` key; dedicated `[CONSUME]` button in Inventory window.
  * Full stomach safeguard prevents wasting food when stats are already full.
  * Freshwater interaction: Drinking from `Tilemap_River` restores +25 Thirst.
  * Seawater rejection: Attempting to drink from ocean gives clear feedback: "Salt water is unsafe to drink."
* **Survival HUD & Game Over (`SurvivalHUD.cs`)**:
  * Dedicated 4-bar pixel-art HUD in bottom-right corner (HP, Hunger, Thirst, Energy) without obstructing the hotbar.
  * Clear resting banner feedback.
  * Full Game Over screen on death (0 HP) with cause-of-death breakdown and `[RESPAWN AT CAMP]` restoring full stats and position cleanly without scene reloads.
* **Compilation**: `Assembly-CSharp.csproj` builds with **0 errors**.

---

### Batch 7: Fishing System (COMPLETED)
* **Dedicated Fishing Spots (`FishingSpot.cs`, `FishingSpotPlacer.cs`)**:
  * 8 designated fishing locations along existing riverbanks and coastal shorelines (4 riverbank spots, 4 coastal spots).
  * Player stands on valid dry ground near water; no deep water traversal required.
  * Subtle animated visual indicators: pulsing concentric water ripples, floating retro red-and-white bobber, and bouncy `!` alert icon.
  * Reusable `FishingSpot` component with configurable wait duration (2.0s - 4.5s) and reaction window (1.6s).
* **Fishing Interaction & Sequence (`PlayerInteraction.cs`)**:
  * Requires equipped `ToolType.FishingRod` (Slot 4 / Key '4').
  * Clear rejection message if wrong tool or no tool equipped (`"Requires Fishing Rod to fish."`).
  * Approach spot -> Press `E` to cast -> Waiting period -> `! FISH ON THE LINE!` bite notification -> Press `E` within reaction window to reel in -> Awards `Raw Fish`.
  * Missing the reaction window fails the catch cleanly (`"The fish got away!"`).
  * Cancelling by moving away (> 2.2f) or opening inventory/crafting cleanly resets the spot to Idle.
  * Exhaustion safeguard: Requires stamina to fish; exhausts when stamina < 8.
  * Anti-spam protection: Atomic state locking prevents multiple fish awards from a single attempt.
* **Inventory & Survival Integration**:
  * Awards `Raw Fish` (`ResourceType.Fish` / item ID `"fish"`) with 99 max stack into existing authoritative inventory.
  * Safe full-bag handling: If inventory is full, catches are not consumed or lost without informing player (`"Inventory full! Cannot carry fish."`).
  * Connects to `SurvivalStats.TryConsumeItem`: Raw fish functions as raw food (+8 Hunger, -2 Health raw food penalty, +2 Energy), distinct from future cooked fish.
* **Testing & Compilation**:
  * Both `Assembly-CSharp.csproj` and `Assembly-CSharp-Editor.csproj` build with **0 errors**.
  * 15/15 automated tests passed with 100% success (`verify_batch7_fishing_system.py`).
  * Zero regressions across Batch 4, Batch 5, and Batch 6 test suites.

---

## Batch 8: Hierarchical Crafting — Special Materials and Boat Components (COMPLETED)
* **Hierarchical Crafting Architecture**:
  * Implemented strict 4-tier crafting progression:
    * Tier 1: Primitive Tools (`Stone Knife`, `Stone Axe`, `Stone Pickaxe`, `Fishing Rod`)
    * Tier 2: Advanced Equipment (`Improved Cutting Knife`, `Wooden Mallet`, `Fiber Twisting Tool`, `Weaving Frame`)
    * Tier 3: Processed Materials (`Shaped Wooden Parts`, `Wooden Pegs`, `Strong Rope`, `Reinforced Rope`, `Woven Sailcloth`, `Reinforced Wooden Joints`)
    * Tier 4: Boat Components (`Paddle`, `Wind-Catching Assembly`, `Rope Binding Kit`, `Structural Frame`, `Reinforced Hull`)
  * **Strict Scope Compliance**: ZERO Stone Chisel, ZERO metal/iron/steel/ore, ZERO world regeneration.
* **Special Gathering Resource: Vines**:
  * Added `ResourceType.Vines` yielding `vines` item (stackable to 99).
  * Harvested using `Stone Knife` or `Improved Cutting Knife`.
  * Integrated non-destructively in `MainScene.unity` with `Assets/Editor/VineResourcePlacer.cs` and runtime fallback `ResourceNode.EnsureDefaultVineNodesExist()`.
* **Prerequisite Equipment & Station System**:
  * `CraftingRecipe.cs` enhanced with `RequiredTool`, `RequiredToolType`, and `RequiredStation` properties.
  * `CraftingManager.CanCraft` validates tool and station presence in player inventory without consuming them during craft.
  * Atomic transactions with capacity pre-checks guarantee zero ingredient loss on inventory overflow.
* **Enhanced Crafting UI (`CraftingUI.cs`)**:
  * Modeled with warm Stardew Valley parchment aesthetics.
  * Added category filter tabs: `[ALL]`, `[TOOLS]`, `[MATERIALS]`, `[BOAT]`.
  * Added `GUI.BeginScrollView` scrollable recipe list supporting dozens of recipes without clipping.
  * Displays tool prerequisite badges, station status, item yield, and real-time inventory count tracking.
* **Pixel Art Assets**:
  * Generated 16 custom 16x16 pixel-art sprites and Unity metadata:
    * `item_vines.png`, `tool_improved_knife.png`, `tool_wooden_mallet.png`, `tool_fiber_twister.png`, `tool_weaving_frame.png`
    * `item_shaped_wood.png`, `item_wooden_pegs.png`, `item_strong_rope.png`, `item_reinforced_rope.png`, `item_woven_sailcloth.png`, `item_reinforced_joints.png`
    * `item_paddle.png`, `item_wind_assembly.png`, `item_rope_binding_kit.png`, `item_structural_frame.png`, `item_reinforced_hull.png`
    * `plant_vine_bush.png`, `plant_vine_depleted.png`
* **Verification & Regression Testing**:
  * Both `Assembly-CSharp.csproj` and `Assembly-CSharp-Editor.csproj` compile with **0 errors**.
  * 29/29 Batch 8 verification tests passed (`verify_batch8_hierarchical_crafting.py`).
  * 100% pass on regression suites for Batch 4 (Inventory), Batch 5 (Crafting), Batch 6 (Survival), and Batch 7 (Fishing).
  * Strict Directed Acyclic Graph (DAG) verified with 0 cycles; all boat components resolve to primitive island resources.

---

## Batch 9: Boat Construction & Objective Progression (COMPLETED)
* **Authoritative Construction Site (`BoatConstructionSite.cs`)**:
  * Established at the designated northeastern escape cove at shoreline coordinates `(276.5, 265.5, 0)`.
  * Positioned on firm sand beach at the water's edge, reachable on foot, completely dry, preserving all existing terrain and resources.
  * Modular data-driven requirement model (`BoatComponentRequirement.cs`) supporting item IDs, display names, order, and quantities.
  * Authoritative state machine (`BoatConstructionState.cs`): `NotStarted`, `HullInstalled`, `FrameInstalled`, `BindingsInstalled`, `PaddleInstalled`, `Completed`.
  * Sequential prerequisite enforcement: Stages strictly validate previous installation (Stage 1: Hull -> Stage 2: Frame -> Stage 3: Bindings -> Stage 4: Paddle -> Stage 5: Wind Assembly). Skipping or re-installing is prevented.
  * Atomic validation & zero consumption: `CanInstallNext` checks component and quantity before deducting from inventory. Failed attempts consume zero items.
  * Proximity discovery trigger within 7.0m with toast notification; interaction within 3.2m.
  * Tactile bounce animation on component installation (`transform.localScale` pulse coroutine).
  * Runtime fallback `EnsureDefaultSiteExists()` + Editor menu tool (`Tools > STRANDED > Place Boat Construction Site in MainScene`).
* **Progressive Visual Evolution**:
  * 6 custom 32x32 pixel-art sprites with point filtering and metadata (`Assets/Art/Environment/Boat/`):
    * `boat_stage_0_slipway.png`: Log cradle and launch skids on sand.
    * `boat_stage_1_hull.png`: Outrigger hull seated on cradle.
    * `boat_stage_2_frame.png`: Timber ribs and gunwale stringers.
    * `boat_stage_3_bindings.png`: Reinforced rope lashings securing framing.
    * `boat_stage_4_paddle.png`: Stowed wooden canoe paddle along starboard gunwale.
    * `boat_stage_5_completed.png`: Stepped mast, cross spar, stay lines, and hoisted woven sail.
  * Dynamic Y-depth sorting order (`BASE_SORTING_ORDER + RoundToInt(-y * 10)`).
* **Interactive Construction UI (`BoatConstructionUI.cs`)**:
  * 980x640px warm parchment interface following Stardew Valley aesthetic.
  * Overall progress bar banner showing percentage and completed stages (e.g. `2 / 5 STAGES COMPLETED (40%)`).
  * Left Column: 5-stage blueprint checklist with dynamic status badges (`[INSTALLED]`, `[NEXT] In Bag: have/need`, `[LOCKED]`).
  * Right Column: Active stage details, component lore, inventory requirement check, and primary action button (`INSTALL ... (PRESS E)`).
  * Post-completion seaworthiness inspection view.
  * Mutual conflict suppression: Closing on Escape/E/C or player departure; closes conflicting inventory and crafting menus upon opening.
* **Objective Progression System (`ObjectiveManager.cs`, `ObjectiveUI.cs`)**:
  * Authoritative narrative tracking with 5 sequential objectives:
    * Objective 1: `Explore the Island` (Discover the northeastern escape cove).
    * Objective 2: `Prepare for Construction` (Manufacture boat components using hierarchical crafting).
    * Objective 3: `Build the Escape Boat` (Install next component at the slipway with live stage counter).
    * Objective 4: `Boat Construction Complete` (All 5 components assembled).
    * Objective 5: `Prepare to Escape` (Vessel is seaworthy; ready for future launch).
  * Lightweight 640x76px Stardew-style HUD banner positioned cleanly at `(20, 165)` below the inventory tracker.
  * Gold header, active instruction text, live stage counter, and progress mini-bar.
  * Auto-suppressed during full modal windows (Inventory, Crafting, Boat UI) to prevent visual clutter; optional `O` key toggle.
* **Strict Scope Compliance**:
  * ZERO final escape sequence or victory cutscenes (reserved for Batch 10).
  * ZERO save/load framework (clean serializable architecture maintained).
  * ZERO metals/iron/steel/ore, ZERO Stone Chisel, ZERO terrain changes or world regeneration.
  * ZERO automatic Git commits or pushes.
* **Testing & Compilation**:
  * Both `Assembly-CSharp.csproj` and `Assembly-CSharp-Editor.csproj` compile with **0 errors**.
  * 23/23 automated Batch 9 verification checks passed (`verify_batch9_boat_construction.py`).
  * 100% pass on regression suites across Batch 3 (Tools), Batch 4 (Inventory), Batch 5 (Crafting), Batch 6 (Survival), Batch 7 (Fishing), and Batch 8 (Hierarchical Crafting).

---


## Batch 10: Boat Launch & Escape Ending (COMPLETED)
* **Boat Launch Validation & Interaction (`BoatConstructionSite.cs`, `BoatConstructionUI.cs`, `PlayerInteraction.cs`)**:
  * Authoritative launch validation: `TryLaunch()` strictly validates that `IsComplete == true` (all 5 stages assembled) before initiating departure.
  * Incomplete boat protection: Attempting to launch an incomplete vessel is strictly rejected with a clear notification toast: `"Cannot launch: Boat construction is incomplete!"`.
  * Dynamic world interaction: Standing near the completed boat updates the interaction HUD prompt to `[E] Launch Escape Boat (Set Sail)`.
  * Boat UI integration: Inspection screen provides a prominent green `[LAUNCH ESCAPE BOAT (SET SAIL)]` action button alongside `[CLOSE SHIPYARD INSPECTION]`.
  * Single-trigger enforcement: `hasLaunched` guard and state machine prevent duplicate launch triggers.
* **Departure Sequence (`EscapeEndingController.cs`)**:
  * Short, polished ~2.8s departure sequence with zero external heavy animation/cutscene dependencies.
  * Exploration camera smoothly shifts focus to the departing boat (`ExplorationCamera.SetTarget`).
  * Player boards the vessel, dynamically adjusting position and Y-sorting order.
  * Vessel gently sails outward toward open ocean water (`sailDirection * sailSpeed * Time.deltaTime`).
  * Smooth oceanic screen fade (0.0 to 1.0 alpha) with contextual subtitle `"Setting sail for freedom..."`.
  * Input & gameplay protection: Player movement and world interaction disabled during departure; survival metabolic depletion halted.
* **Warm Stardew-Style Victory Screen (`EscapeEndingController.cs`)**:
  * Deep oceanic backdrop with subtle ambient star particles.
  * Centered 640x450px parchment modal dialog with dark wood border trim.
  * Prominent golden title: `"YOU ESCAPED!"`.
  * Narrative subtitle: `"You survived the island and built your way to freedom."`.
  * Journey summary card: Displays elapsed survival time (e.g. `06:42`), 5/5 components assembled, and narrative victory lore.
  * Action buttons:
    * `[RESTART GAME]`: Reloads active scene via `SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex)`, restoring fresh playable state.
    * `[RETURN TO MAIN MENU]`: Safely routes to main menu or reloads active scene if running single-scene.
* **Developer Testing Shortcut (F8)**:
  * Non-intrusive F8 key handler active strictly inside `#if UNITY_EDITOR || DEVELOPMENT_BUILD`.
  * Automatically fast-completes all 5 boat stages and triggers the real departure sequence for fast testing.
  * Completely stripped from release builds.
* **Testing & Compilation**:
  * Both `Assembly-CSharp.csproj` and `Assembly-CSharp-Editor.csproj` compile with **0 errors**.
  * 12/12 automated Batch 10 verification checks passed (`verify_batch10_boat_launch_ending.py`).
  * 100% regression pass across all 9 project test suites (Batches 3, 4, 5, 6, 7, 8, 9, Vine Gathering, and Batch 10).
  * Strictly NO Git commits or pushes executed.

---

## Batch 11: Save & Load System (COMPLETED)
* **Authoritative Serializable Data Model (`SaveData.cs`)**:
  * Versioned root schema (`version = 1`, `timestamp`) ensuring backwards/forwards compatibility.
  * Coordinates: Player position (`playerX`, `playerY`, `playerZ`).
  * Inventory: Full 36-slot inventory array (`InventorySaveSlot[]`) saving slot indices, item IDs, and stack counts.
  * Survival Stats: Health, Hunger, Thirst, Energy vitals.
  * Narrative Progression: Active objective enum, cove discovery flag, escape state flag.
  * Boat Construction: Active stage index, construction state enum, site discovery flag, and installed component IDs list.
* **Save Manager Architecture (`SaveManager.cs`)**:
  * Centralized controller saving to `Application.persistentDataPath/stranded_save.json`.
  * Safe file operations: Atomic JSON serialization via `JsonUtility` and atomic file write with temporary file backup.
  * Robust deserialization & resilience:
    * Missing save detection with graceful fallback.
    * Corrupted JSON detection with try-catch and descriptive logging without crashing.
    * Incompatible schema version validation (gracefully warns and rejects unsupported future schemas).
    * Unknown / removed item ID tolerance: Skips deprecated or unrecognized item IDs during slot restoration without throwing exceptions.
  * Strict restoration order:
    1. Restore player Transform, Rigidbody2D, and ExplorationCamera clamping/snapping.
    2. Clear inventory completely to eliminate item duplication, then restore all 36 slots matching serialized item IDs.
    3. Restore and clamp survival stats within `[0, Max]` bounds.
    4. Restore narrative objective state and HUD banner.
    5. Restore boat construction visual stage, state machine, and installed components.
  * Shortcuts & guards:
    * `F5`: Quick save with toast confirmation.
    * `F9`: Quick load with toast confirmation.
    * Focus guards: Shortcuts ignored while player has focus in text fields/keyboard input.
    * Victory guards: Shortcuts ignored during the boat launch departure sequence and victory screen.
  * Fresh New Game guarantee:
    * Scene startup / restarts do NOT automatically load existing save files; loading is strictly explicit via `[LOAD GAME]` button or `F9`.
* **Inventory UI Integration (`InventoryUI.cs`)**:
  * Warm Stardew Valley parchment bottom card panel integrating:
    * `[SAVE GAME (F5)]`: Prominent button triggering immediate game state capture.
    * `[LOAD GAME (F9)]`: Prominent button dynamically disabled (`GUI.enabled = hasSave`) when no save file exists.
    * Timestamp banner displaying the last saved date and time (e.g. `Saved: 2026-10-12 04:30:15`).
  * Clean UI layout without disrupting hotbar, backpack slots, or crafting tabs.
* **Testing & Compilation**:
  * Both `Assembly-CSharp.csproj` and `Assembly-CSharp-Editor.csproj` compile with **0 errors**.
  * 14/14 automated Batch 11 verification checks passed (`verify_batch11_save_load_system.py`).
  * 100% pass on regression suites across all 10 project test suites (Batches 3 through 11).
  * Strictly NO Git commits or pushes executed.

---

## 2. Project Milestone: Playable Game Complete with Full Persistence
The complete loop of STRANDED is now fully realized with robust persistence: player movement, resource gathering, hierarchical crafting, survival vitals, fishing, narrative objectives, boat building, launch & escape ending, and reliable JSON-based save & load!


