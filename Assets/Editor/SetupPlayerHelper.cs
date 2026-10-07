using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;
using System.IO;
using System.Collections.Generic;
using System.Linq;

public class SetupPlayerHelper : EditorWindow
{
    [MenuItem("Tools/STRANDED/Setup Player Assets")]
    public static void SetupPlayerAssets()
    {
        string spritePath = "Assets/player/player_base.png";
        string animFolder = "Assets/player/Animations";
        
        if (!File.Exists(spritePath))
        {
            Debug.LogError("Could not find player_base.png at " + spritePath);
            return;
        }

        if (!AssetDatabase.IsValidFolder(animFolder))
        {
            AssetDatabase.CreateFolder("Assets/player", "Animations");
        }

        // 1. Configure and Slice Sprite
        TextureImporter importer = AssetImporter.GetAtPath(spritePath) as TextureImporter;
        if (importer != null)
        {
            importer.textureType = TextureImporterType.Sprite;
            importer.spriteImportMode = SpriteImportMode.Multiple;
            importer.spritePixelsPerUnit = 32;
            importer.filterMode = FilterMode.Point;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.mipmapEnabled = false;

            int cols = 6;
            int rows = 4;
            int frameWidth = 32;
            int frameHeight = 32;

            SpriteMetaData[] metaData = new SpriteMetaData[cols * rows];
            int index = 0;
            // Unity reads from bottom to top for sprites, so row 0 is bottom
            // Row 0: Down (my row 0 is top in PNG, so row 3 in Unity coordinates)
            // PNG Rows: 0 (Down), 1 (Up), 2 (Right), 3 (Left)
            // Unity Y goes from bottom to top. 
            // Unity Y=0 is PNG Row 3.
            for (int r = 0; r < rows; r++)
            {
                for (int c = 0; c < cols; c++)
                {
                    SpriteMetaData smd = new SpriteMetaData();
                    // Unity Y starts at bottom. PNG row 0 (Down) is Y = 96
                    int unityY = (rows - 1 - r) * frameHeight; 
                    smd.rect = new Rect(c * frameWidth, unityY, frameWidth, frameHeight);
                    smd.alignment = 0; // Center
                    smd.pivot = new Vector2(0.5f, 0.5f);
                    smd.name = $"player_base_{r}_{c}";
                    metaData[index++] = smd;
                }
            }
            importer.spritesheet = metaData;
            EditorUtility.SetDirty(importer);
            importer.SaveAndReimport();
        }

        // Load sliced sprites
        Object[] assets = AssetDatabase.LoadAllAssetsAtPath(spritePath);
        Sprite[] sprites = assets.OfType<Sprite>().OrderBy(s => s.name).ToArray();
        
        if (sprites.Length < 24)
        {
            Debug.LogError("Slicing failed, found " + sprites.Length + " sprites.");
            return;
        }

        // Mapping based on my PNG generation:
        // Row 0 (player_base_0_x): Down
        // Row 1 (player_base_1_x): Up
        // Row 2 (player_base_2_x): Right
        // Row 3 (player_base_3_x): Left
        // Col 0: Idle A
        // Col 1: Idle B (bob)
        // Col 2: Walk L
        // Col 3: Walk Pass
        // Col 4: Walk R
        // Col 5: Walk Pass
        
        AnimationClip idleDown = CreateAnim(animFolder, "IdleDown", new[] { sprites[0], sprites[1] }, 2f);
        AnimationClip walkDown = CreateAnim(animFolder, "WalkDown", new[] { sprites[2], sprites[3], sprites[4], sprites[5] }, 6f);
        
        AnimationClip idleUp = CreateAnim(animFolder, "IdleUp", new[] { sprites[6], sprites[7] }, 2f);
        AnimationClip walkUp = CreateAnim(animFolder, "WalkUp", new[] { sprites[8], sprites[9], sprites[10], sprites[11] }, 6f);
        
        AnimationClip idleRight = CreateAnim(animFolder, "IdleRight", new[] { sprites[12], sprites[13] }, 2f);
        AnimationClip walkRight = CreateAnim(animFolder, "WalkRight", new[] { sprites[14], sprites[15], sprites[16], sprites[17] }, 6f);
        
        AnimationClip idleLeft = CreateAnim(animFolder, "IdleLeft", new[] { sprites[18], sprites[19] }, 2f);
        AnimationClip walkLeft = CreateAnim(animFolder, "WalkLeft", new[] { sprites[20], sprites[21], sprites[22], sprites[23] }, 6f);

        // Create Animator Controller
        string controllerPath = "Assets/player/PlayerController.controller";
        AnimatorController controller = AnimatorController.CreateAnimatorControllerAtPath(controllerPath);
        controller.AddParameter("MoveX", AnimatorControllerParameterType.Float);
        controller.AddParameter("MoveY", AnimatorControllerParameterType.Float);
        controller.AddParameter("IsMoving", AnimatorControllerParameterType.Bool);

        // Blend Trees
        BlendTree idleTree;
        AnimatorState idleState = controller.CreateBlendTreeInController("Idle", out idleTree);
        idleTree.blendType = BlendTreeType.SimpleDirectional2D;
        idleTree.blendParameter = "MoveX";
        idleTree.blendParameterY = "MoveY";
        idleTree.AddChild(idleDown, new Vector2(0, -1));
        idleTree.AddChild(idleUp, new Vector2(0, 1));
        idleTree.AddChild(idleLeft, new Vector2(-1, 0));
        idleTree.AddChild(idleRight, new Vector2(1, 0));

        BlendTree walkTree;
        AnimatorState walkState = controller.CreateBlendTreeInController("Walk", out walkTree);
        walkTree.blendType = BlendTreeType.SimpleDirectional2D;
        walkTree.blendParameter = "MoveX";
        walkTree.blendParameterY = "MoveY";
        walkTree.AddChild(walkDown, new Vector2(0, -1));
        walkTree.AddChild(walkUp, new Vector2(0, 1));
        walkTree.AddChild(walkLeft, new Vector2(-1, 0));
        walkTree.AddChild(walkRight, new Vector2(1, 0));

        // Transitions
        AnimatorStateTransition toWalk = idleState.AddTransition(walkState);
        toWalk.AddCondition(AnimatorConditionMode.If, 0, "IsMoving");
        toWalk.hasExitTime = false;
        toWalk.duration = 0f;

        AnimatorStateTransition toIdle = walkState.AddTransition(idleState);
        toIdle.AddCondition(AnimatorConditionMode.IfNot, 0, "IsMoving");
        toIdle.hasExitTime = false;
        toIdle.duration = 0f;

        AssetDatabase.SaveAssets();

        // Setup Player GameObject in scene
        GameObject playerObj = GameObject.Find("Player");
        if (playerObj == null)
        {
            playerObj = new GameObject("Player");
            playerObj.transform.position = Vector3.zero;
        }

        SpriteRenderer sr = playerObj.GetComponent<SpriteRenderer>();
        if (sr == null) sr = playerObj.AddComponent<SpriteRenderer>();
        sr.sprite = sprites[0];

        Animator anim = playerObj.GetComponent<Animator>();
        if (anim == null) anim = playerObj.AddComponent<Animator>();
        anim.runtimeAnimatorController = controller;

        Rigidbody2D rb = playerObj.GetComponent<Rigidbody2D>();
        if (rb == null) rb = playerObj.AddComponent<Rigidbody2D>();
        rb.gravityScale = 0;
        rb.freezeRotation = true;

        BoxCollider2D col = playerObj.GetComponent<BoxCollider2D>();
        if (col == null) col = playerObj.AddComponent<BoxCollider2D>();
        // Feet collider
        col.size = new Vector2(0.5f, 0.25f);
        col.offset = new Vector2(0, -0.375f); 

        if (playerObj.GetComponent<PlayerMovement>() == null)
        {
            playerObj.AddComponent<PlayerMovement>();
        }

        Debug.Log("Player Setup Complete!");
    }

    private static AnimationClip CreateAnim(string folder, string clipName, Sprite[] sprites, float fps)
    {
        string path = $"{folder}/{clipName}.anim";
        AnimationClip clip = new AnimationClip();
        clip.frameRate = fps;

        EditorCurveBinding spriteBinding = new EditorCurveBinding();
        spriteBinding.type = typeof(SpriteRenderer);
        spriteBinding.path = "";
        spriteBinding.propertyName = "m_Sprite";

        ObjectReferenceKeyframe[] keyFrames = new ObjectReferenceKeyframe[sprites.Length + 1];
        for (int i = 0; i < sprites.Length; i++)
        {
            keyFrames[i] = new ObjectReferenceKeyframe();
            keyFrames[i].time = i / fps;
            keyFrames[i].value = sprites[i];
        }
        // Loop frame
        keyFrames[sprites.Length] = new ObjectReferenceKeyframe();
        keyFrames[sprites.Length].time = sprites.Length / fps;
        keyFrames[sprites.Length].value = sprites[sprites.Length - 1];

        AnimationUtility.SetObjectReferenceCurve(clip, spriteBinding, keyFrames);
        
        AnimationClipSettings settings = AnimationUtility.GetAnimationClipSettings(clip);
        settings.loopTime = true;
        AnimationUtility.SetAnimationClipSettings(clip, settings);

        AssetDatabase.CreateAsset(clip, path);
        return clip;
    }
}
