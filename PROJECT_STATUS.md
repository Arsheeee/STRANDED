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

## 2. Next Batch: Batch 5 (Crafting System)

When you start the new session on your new account:
1. Tell the assistant:
   > "I am continuing work on STRANDED. Please read `PROJECT_STATUS.md` first. Batches 1 to 4 are already finished. We are now working on Batch 5."
2. Provide your instructions for Batch 5 (Crafting System).
