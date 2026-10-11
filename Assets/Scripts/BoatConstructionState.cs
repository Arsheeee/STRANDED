/// <summary>
/// Authoritative state progression for escape boat construction in STRANDED.
/// </summary>
public enum BoatConstructionState
{
    NotStarted = 0,         // Slipway cradle placed, ready for hull
    HullInstalled = 1,      // Stage 1: Reinforced Hull installed
    FrameInstalled = 2,     // Stage 2: Structural Frame installed
    BindingsInstalled = 3,  // Stage 3: Rope Binding Kit installed
    PaddleInstalled = 4,    // Stage 4: Paddle installed
    Completed = 5           // Stage 5: Wind-Catching Assembly installed; Construction Complete!
}
