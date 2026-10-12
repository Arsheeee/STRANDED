using System;
using UnityEngine;

/// <summary>
/// Authoritative Audio Manager for STRANDED (Batch 12).
/// Manages player footsteps, resource gathering, item collection, crafting,
/// fishing, boat construction, victory fanfare, and UI feedback.
/// Supports both Inspector-assigned audio clips and procedural retro waveform fallbacks.
/// </summary>
public class AudioManager : MonoBehaviour
{
    private static AudioManager instance;
    public static AudioManager Instance => instance;

    [Header("Volume Settings")]
    [Range(0f, 1f)] [SerializeField] private float masterVolume = 1.0f;
    [Range(0f, 1f)] [SerializeField] private float sfxVolume = 0.85f;
    [Range(0f, 1f)] [SerializeField] private float footstepVolume = 0.45f;
    [Range(0f, 1f)] [SerializeField] private float musicVolume = 0.60f;

    [Header("Audio Clips (Optional Inspector Assignment)")]
    [SerializeField] private AudioClip footstepClip;
    [SerializeField] private AudioClip waterFootstepClip;
    [SerializeField] private AudioClip gatherWoodClip;
    [SerializeField] private AudioClip gatherStoneClip;
    [SerializeField] private AudioClip gatherPlantClip;
    [SerializeField] private AudioClip itemCollectClip;
    [SerializeField] private AudioClip craftSuccessClip;
    [SerializeField] private AudioClip craftFailClip;
    [SerializeField] private AudioClip buttonClickClip;
    [SerializeField] private AudioClip fishBiteClip;
    [SerializeField] private AudioClip fishCatchClip;
    [SerializeField] private AudioClip boatBuildClip;
    [SerializeField] private AudioClip boatLaunchClip;
    [SerializeField] private AudioClip victoryClip;
    [SerializeField] private AudioClip saveSuccessClip;
    [SerializeField] private AudioClip loadSuccessClip;

    // Dedicated AudioSource channels
    private AudioSource sfxSource;
    private AudioSource footstepSource;
    private AudioSource uiSource;
    private AudioSource musicSource;

    // Anti-Spam / Rate Limiting Cooldowns
    private float lastFootstepTime = -1f;
    private float lastGatherTime = -1f;
    private float lastClickTime = -1f;
    private const float MIN_FOOTSTEP_INTERVAL = 0.32f;
    private const float MIN_GATHER_INTERVAL = 0.08f;
    private const float MIN_CLICK_INTERVAL = 0.04f;

    // Public Volume Properties
    public float MasterVolume
    {
        get => masterVolume;
        set
        {
            masterVolume = Mathf.Clamp01(value);
            UpdateSourceVolumes();
        }
    }

    public float SfxVolume
    {
        get => sfxVolume;
        set
        {
            sfxVolume = Mathf.Clamp01(value);
            UpdateSourceVolumes();
        }
    }

    public float FootstepVolume
    {
        get => footstepVolume;
        set
        {
            footstepVolume = Mathf.Clamp01(value);
            UpdateSourceVolumes();
        }
    }

    public float MusicVolume
    {
        get => musicVolume;
        set
        {
            musicVolume = Mathf.Clamp01(value);
            UpdateSourceVolumes();
        }
    }

    void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(gameObject);
            return;
        }

        instance = this;
        DontDestroyOnLoad(gameObject);

        InitializeAudioSources();
        GenerateProceduralFallbacks();
    }

    private void InitializeAudioSources()
    {
        sfxSource = CreateChildSource("SFX_Channel");
        footstepSource = CreateChildSource("Footstep_Channel");
        uiSource = CreateChildSource("UI_Channel");
        musicSource = CreateChildSource("Music_Channel");
        musicSource.loop = true;

        UpdateSourceVolumes();
    }

    private AudioSource CreateChildSource(string channelName)
    {
        GameObject child = new GameObject(channelName);
        child.transform.SetParent(transform);
        AudioSource src = child.AddComponent<AudioSource>();
        src.playOnAwake = false;
        src.spatialBlend = 0f; // 2D flat sound
        return src;
    }

    private void UpdateSourceVolumes()
    {
        if (sfxSource != null) sfxSource.volume = masterVolume * sfxVolume;
        if (footstepSource != null) footstepSource.volume = masterVolume * footstepVolume;
        if (uiSource != null) uiSource.volume = masterVolume * sfxVolume;
        if (musicSource != null) musicSource.volume = masterVolume * musicVolume;
    }

    /// <summary>
    /// Ensures a persistent AudioManager singleton exists in the scene.
    /// </summary>
    public static void EnsureExists()
    {
        if (instance == null)
        {
            var existing = FindAnyObjectByType<AudioManager>();
            if (existing != null)
            {
                instance = existing;
            }
            else
            {
                GameObject obj = new GameObject("AudioManager");
                instance = obj.AddComponent<AudioManager>();
            }
        }
    }

    // =========================================================================
    // PUBLIC AUDIO PLAYBACK API
    // =========================================================================

    public void PlayFootstep(bool isWater = false)
    {
        float interval = isWater ? 0.44f : MIN_FOOTSTEP_INTERVAL;
        if (Time.time - lastFootstepTime < interval) return;
        lastFootstepTime = Time.time;

        if (isWater)
        {
            AudioClip clip = waterFootstepClip != null ? waterFootstepClip : footstepClip;
            if (clip != null && footstepSource != null)
            {
                footstepSource.pitch = UnityEngine.Random.Range(0.82f, 1.12f);
                footstepSource.PlayOneShot(clip, masterVolume * footstepVolume * 0.85f);
            }
        }
        else if (footstepClip != null && footstepSource != null)
        {
            footstepSource.pitch = UnityEngine.Random.Range(0.92f, 1.08f);
            footstepSource.PlayOneShot(footstepClip, masterVolume * footstepVolume);
        }
    }

    public void PlayResourceGather(ResourceType type)
    {
        if (Time.time - lastGatherTime < MIN_GATHER_INTERVAL) return;
        lastGatherTime = Time.time;

        AudioClip clipToPlay;
        switch (type)
        {
            case ResourceType.Wood:
                clipToPlay = gatherWoodClip;
                break;
            case ResourceType.Stone:
                clipToPlay = gatherStoneClip;
                break;
            case ResourceType.Fiber:
            case ResourceType.Vines:
            case ResourceType.Berries:
            case ResourceType.Coconut:
            default:
                clipToPlay = gatherPlantClip;
                break;
        }

        if (clipToPlay != null && sfxSource != null)
        {
            sfxSource.pitch = UnityEngine.Random.Range(0.92f, 1.08f);
            sfxSource.PlayOneShot(clipToPlay, masterVolume * sfxVolume);
        }
    }

    public void PlayItemCollect()
    {
        if (itemCollectClip != null && sfxSource != null)
        {
            sfxSource.pitch = UnityEngine.Random.Range(0.97f, 1.03f);
            sfxSource.PlayOneShot(itemCollectClip, masterVolume * sfxVolume * 0.9f);
        }
    }

    public void PlayCraftSuccess()
    {
        if (craftSuccessClip != null && sfxSource != null)
        {
            sfxSource.pitch = 1.0f;
            sfxSource.PlayOneShot(craftSuccessClip, masterVolume * sfxVolume);
        }
    }

    public void PlayCraftFail()
    {
        if (craftFailClip != null && sfxSource != null)
        {
            sfxSource.pitch = 1.0f;
            sfxSource.PlayOneShot(craftFailClip, masterVolume * sfxVolume * 0.85f);
        }
    }

    public void PlayButtonClick()
    {
        if (Time.time - lastClickTime < MIN_CLICK_INTERVAL) return;
        lastClickTime = Time.time;

        if (buttonClickClip != null && uiSource != null)
        {
            uiSource.pitch = UnityEngine.Random.Range(0.98f, 1.02f);
            uiSource.PlayOneShot(buttonClickClip, masterVolume * sfxVolume * 0.75f);
        }
    }

    public void PlayFishBite()
    {
        if (fishBiteClip != null && sfxSource != null)
        {
            sfxSource.pitch = 1.0f;
            sfxSource.PlayOneShot(fishBiteClip, masterVolume * sfxVolume);
        }
    }

    public void PlayFishCatch()
    {
        if (fishCatchClip != null && sfxSource != null)
        {
            sfxSource.pitch = 1.0f;
            sfxSource.PlayOneShot(fishCatchClip, masterVolume * sfxVolume);
        }
    }

    public void PlayBoatBuild()
    {
        if (boatBuildClip != null && sfxSource != null)
        {
            sfxSource.pitch = UnityEngine.Random.Range(0.96f, 1.04f);
            sfxSource.PlayOneShot(boatBuildClip, masterVolume * sfxVolume);
        }
    }

    public void PlayBoatLaunch()
    {
        if (boatLaunchClip != null && sfxSource != null)
        {
            sfxSource.pitch = 1.0f;
            sfxSource.PlayOneShot(boatLaunchClip, masterVolume * sfxVolume);
        }
    }

    public void PlayVictory()
    {
        if (victoryClip != null && sfxSource != null)
        {
            sfxSource.pitch = 1.0f;
            sfxSource.PlayOneShot(victoryClip, masterVolume * sfxVolume);
        }
    }

    public void PlaySaveSuccess()
    {
        if (saveSuccessClip != null && uiSource != null)
        {
            uiSource.pitch = 1.05f;
            uiSource.PlayOneShot(saveSuccessClip, masterVolume * sfxVolume * 0.8f);
        }
    }

    public void PlayLoadSuccess()
    {
        if (loadSuccessClip != null && uiSource != null)
        {
            uiSource.pitch = 0.98f;
            uiSource.PlayOneShot(loadSuccessClip, masterVolume * sfxVolume * 0.8f);
        }
    }

    public void PlayInventoryOpen()
    {
        PlayButtonClick();
    }

    public void PlayInventoryClose()
    {
        PlayButtonClick();
    }

    public void PlayConsume()
    {
        if (itemCollectClip != null && sfxSource != null)
        {
            sfxSource.pitch = 1.15f;
            sfxSource.PlayOneShot(itemCollectClip, masterVolume * sfxVolume);
        }
    }

    public void PlayObjectiveUpdate()
    {
        if (craftSuccessClip != null && sfxSource != null)
        {
            sfxSource.pitch = 1.10f;
            sfxSource.PlayOneShot(craftSuccessClip, masterVolume * sfxVolume * 0.9f);
        }
    }

    public void PlayToolEquip()
    {
        PlayButtonClick();
    }

    public void PlayToolUse(ToolType tool)
    {
        switch (tool)
        {
            case ToolType.StoneAxe:
                PlayResourceGather(ResourceType.Wood);
                break;
            case ToolType.StonePickaxe:
                PlayResourceGather(ResourceType.Stone);
                break;
            case ToolType.FishingRod:
                PlayFishBite();
                break;
            default:
                PlayResourceGather(ResourceType.Fiber);
                break;
        }
    }

    // =========================================================================
    // PROCEDURAL RETRO AUDIO SYNTHESIS FALLBACKS
    // Generates clean retro pixel-art audio waveforms if clips are not assigned in Inspector.
    // =========================================================================

    private void GenerateProceduralFallbacks()
    {
        if (footstepClip == null) footstepClip = CreateSynthClip("Procedural_Footstep", GenerateFootstep);
        if (waterFootstepClip == null) waterFootstepClip = CreateSynthClip("Procedural_WaterFootstep", GenerateWaterFootstep);
        if (gatherWoodClip == null) gatherWoodClip = CreateSynthClip("Procedural_GatherWood", GenerateWoodChop);
        if (gatherStoneClip == null) gatherStoneClip = CreateSynthClip("Procedural_GatherStone", GenerateStoneMine);
        if (gatherPlantClip == null) gatherPlantClip = CreateSynthClip("Procedural_GatherPlant", GeneratePlantForage);
        if (itemCollectClip == null) itemCollectClip = CreateSynthClip("Procedural_ItemCollect", GenerateItemCollect);
        if (craftSuccessClip == null) craftSuccessClip = CreateSynthClip("Procedural_CraftSuccess", GenerateCraftSuccess);
        if (craftFailClip == null) craftFailClip = CreateSynthClip("Procedural_CraftFail", GenerateCraftFail);
        if (buttonClickClip == null) buttonClickClip = CreateSynthClip("Procedural_ButtonClick", GenerateButtonClick);
        if (fishBiteClip == null) fishBiteClip = CreateSynthClip("Procedural_FishBite", GenerateFishBite);
        if (fishCatchClip == null) fishCatchClip = CreateSynthClip("Procedural_FishCatch", GenerateFishCatch);
        if (boatBuildClip == null) boatBuildClip = CreateSynthClip("Procedural_BoatBuild", GenerateBoatBuild);
        if (boatLaunchClip == null) boatLaunchClip = CreateSynthClip("Procedural_BoatLaunch", GenerateBoatLaunch);
        if (victoryClip == null) victoryClip = CreateSynthClip("Procedural_Victory", GenerateVictory);
        if (saveSuccessClip == null) saveSuccessClip = CreateSynthClip("Procedural_SaveSuccess", GenerateSaveSuccess);
        if (loadSuccessClip == null) loadSuccessClip = CreateSynthClip("Procedural_LoadSuccess", GenerateLoadSuccess);
    }

    private AudioClip CreateSynthClip(string clipName, Func<float[]> generator)
    {
        float[] samples = generator();
        AudioClip clip = AudioClip.Create(clipName, samples.Length, 1, 44100, false);
        clip.SetData(samples, 0);
        return clip;
    }

    private float[] GenerateFootstep()
    {
        int sampleRate = 44100;
        float duration = 0.05f;
        int count = Mathf.RoundToInt(sampleRate * duration);
        float[] data = new float[count];

        for (int i = 0; i < count; i++)
        {
            float t = (float)i / sampleRate;
            float env = Mathf.Exp(-t * 90f);
            float freq = Mathf.Lerp(140f, 45f, t / duration);
            float sine = Mathf.Sin(2f * Mathf.PI * freq * t);
            float noise = (UnityEngine.Random.value * 2f - 1f) * 0.25f;
            data[i] = (sine * 0.75f + noise) * env * 0.6f;
        }
        return data;
    }

    private float[] GenerateWaterFootstep()
    {
        int sampleRate = 44100;
        float duration = 0.085f;
        int count = Mathf.RoundToInt(sampleRate * duration);
        float[] data = new float[count];

        for (int i = 0; i < count; i++)
        {
            float t = (float)i / sampleRate;
            float env = Mathf.Exp(-t * 32f);
            float splashFreq = Mathf.Lerp(260f, 95f, t / duration);
            float sine = Mathf.Sin(2f * Mathf.PI * splashFreq * t);
            float slosh = (UnityEngine.Random.value * 2f - 1f) * 0.42f * Mathf.Exp(-t * 22f);
            data[i] = (sine * 0.45f + slosh) * env * 0.7f;
        }
        return data;
    }

    private float[] GenerateWoodChop()
    {
        int sampleRate = 44100;
        float duration = 0.09f;
        int count = Mathf.RoundToInt(sampleRate * duration);
        float[] data = new float[count];

        for (int i = 0; i < count; i++)
        {
            float t = (float)i / sampleRate;
            float env = Mathf.Exp(-t * 45f);
            float wave = Mathf.Sin(2f * Mathf.PI * 220f * t) + 0.5f * Mathf.Sin(2f * Mathf.PI * 440f * t);
            float pop = (UnityEngine.Random.value * 2f - 1f) * 0.4f * Mathf.Exp(-t * 120f);
            data[i] = (wave * 0.6f + pop) * env * 0.8f;
        }
        return data;
    }

    private float[] GenerateStoneMine()
    {
        int sampleRate = 44100;
        float duration = 0.08f;
        int count = Mathf.RoundToInt(sampleRate * duration);
        float[] data = new float[count];

        for (int i = 0; i < count; i++)
        {
            float t = (float)i / sampleRate;
            float env = Mathf.Exp(-t * 50f);
            float ping = Mathf.Sin(2f * Mathf.PI * 880f * t) * 0.6f + Mathf.Sin(2f * Mathf.PI * 1760f * t) * 0.4f;
            float grit = (UnityEngine.Random.value * 2f - 1f) * 0.2f * Mathf.Exp(-t * 90f);
            data[i] = (ping + grit) * env * 0.8f;
        }
        return data;
    }

    private float[] GeneratePlantForage()
    {
        int sampleRate = 44100;
        float duration = 0.07f;
        int count = Mathf.RoundToInt(sampleRate * duration);
        float[] data = new float[count];

        for (int i = 0; i < count; i++)
        {
            float t = (float)i / sampleRate;
            float env = Mathf.Exp(-t * 60f);
            float rustle = (UnityEngine.Random.value * 2f - 1f) * 0.7f;
            float tone = Mathf.Sin(2f * Mathf.PI * 340f * t) * 0.3f;
            data[i] = (rustle + tone) * env * 0.65f;
        }
        return data;
    }

    private float[] GenerateItemCollect()
    {
        int sampleRate = 44100;
        float duration = 0.09f;
        int count = Mathf.RoundToInt(sampleRate * duration);
        float[] data = new float[count];

        for (int i = 0; i < count; i++)
        {
            float t = (float)i / sampleRate;
            float env = Mathf.Exp(-t * 35f);
            float freq = Mathf.Lerp(480f, 960f, t / duration);
            data[i] = Mathf.Sin(2f * Mathf.PI * freq * t) * env * 0.75f;
        }
        return data;
    }

    private float[] GenerateCraftSuccess()
    {
        int sampleRate = 44100;
        float duration = 0.24f;
        int count = Mathf.RoundToInt(sampleRate * duration);
        float[] data = new float[count];

        // Three ascending cheerful notes (C5, E5, G5)
        for (int i = 0; i < count; i++)
        {
            float t = (float)i / sampleRate;
            float freq = (t < 0.08f) ? 523.25f : (t < 0.16f) ? 659.25f : 783.99f;
            float noteT = t % 0.08f;
            float env = Mathf.Exp(-noteT * 25f);
            data[i] = Mathf.Sin(2f * Mathf.PI * freq * t) * env * 0.7f;
        }
        return data;
    }

    private float[] GenerateCraftFail()
    {
        int sampleRate = 44100;
        float duration = 0.12f;
        int count = Mathf.RoundToInt(sampleRate * duration);
        float[] data = new float[count];

        for (int i = 0; i < count; i++)
        {
            float t = (float)i / sampleRate;
            float env = Mathf.Exp(-t * 30f);
            float wave = (Mathf.Sin(2f * Mathf.PI * 180f * t) > 0f ? 0.6f : -0.6f);
            data[i] = wave * env * 0.6f;
        }
        return data;
    }

    private float[] GenerateButtonClick()
    {
        int sampleRate = 44100;
        float duration = 0.025f;
        int count = Mathf.RoundToInt(sampleRate * duration);
        float[] data = new float[count];

        for (int i = 0; i < count; i++)
        {
            float t = (float)i / sampleRate;
            float env = Mathf.Exp(-t * 150f);
            float freq = Mathf.Lerp(1200f, 500f, t / duration);
            data[i] = Mathf.Sin(2f * Mathf.PI * freq * t) * env * 0.6f;
        }
        return data;
    }

    private float[] GenerateFishBite()
    {
        int sampleRate = 44100;
        float duration = 0.18f;
        int count = Mathf.RoundToInt(sampleRate * duration);
        float[] data = new float[count];

        for (int i = 0; i < count; i++)
        {
            float t = (float)i / sampleRate;
            bool pulse = (t < 0.07f) || (t >= 0.10f && t < 0.17f);
            float env = pulse ? Mathf.Exp(-(t % 0.07f) * 40f) : 0f;
            data[i] = Mathf.Sin(2f * Mathf.PI * 880f * t) * env * 0.8f;
        }
        return data;
    }

    private float[] GenerateFishCatch()
    {
        int sampleRate = 44100;
        float duration = 0.35f;
        int count = Mathf.RoundToInt(sampleRate * duration);
        float[] data = new float[count];

        // 4-note ascending fanfare: 523, 659, 784, 1046 Hz
        float[] freqs = new float[] { 523.25f, 659.25f, 783.99f, 1046.50f };
        for (int i = 0; i < count; i++)
        {
            float t = (float)i / sampleRate;
            int noteIndex = Mathf.Clamp(Mathf.FloorToInt(t / 0.085f), 0, 3);
            float noteT = t - noteIndex * 0.085f;
            float env = Mathf.Exp(-noteT * 18f);
            data[i] = Mathf.Sin(2f * Mathf.PI * freqs[noteIndex] * t) * env * 0.75f;
        }
        return data;
    }

    private float[] GenerateBoatBuild()
    {
        int sampleRate = 44100;
        float duration = 0.22f;
        int count = Mathf.RoundToInt(sampleRate * duration);
        float[] data = new float[count];

        for (int i = 0; i < count; i++)
        {
            float t = (float)i / sampleRate;
            float env = Mathf.Exp(-t * 22f);
            float lowThump = Mathf.Sin(2f * Mathf.PI * 130f * t) * 0.7f;
            float woodPing = Mathf.Sin(2f * Mathf.PI * 390f * t) * 0.4f;
            float strikeNoise = (UnityEngine.Random.value * 2f - 1f) * 0.3f * Mathf.Exp(-t * 80f);
            data[i] = (lowThump + woodPing + strikeNoise) * env * 0.85f;
        }
        return data;
    }

    private float[] GenerateBoatLaunch()
    {
        int sampleRate = 44100;
        float duration = 0.55f;
        int count = Mathf.RoundToInt(sampleRate * duration);
        float[] data = new float[count];

        for (int i = 0; i < count; i++)
        {
            float t = (float)i / sampleRate;
            float env = Mathf.Sin(Mathf.PI * (t / duration)); // Swell envelope
            float freq = Mathf.Lerp(130f, 260f, t / duration);
            float wave = Mathf.Sin(2f * Mathf.PI * freq * t) * 0.6f + Mathf.Sin(2f * Mathf.PI * (freq * 1.5f) * t) * 0.3f;
            float foam = (UnityEngine.Random.value * 2f - 1f) * 0.25f;
            data[i] = (wave + foam) * env * 0.85f;
        }
        return data;
    }

    private float[] GenerateVictory()
    {
        int sampleRate = 44100;
        float duration = 0.75f;
        int count = Mathf.RoundToInt(sampleRate * duration);
        float[] data = new float[count];

        // Grand ascending major arpeggio: C4, E4, G4, C5, E5, G5
        float[] freqs = new float[] { 261.63f, 329.63f, 392.00f, 523.25f, 659.25f, 783.99f };
        for (int i = 0; i < count; i++)
        {
            float t = (float)i / sampleRate;
            int noteIndex = Mathf.Clamp(Mathf.FloorToInt(t / 0.12f), 0, freqs.Length - 1);
            float noteT = t - noteIndex * 0.12f;
            float env = Mathf.Exp(-noteT * 12f);
            float vibrato = 1f + 0.02f * Mathf.Sin(2f * Mathf.PI * 6f * t);
            data[i] = Mathf.Sin(2f * Mathf.PI * freqs[noteIndex] * vibrato * t) * env * 0.75f;
        }
        return data;
    }

    private float[] GenerateSaveSuccess()
    {
        int sampleRate = 44100;
        float duration = 0.12f;
        int count = Mathf.RoundToInt(sampleRate * duration);
        float[] data = new float[count];

        for (int i = 0; i < count; i++)
        {
            float t = (float)i / sampleRate;
            float env = Mathf.Exp(-t * 30f);
            float chime = Mathf.Sin(2f * Mathf.PI * 660f * t) * 0.5f + Mathf.Sin(2f * Mathf.PI * 990f * t) * 0.5f;
            data[i] = chime * env * 0.65f;
        }
        return data;
    }

    private float[] GenerateLoadSuccess()
    {
        int sampleRate = 44100;
        float duration = 0.12f;
        int count = Mathf.RoundToInt(sampleRate * duration);
        float[] data = new float[count];

        for (int i = 0; i < count; i++)
        {
            float t = (float)i / sampleRate;
            float env = Mathf.Exp(-t * 30f);
            float chime = Mathf.Sin(2f * Mathf.PI * 520f * t) * 0.5f + Mathf.Sin(2f * Mathf.PI * 780f * t) * 0.5f;
            data[i] = chime * env * 0.65f;
        }
        return data;
    }
}
