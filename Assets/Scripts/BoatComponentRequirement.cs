using System;
using UnityEngine;

/// <summary>
/// Modular data definition for a component required during boat construction in STRANDED.
/// Configurable and extensible so required components, quantities, and order can be tuned without rewriting logic.
/// </summary>
[Serializable]
public class BoatComponentRequirement
{
    [SerializeField] private string componentItemId;
    [SerializeField] private string displayName;
    [SerializeField] private int requiredQuantity = 1;
    [SerializeField] private int stageIndex;
    [SerializeField] private string description;

    public string ComponentItemId => componentItemId;
    public string DisplayName => displayName;
    public int RequiredQuantity => requiredQuantity;
    public int StageIndex => stageIndex;
    public string Description => description;

    public BoatComponentRequirement(string componentItemId, string displayName, int requiredQuantity, int stageIndex, string description)
    {
        this.componentItemId = componentItemId;
        this.displayName = displayName;
        this.requiredQuantity = requiredQuantity;
        this.stageIndex = stageIndex;
        this.description = description;
    }
}
