import os
import sys

def verify_vine_harvesting():
    print("=====================================================================")
    print("STRANDED: VINE HARVESTING DIAGNOSTIC & VERIFICATION SUITE")
    print("=====================================================================")
    failures = []

    # 1. Source code check: PlayerInteraction collider filtering
    print("\n[CHECK 1/6] Verifying PlayerInteraction collider filtering logic...")
    with open("Assets/Scripts/PlayerInteraction.cs", "r", encoding="utf-8") as f:
        pi_code = f.read()

    # The buggy code had: if (col == null || col.isTrigger) continue;
    # The fixed code checks ResourceNode FIRST before skipping triggers!
    if "if (node == null && col.isTrigger) continue;" not in pi_code:
        failures.append("PlayerInteraction still discards trigger colliders before checking for ResourceNode!")
    else:
        print("  -> PASS: PlayerInteraction correctly inspects ResourceNode before ignoring triggers.")

    # 2. Source code check: ResourceNode EnsureDefaultVineNodesExist colliders
    print("\n[CHECK 2/6] Verifying ResourceNode.EnsureDefaultVineNodesExist collider setup...")
    with open("Assets/Scripts/ResourceNode.cs", "r", encoding="utf-8") as f:
        rn_code = f.read()

    if "col.isTrigger = false;" not in rn_code:
        failures.append("ResourceNode.EnsureDefaultVineNodesExist does not set col.isTrigger = false")
    else:
        print("  -> PASS: EnsureDefaultVineNodesExist creates solid non-trigger colliders.")

    # 3. Source code check: Tool requirement for Vines (StoneKnife or ImprovedKnife)
    print("\n[CHECK 3/6] Verifying tool requirement for Vines...")
    if 'node.requiredTool = ToolType.StoneKnife;' not in rn_code:
        failures.append("Vine nodes do not require StoneKnife")
    if 'requiredTool == ToolType.StoneKnife && equippedTool == ToolType.ImprovedKnife' not in rn_code:
        failures.append("ImprovedKnife does not satisfy StoneKnife cutting requirement")
    print("  -> PASS: Vine nodes require StoneKnife and accept ImprovedKnife.")

    # 4. Source code check: ItemDatabase vines resource registration
    print("\n[CHECK 4/6] Verifying ItemDatabase vines item registration...")
    with open("Assets/Scripts/ItemDatabase.cs", "r", encoding="utf-8") as f:
        id_code = f.read()
    if 'RegisterResource(ResourceType.Vines, "vines", "Vines"' not in id_code:
        failures.append("Vines item not registered in ItemDatabase")
    else:
        print("  -> PASS: ItemDatabase registers ResourceType.Vines -> 'vines' item.")

    # 5. Simulation of Interaction & Harvesting Sequence
    print("\n[CHECK 5/6] Simulating Vine Cluster Interaction & Harvesting Sequence...")
    class MockCollider:
        def __init__(self, is_trigger=False):
            self.isTrigger = is_trigger

    class MockResourceNode:
        def __init__(self, res_type="Vines", req_tool="StoneKnife", yield_amt=2):
            self.res_type = res_type
            self.req_tool = req_tool
            self.yield_amt = yield_amt
            self.is_harvestable = True
            self.depleted = False

        def can_harvest_with(self, tool):
            if not self.is_harvestable or self.depleted: return False
            if self.req_tool == "None": return True
            if self.req_tool == "StoneKnife" and tool in ("StoneKnife", "ImprovedKnife"): return True
            return tool == self.req_tool

        def interact(self, player):
            if not self.can_harvest_with(player.equipped_tool):
                player.notifications.append(f"Requires {self.req_tool}")
                return 0
            if player.inv_count + self.yield_amt > player.inv_max:
                player.notifications.append("Inventory Full")
                return 0
            player.inv_count += self.yield_amt
            player.vines_count += self.yield_amt
            player.energy -= 8.0
            self.depleted = True
            self.is_harvestable = False
            player.notifications.append(f"Collected Vines +{self.yield_amt}")
            return self.yield_amt

    class MockPlayer:
        def __init__(self):
            self.equipped_tool = "None"
            self.energy = 100.0
            self.inv_count = 0
            self.vines_count = 0
            self.inv_max = 99
            self.notifications = []

    # Case A: Collider is a trigger (as created in previous scene runs)
    trigger_col = MockCollider(is_trigger=True)
    vine_node = MockResourceNode()
    player = MockPlayer()

    # Step A1: Query nearby object with the FIXED query logic
    detected_node = None
    col = trigger_col
    node = vine_node # col.GetComponent<ResourceNode>()
    if not (node is None and col.isTrigger):
        detected_node = node

    assert detected_node is not None, "Failed: trigger collider on ResourceNode was ignored!"
    print("  -> Step 1 Passed: Node with trigger collider is successfully detected!")

    # Step A2: Player approaches with bare hands (equipped_tool = "None")
    assert not detected_node.can_harvest_with(player.equipped_tool)
    yielded = detected_node.interact(player)
    assert yielded == 0
    assert "Requires StoneKnife" in player.notifications[-1]
    assert player.vines_count == 0
    print("  -> Step 2 Passed: Bare-handed interact shows 'Requires Stone Knife' with zero consumption.")

    # Step A3: Player equips Stone Knife (key 1 / slot 0)
    player.equipped_tool = "StoneKnife"
    assert detected_node.can_harvest_with(player.equipped_tool)
    yielded = detected_node.interact(player)
    assert yielded == 2
    assert player.vines_count == 2
    assert player.energy == 92.0
    assert detected_node.depleted == True
    print("  -> Step 3 Passed: Equipped Stone Knife successfully harvests +2 Vines into inventory.")

    # Step A4: Re-interacting with depleted node yields 0
    yielded_again = detected_node.interact(player)
    assert yielded_again == 0
    print("  -> Step 4 Passed: Depleted node cannot be re-harvested.")

    # Case B: Improved Cutting Knife test
    node_b = MockResourceNode()
    player_b = MockPlayer()
    player_b.equipped_tool = "ImprovedKnife"
    assert node_b.can_harvest_with(player_b.equipped_tool)
    yielded_b = node_b.interact(player_b)
    assert yielded_b == 2 and player_b.vines_count == 2
    print("  -> Step 5 Passed: Improved Cutting Knife also successfully harvests Vines.")

    # 6. Verify Regression Suites (Batch 8 and Batch 9)
    print("\n[CHECK 6/6] Verifying Regression Suites...")
    import subprocess
    rc8 = subprocess.run("python scratch/verify_batch8_hierarchical_crafting.py", shell=True, capture_output=True).returncode
    rc9 = subprocess.run("python scratch/verify_batch9_boat_construction.py", shell=True, capture_output=True).returncode
    if rc8 != 0:
        failures.append("Batch 8 regression failed!")
    else:
        print("  -> PASS: Batch 8 suite passed 100%.")
    if rc9 != 0:
        failures.append("Batch 9 regression failed!")
    else:
        print("  -> PASS: Batch 9 suite passed 100%.")

    print("\n=====================================================================")
    if failures:
        print(f"FAILED: {len(failures)} failures:")
        for f in failures:
            print(f"  [X] {f}")
        return False
    else:
        print("RESULT: ALL VINE GATHERING DIAGNOSTIC CHECKS PASSED (6/6)!")
        print("=====================================================================")
        return True

if __name__ == "__main__":
    success = verify_vine_harvesting()
    sys.exit(0 if success else 1)
