using System;
using System.IO;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;

/// <summary>
/// Editor utility to place natural, biome-distributed ResourceNodes across the STRANDED island.
/// Preserves existing terrain, water, river crossing, camp clearing, and escape cove.
/// Creates fully interactive gameplay objects with proper colliders, Y-depth sorting, and visual feedback.
/// </summary>
public class IslandResourcePlacer : EditorWindow
{
    private const string JSON_PATH = "Assets/Art/Terrain/island_world_350.json";
    private const string SCENE_PATH = "Assets/Scenes/MainScene.unity";

    // Data structures for JSON parsing
    [Serializable]
    private class MapData
    {
        public string title;
        public int width;
        public int height;
        public PlayerSpawn playerSpawn;
        public List<List<int>> tiles;
    }

    [Serializable]
    private class PlayerSpawn
    {
        public int x;
        public int y;
    }

    [MenuItem("Tools/STRANDED/Populate Environment & Resource Objects")]
    public static void PopulateResources()
    {
        if (!File.Exists(JSON_PATH))
        {
            Debug.LogError($"Map JSON file not found at {JSON_PATH}!");
            return;
        }

        // Open Scene if needed
        var activeScene = EditorSceneManager.GetActiveScene();
        if (activeScene.path != SCENE_PATH)
        {
            EditorSceneManager.OpenScene(SCENE_PATH);
        }

        EditorUtility.DisplayProgressBar("STRANDED Resource Placement", "Loading island world data...", 0.1f);

        string jsonText = File.ReadAllText(JSON_PATH);
        MapData mapData = ParseMapData(jsonText);
        if (mapData == null || mapData.tiles == null)
        {
            EditorUtility.ClearProgressBar();
            Debug.LogError("Failed to parse map JSON data.");
            return;
        }

        int width = mapData.width;
        int height = mapData.height;

        // 1. Load Sprite Assets
        EditorUtility.DisplayProgressBar("STRANDED Resource Placement", "Loading environmental sprites...", 0.2f);
        Sprite spMatureTree = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_tropical_mature.png");
        Sprite spTreeStump = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_tropical_stump.png");
        Sprite spPineMature = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_pine_mature.png");
        Sprite spPineStump = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_pine_stump.png");
        Sprite spBirchMature = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_birch_mature.png");
        Sprite spBirchStump = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_birch_stump.png");
        Sprite spMapleMature = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_maple_mature.png");
        Sprite spMapleStump = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_maple_stump.png");
        Sprite spMahoganyMature = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_mahogany_mature.png");
        Sprite spMahoganyStump = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_mahogany_stump.png");
        Sprite spSpruceMature = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_spruce_mature.png");
        Sprite spSpruceStump = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_spruce_stump.png");

        Sprite spFirMature = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_fir_mature.png");
        Sprite spFirStump = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_fir_stump.png");
        Sprite spCedarMature = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_cedar_mature.png");
        Sprite spCedarStump = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_cedar_stump.png");
        Sprite spMossyOakMature = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_mossy_oak_mature.png");
        Sprite spMossyOakStump = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_mossy_oak_stump.png");
        Sprite spFruitMature = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_fruit_mature.png");
        Sprite spFruitStump = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/tree_fruit_stump.png");

        Sprite spPalmFull = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/palm_coconut_full.png");
        Sprite spPalmEmpty = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/palm_coconut_empty.png");
        Sprite spDriftwood = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/driftwood_log.png");
        Sprite spDriftwoodSmall = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Trees/driftwood_small.png");

        Sprite spBoulder = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Rocks/rock_boulder_large.png");
        Sprite spRockMed = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Rocks/rock_slate_medium.png");
        Sprite spRockSmall = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Rocks/rock_slate_small.png");

        Sprite spBerryFull = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Plants/bush_berry_full.png");
        Sprite spBerryEmpty = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Plants/bush_berry_empty.png");
        Sprite spBushSmall = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Plants/bush_shrub_small.png");
        Sprite spBushMed = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Plants/bush_foliage_medium.png");
        Sprite spBushPink = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Plants/bush_flowering_pink.png");
        Sprite spBushWhite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Plants/bush_flowering_white.png");
        Sprite spBushGolden = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Plants/bush_autumn_golden.png");
        Sprite spFiberFern = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Plants/plant_fiber_fern.png");
        Sprite spFiberTuft = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Plants/plant_fiber_tuft.png");
        Sprite spGrassWild = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/Environment/Plants/plant_grass_wild.png");

        if (spMatureTree == null || spBoulder == null || spBerryFull == null || spPalmFull == null || spFiberFern == null || spPineMature == null || spBirchMature == null)
        {
            EditorUtility.ClearProgressBar();
            Debug.LogError("One or more required environmental sprite assets are missing! Re-import Assets/Art/Environment.");
            return;
        }

        // Tree Specifications for Clustered Forest Biomes & Diverse Roster
        var allTreeSpecs = new List<(string name, Sprite mature, Sprite stump, float colWidth, float colHeight)>
        {
            ("Vibrant Emerald Fir", spFirMature != null ? spFirMature : spPineMature, spFirStump != null ? spFirStump : spPineStump, 0.65f, 0.30f),
            ("Pinecone Cedar", spCedarMature != null ? spCedarMature : spPineMature, spCedarStump != null ? spCedarStump : spPineStump, 0.65f, 0.30f),
            ("Emerald Spruce Tree", spSpruceMature != null ? spSpruceMature : spPineMature, spSpruceStump != null ? spSpruceStump : spPineStump, 0.70f, 0.30f),
            ("Mountain Pine", spPineMature, spPineStump, 0.65f, 0.30f),
            ("Slender Birch Tree", spBirchMature, spBirchStump, 0.55f, 0.28f),
            ("Mossy Ancient Oak", spMossyOakMature != null ? spMossyOakMature : spMatureTree, spMossyOakStump != null ? spMossyOakStump : spTreeStump, 0.80f, 0.35f),
            ("Golden Fruit Tree", spFruitMature != null ? spFruitMature : spMatureTree, spFruitStump != null ? spFruitStump : spTreeStump, 0.75f, 0.32f),
            ("Amber Maple Tree", spMapleMature != null ? spMapleMature : spMatureTree, spMapleStump != null ? spMapleStump : spTreeStump, 0.75f, 0.32f),
            ("Mahogany Tree", spMahoganyMature != null ? spMahoganyMature : spMatureTree, spMahoganyStump != null ? spMahoganyStump : spTreeStump, 0.75f, 0.32f),
            ("Tropical Oak", spMatureTree, spTreeStump, 0.80f, 0.35f)
        };

        var highlandTreeSpecs = new List<(string name, Sprite mature, Sprite stump, float colWidth, float colHeight)>
        {
            ("Mountain Pine", spPineMature, spPineStump, 0.65f, 0.30f),
            ("Vibrant Emerald Fir", spFirMature != null ? spFirMature : spPineMature, spFirStump != null ? spFirStump : spPineStump, 0.65f, 0.30f),
            ("Pinecone Cedar", spCedarMature != null ? spCedarMature : spPineMature, spCedarStump != null ? spCedarStump : spPineStump, 0.65f, 0.30f),
            ("Emerald Spruce Tree", spSpruceMature != null ? spSpruceMature : spPineMature, spSpruceStump != null ? spSpruceStump : spPineStump, 0.70f, 0.30f)
        };

        // 2. Prepare Root Hierarchy
        EditorUtility.DisplayProgressBar("STRANDED Resource Placement", "Setting up Environment hierarchy...", 0.3f);
        GameObject envRoot = GameObject.Find("Environment_Resources");
        if (envRoot != null)
        {
            Undo.DestroyObjectImmediate(envRoot);
        }
        envRoot = new GameObject("Environment_Resources");
        Undo.RegisterCreatedObjectUndo(envRoot, "Create Environment_Resources");

        Transform pTrees = new GameObject("Trees").transform;
        pTrees.SetParent(envRoot.transform);
        Transform pPalms = new GameObject("CoconutPalms").transform;
        pPalms.SetParent(envRoot.transform);
        Transform pRocks = new GameObject("Rocks").transform;
        pRocks.SetParent(envRoot.transform);
        Transform pBushes = new GameObject("BerryBushes").transform;
        pBushes.SetParent(envRoot.transform);
        Transform pFiber = new GameObject("FiberPlants").transform;
        pFiber.SetParent(envRoot.transform);
        Transform pDriftwood = new GameObject("Driftwood").transform;
        pDriftwood.SetParent(envRoot.transform);

        // Precompute river proximity
        EditorUtility.DisplayProgressBar("STRANDED Resource Placement", "Analyzing riverbanks & geography...", 0.4f);
        float[,] distToRiver = new float[height, width];
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                distToRiver[y, x] = 999f;
            }
        }

        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                if (mapData.tiles[y][x] == 5) // River
                {
                    distToRiver[y, x] = 0f;
                    for (int dy = -4; dy <= 4; dy++)
                    {
                        for (int dx = -4; dx <= 4; dx++)
                        {
                            int ny = y + dy;
                            int nx = x + dx;
                            if (ny >= 0 && ny < height && nx >= 0 && nx < width)
                            {
                                float dist = Mathf.Sqrt(dx * dx + dy * dy);
                                if (dist < distToRiver[ny, nx])
                                {
                                    distToRiver[ny, nx] = dist;
                                }
                            }
                        }
                    }
                }
            }
        }

        // Spatial grid for organic non-overlapping placement
        const int GRID_CELL = 4;
        Dictionary<Vector2Int, List<Vector2>> spatialGrid = new Dictionary<Vector2Int, List<Vector2>>();

        bool CanPlace(Vector2 pos, float minDist)
        {
            int gx = Mathf.FloorToInt(pos.x / GRID_CELL);
            int gy = Mathf.FloorToInt(pos.y / GRID_CELL);
            float minDistSq = minDist * minDist;

            for (int dgy = -1; dgy <= 1; dgy++)
            {
                for (int dgx = -1; dgx <= 1; dgx++)
                {
                    Vector2Int cell = new Vector2Int(gx + dgx, gy + dgy);
                    if (spatialGrid.TryGetValue(cell, out var list))
                    {
                        for (int i = 0; i < list.Count; i++)
                        {
                            if ((list[i] - pos).sqrMagnitude < minDistSq)
                            {
                                return false;
                            }
                        }
                    }
                }
            }
            return true;
        }

        void RegisterPlaced(Vector2 pos)
        {
            int gx = Mathf.FloorToInt(pos.x / GRID_CELL);
            int gy = Mathf.FloorToInt(pos.y / GRID_CELL);
            Vector2Int cell = new Vector2Int(gx, gy);
            if (!spatialGrid.TryGetValue(cell, out var list))
            {
                list = new List<Vector2>();
                spatialGrid[cell] = list;
            }
            list.Add(pos);
        }

        int countTrees = 0, countPalms = 0, countBoulders = 0, countRocksMed = 0;
        int countRocksSmall = 0, countBushes = 0, countFiber = 0, countDriftwood = 0;

        // 3. Guaranteed Starting Camp Starter Resources
        EditorUtility.DisplayProgressBar("STRANDED Resource Placement", "Placing starter resources near camp...", 0.5f);
        CreateTree(new Vector2(131.5f, 124.5f), spMatureTree, spTreeStump, pTrees, "Tropical Tree", 0.80f, 0.35f);
        RegisterPlaced(new Vector2(131.5f, 124.5f)); countTrees++;

        CreateTree(new Vector2(140.5f, 125.5f), spSpruceMature != null ? spSpruceMature : spMatureTree, spSpruceStump != null ? spSpruceStump : spTreeStump, pTrees, "Emerald Spruce Tree", 0.70f, 0.30f);
        RegisterPlaced(new Vector2(140.5f, 125.5f)); countTrees++;

        CreateBerryBush(new Vector2(138.5f, 116.5f), spBerryFull, spBerryEmpty, pBushes);
        RegisterPlaced(new Vector2(138.5f, 116.5f)); countBushes++;

        CreateFiberPlant(new Vector2(132.5f, 117.5f), spFiberFern, pFiber, "Fiber Fern");
        RegisterPlaced(new Vector2(132.5f, 117.5f)); countFiber++;

        CreateFiberPlant(new Vector2(137.5f, 123.5f), spFiberTuft, pFiber, "Wild Fiber");
        RegisterPlaced(new Vector2(137.5f, 123.5f)); countFiber++;

        CreateMediumRock(new Vector2(130.5f, 119.5f), spRockMed, pRocks);
        RegisterPlaced(new Vector2(130.5f, 119.5f)); countRocksMed++;

        // 4. Biome Distribution Loop
        EditorUtility.DisplayProgressBar("STRANDED Resource Placement", "Scattering biome resource nodes...", 0.6f);
        float spawnX = mapData.playerSpawn.x;
        float spawnY = mapData.playerSpawn.y;

        for (int y = 50; y < 310; y++)
        {
            for (int x = 50; x < 310; x++)
            {
                int t = mapData.tiles[y][x];

                // Never place on deep ocean (0), shallow water (1), river water (5), or cliff wall (6)
                if (t == 0 || t == 1 || t == 5 || t == 6) continue;

                // Keep camp clearing open
                float distSpawn = Mathf.Sqrt((x - spawnX) * (x - spawnX) + (y - spawnY) * (y - spawnY));
                if (distSpawn < 7.5f) continue;

                // Keep river crossing clear: Y=149..161, X=170..182
                if (y >= 149 && y <= 161 && x >= 170 && x <= 182) continue;

                // Keep Escape Cove boat launching area clear: Y=84..96, X=224..246
                if (y >= 84 && y <= 96 && x >= 224 && x <= 246) continue;

                float clusterVal = GetNoise(x / 6, y / 6, 42); // macro clusters
                float localVal = GetNoise(x, y, 99);
                float dRiver = distToRiver[y, x];

                // Organic jitter
                Vector2 pos = new Vector2(
                    x + 0.2f + (GetNoise(x, y, 101) * 0.6f),
                    y + 0.2f + (GetNoise(x, y, 102) * 0.6f)
                );

                // --- BIOME 1: BEACH / COAST (Tile 2: Sand) ---
                if (t == 2)
                {
                    // Coconut Palms along coastal sandy curves
                    if (clusterVal > 0.68f && localVal < 0.14f)
                    {
                        if (CanPlace(pos, 4.5f))
                        {
                            CreatePalm(pos, spPalmFull, spPalmEmpty, pPalms);
                            RegisterPlaced(pos);
                            countPalms++;
                        }
                    }
                    // Driftwood logs washed up on sand
                    else if (localVal < 0.025f)
                    {
                        if (CanPlace(pos, 3.5f))
                        {
                            if (GetNoise(x, y, 77) < 0.5f && spDriftwoodSmall != null)
                            {
                                CreateVerySmallLog(pos, spDriftwoodSmall, pDriftwood);
                            }
                            else
                            {
                                CreateDriftwood(pos, spDriftwood, pDriftwood);
                            }
                            RegisterPlaced(pos);
                            countDriftwood++;
                        }
                    }
                    // Coastal small slate stones
                    else if (localVal < 0.045f)
                    {
                        if (CanPlace(pos, 2.5f))
                        {
                            CreateSmallRock(pos, spRockSmall, pRocks);
                            RegisterPlaced(pos);
                            countRocksSmall++;
                        }
                    }
                    // Coastal fiber tufts
                    else if (localVal < 0.065f)
                    {
                        if (CanPlace(pos, 2.2f))
                        {
                            CreateFiberPlant(pos, spFiberTuft, pFiber, "Coastal Fiber");
                            RegisterPlaced(pos);
                            countFiber++;
                        }
                    }
                }
                // --- BIOME 2: RIVERBANKS (near River water <= 3.2 tiles) ---
                else if (dRiver <= 3.2f)
                {
                    // Riverbank fiber ferns
                    if (localVal < 0.09f)
                    {
                        if (CanPlace(pos, 2.2f))
                        {
                            CreateFiberPlant(pos, spFiberFern, pFiber, "River Fern");
                            RegisterPlaced(pos);
                            countFiber++;
                        }
                    }
                    // River slate stones
                    else if (localVal < 0.14f)
                    {
                        if (CanPlace(pos, 2.4f))
                        {
                            CreateMediumRock(pos, spRockMed, pRocks);
                            RegisterPlaced(pos);
                            countRocksMed++;
                        }
                    }
                    // Riverbank berry bushes
                    else if (localVal < 0.17f)
                    {
                        if (CanPlace(pos, 2.8f))
                        {
                            CreateBerryBush(pos, spBerryFull, spBerryEmpty, pBushes);
                            RegisterPlaced(pos);
                            countBushes++;
                        }
                    }
                }
                // --- BIOME 3: ROCKY PLATEAU / HIGHLANDS (Tile 7: Cliff Top) ---
                else if (t == 7)
                {
                    // Large Boulders
                    if (localVal < 0.07f)
                    {
                        if (CanPlace(pos, 3.2f))
                        {
                            CreateBoulder(pos, spBoulder, spRockSmall, pRocks);
                            RegisterPlaced(pos);
                            countBoulders++;
                        }
                    }
                    // Medium Rocks
                    else if (localVal < 0.15f)
                    {
                        if (CanPlace(pos, 2.4f))
                        {
                            CreateMediumRock(pos, spRockMed, pRocks);
                            RegisterPlaced(pos);
                            countRocksMed++;
                        }
                    }
                    // Scree pebbles
                    else if (localVal < 0.22f)
                    {
                        if (CanPlace(pos, 2.0f))
                        {
                            CreateSmallRock(pos, spRockSmall, pRocks);
                            RegisterPlaced(pos);
                            countRocksSmall++;
                        }
                    }
                    // Hardy mountain fiber tufts
                    else if (localVal < 0.26f)
                    {
                        if (CanPlace(pos, 2.2f))
                        {
                            CreateFiberPlant(pos, spFiberTuft, pFiber, "Mountain Fiber");
                            RegisterPlaced(pos);
                            countFiber++;
                        }
                    }
                    // Hardy mountain conifers on rocky plateau
                    else if (localVal < 0.22f)
                    {
                        if (CanPlace(pos, 2.8f))
                        {
                            float hNoise = GetNoise(x, y, 88);
                            int hIdx = Mathf.Clamp(Mathf.FloorToInt(hNoise * highlandTreeSpecs.Count), 0, highlandTreeSpecs.Count - 1);
                            var spec = highlandTreeSpecs[hIdx];
                            CreateTree(pos, spec.mature, spec.stump, pTrees, spec.name, spec.colWidth, spec.colHeight);
                            RegisterPlaced(pos);
                            countTrees++;
                        }
                    }
                }
                // --- BIOME 4: FOREST & MEADOWS (Tile 3: Grass) ---
                else if (t == 3)
                {
                    bool placeTree = false;
                    float treeSpacing = 2.4f;

                    // Dense forest groves & clusters
                    if (clusterVal > 0.32f && localVal < 0.32f)
                    {
                        placeTree = true;
                        treeSpacing = 2.4f;
                    }
                    // Open meadows & scattered clearings
                    else if (clusterVal <= 0.32f && localVal < 0.08f)
                    {
                        placeTree = true;
                        treeSpacing = 3.2f;
                    }

                    if (placeTree && CanPlace(pos, treeSpacing))
                    {
                        // Forest grove clustering algorithm:
                        // Regional macro noise creates continuous forest biomes/groves of the same tree type
                        float groveSpecies = GetNoise(x / 14, y / 14, 555);
                        float grovePurity = GetNoise(x / 8, y / 8, 333);

                        int specIdx;
                        if (grovePurity > 0.25f)
                        {
                            // Coherent species grove (clusters of same type of trees creating a forest-like terrain)
                            specIdx = Mathf.Clamp(Mathf.FloorToInt(groveSpecies * allTreeSpecs.Count), 0, allTreeSpecs.Count - 1);
                        }
                        else
                        {
                            // Organic mixed woodland transition
                            float mixNoise = GetNoise(x, y, 77);
                            specIdx = Mathf.Clamp(Mathf.FloorToInt(mixNoise * allTreeSpecs.Count), 0, allTreeSpecs.Count - 1);
                        }

                        var spec = allTreeSpecs[specIdx];
                        CreateTree(pos, spec.mature, spec.stump, pTrees, spec.name, spec.colWidth, spec.colHeight);
                        RegisterPlaced(pos);
                        countTrees++;
                    }
                    // Diverse Bushes in forest clearings
                    else if (clusterVal > 0.35f && localVal < 0.055f)
                    {
                        if (CanPlace(pos, 2.5f))
                        {
                            float bushNoise = GetNoise(x, y, 62);
                            if (bushNoise < 0.35f)
                            {
                                CreateBerryBush(pos, spBerryFull, spBerryEmpty, pBushes);
                            }
                            else if (bushNoise < 0.55f && spBushPink != null)
                            {
                                CreateFoliageBush(pos, spBushPink, pBushes, "Flowering Pink Bush");
                            }
                            else if (bushNoise < 0.75f && spBushWhite != null)
                            {
                                CreateFoliageBush(pos, spBushWhite, pBushes, "Flowering White Bush");
                            }
                            else if (spBushMed != null)
                            {
                                CreateFoliageBush(pos, spBushMed, pBushes, "Foliage Bush");
                            }
                            else
                            {
                                CreateBerryBush(pos, spBerryFull, spBerryEmpty, pBushes);
                            }
                            RegisterPlaced(pos);
                            countBushes++;
                        }
                    }
                    // Forest Fiber plants
                    else if (localVal < 0.055f)
                    {
                        if (CanPlace(pos, 2.0f))
                        {
                            CreateFiberPlant(pos, spFiberFern, pFiber, "Forest Fern");
                            RegisterPlaced(pos);
                            countFiber++;
                        }
                    }
                    // Mossy Forest Rocks
                    else if (localVal < 0.075f)
                    {
                        if (CanPlace(pos, 2.6f))
                        {
                            CreateMediumRock(pos, spRockMed, pRocks);
                            RegisterPlaced(pos);
                            countRocksMed++;
                        }
                    }
                }
                // --- BIOME 5: INTERIOR SOIL / DIRT (Tile 4) ---
                else if (t == 4)
                {
                    // Interior trees in natural groves
                    if (clusterVal > 0.55f && localVal < 0.08f)
                    {
                        if (CanPlace(pos, 4.0f))
                        {
                            float varNoise = GetNoise(x, y, 88);
                            if (varNoise < 0.22f)
                            {
                                CreateTree(pos, spBirchMature, spBirchStump, pTrees, "Birch Tree", 0.55f, 0.28f);
                            }
                            else if (varNoise < 0.44f && spMapleMature != null)
                            {
                                CreateTree(pos, spMapleMature, spMapleStump, pTrees, "Amber Maple Tree", 0.70f, 0.30f);
                            }
                            else if (varNoise < 0.66f)
                            {
                                CreateTree(pos, spPineMature, spPineStump, pTrees, "Pine Tree", 0.65f, 0.30f);
                            }
                            else if (varNoise < 0.85f && spSpruceMature != null)
                            {
                                CreateTree(pos, spSpruceMature, spSpruceStump, pTrees, "Mountain Spruce", 0.65f, 0.30f);
                            }
                            else
                            {
                                CreateTree(pos, spMatureTree, spTreeStump, pTrees, "Tropical Tree", 0.80f, 0.35f);
                            }
                            RegisterPlaced(pos);
                            countTrees++;
                        }
                    }
                    // Interior bushes and shrubs (NO large boulders in interior plains!)
                    else if (localVal < 0.065f)
                    {
                        if (CanPlace(pos, 2.6f))
                        {
                            float bushNoise = GetNoise(x, y, 94);
                            if (bushNoise < 0.40f)
                            {
                                CreateBerryBush(pos, spBerryFull, spBerryEmpty, pBushes);
                            }
                            else if (bushNoise < 0.70f && spBushSmall != null)
                            {
                                CreateFoliageBush(pos, spBushSmall, pBushes, "Green Shrub");
                            }
                            else if (spBushGolden != null)
                            {
                                CreateFoliageBush(pos, spBushGolden, pBushes, "Golden Shrub");
                            }
                            else
                            {
                                CreateBerryBush(pos, spBerryFull, spBerryEmpty, pBushes);
                            }
                            RegisterPlaced(pos);
                            countBushes++;
                        }
                    }
                    // Interior fiber & ferns
                    else if (localVal < 0.045f)
                    {
                        if (CanPlace(pos, 2.0f))
                        {
                            CreateFiberPlant(pos, spFiberFern, pFiber, "Wild Fern");
                            RegisterPlaced(pos);
                            countFiber++;
                        }
                    }
                    // Small stone pebbles and slate rocks (replaces boulders on interior plains)
                    else if (clusterVal < 0.22f && localVal < 0.035f)
                    {
                        if (CanPlace(pos, 2.5f))
                        {
                            CreateSmallRock(pos, spRockSmall, pRocks);
                            RegisterPlaced(pos);
                            countRocksSmall++;
                        }
                    }
                }
            }
        }

        // 5. Ensure Player has PlayerInteraction component & TemporaryResourceHUD exists
        EditorUtility.DisplayProgressBar("STRANDED Resource Placement", "Configuring Player interaction...", 0.9f);
        GameObject playerObj = GameObject.Find("Player");
        if (playerObj != null)
        {
            if (playerObj.GetComponent<PlayerInteraction>() == null)
            {
                Undo.AddComponent<PlayerInteraction>(playerObj);
                Debug.Log("Attached PlayerInteraction component to Player.");
            }
            if (playerObj.GetComponent<Inventory>() == null)
            {
                Undo.AddComponent<Inventory>(playerObj);
                Debug.Log("Attached Inventory component to Player.");
            }
            if (playerObj.GetComponent<HotbarUI>() == null)
            {
                Undo.AddComponent<HotbarUI>(playerObj);
                Debug.Log("Attached HotbarUI component to Player.");
            }
            if (playerObj.GetComponent<InventoryUI>() == null)
            {
                Undo.AddComponent<InventoryUI>(playerObj);
                Debug.Log("Attached InventoryUI component to Player.");
            }
        }

        GameObject hudObj = GameObject.Find("TemporaryResourceHUD");
        if (hudObj == null)
        {
            hudObj = new GameObject("TemporaryResourceHUD");
            hudObj.AddComponent<TemporaryResourceHUD>();
            Undo.RegisterCreatedObjectUndo(hudObj, "Create TemporaryResourceHUD");
        }

        VineResourcePlacer.PlaceVineResources();
        ResourceNode.EnsureStartingCampResourcesExist();

        // 6. Save Scene
        EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
        EditorSceneManager.SaveOpenScenes();
        EditorUtility.ClearProgressBar();

        Debug.Log("=====================================================================");
        Debug.Log("STRANDED: Environment & Resource Objects Successfully Populated!");
        Debug.Log($"  Trees (Wood):            {countTrees}");
        Debug.Log($"  Coconut Palms (Coconut): {countPalms}");
        Debug.Log($"  Large Boulders (Stone):  {countBoulders}");
        Debug.Log($"  Medium Slate (Stone):    {countRocksMed}");
        Debug.Log($"  Small Pebbles (Stone):   {countRocksSmall}");
        Debug.Log($"  Berry Bushes (Berries):  {countBushes}");
        Debug.Log($"  Fiber Plants (Fiber):    {countFiber}");
        Debug.Log($"  Driftwood Logs (Wood):   {countDriftwood}");
        Debug.Log($"  TOTAL RESOURCE NODES:    {countTrees + countPalms + countBoulders + countRocksMed + countRocksSmall + countBushes + countFiber + countDriftwood}");
        Debug.Log("=====================================================================");
    }

    private static float GetNoise(int x, int y, int seed)
    {
        int n = (x * 73856093) ^ (y * 19349663) ^ (seed * 83492791);
        n = (n ^ (n >> 13)) * 1274126177;
        int h = (n ^ (n >> 16)) & 0x7FFFFFFF;
        return (h % 10000) / 10000.0f;
    }

    private static void CreateTree(Vector2 pos, Sprite mature, Sprite stump, Transform parent, string treeName = "Tropical Tree", float colWidth = 0.80f, float colHeight = 0.35f)
    {
        string safePrefix = treeName.Replace(" ", "_");
        GameObject go = new GameObject($"{safePrefix}_{pos.x:F0}_{pos.y:F0}");
        go.transform.position = new Vector3(pos.x, pos.y, 0f);
        go.transform.SetParent(parent);

        SpriteRenderer sr = go.AddComponent<SpriteRenderer>();
        sr.sprite = mature;
        sr.sortingOrder = ResourceNode.BASE_SORTING_ORDER + Mathf.RoundToInt(-pos.y * 10f);

        // Trunk base collider: player can walk behind canopy and in front of trunk
        BoxCollider2D col = go.AddComponent<BoxCollider2D>();
        col.size = new Vector2(colWidth, colHeight);
        col.offset = new Vector2(0f, colHeight * 0.5f);

        ResourceNode node = go.AddComponent<ResourceNode>();
        SetSerializedField(node, "resourceType", (int)ResourceType.Wood);
        SetSerializedField(node, "requiredTool", (int)ToolType.StoneAxe);
        SetSerializedField(node, "nodeCategory", (int)ResourceCategory.Tree);
        SetSerializedField(node, "nodeSize", (int)ResourceSize.Large);
        SetSerializedField(node, "nodeDisplayName", treeName);
        SetSerializedField(node, "yieldAmount", 2);
        SetSerializedField(node, "interactionRange", 1.6f);
        SetSerializedField(node, "availableSprite", mature);
        SetSerializedField(node, "depletedSprite", stump);
        SetSerializedField(node, "depleteOnHarvest", true);
        SetSerializedField(node, "destroyOnDeplete", false);
        SetSerializedField(node, "regrowthDuration", 90f);

        node.UpdateSortingOrder();
    }

    private static void CreatePalm(Vector2 pos, Sprite full, Sprite empty, Transform parent)
    {
        GameObject go = new GameObject($"Palm_Coconut_{pos.x:F0}_{pos.y:F0}");
        go.transform.position = new Vector3(pos.x, pos.y, 0f);
        go.transform.SetParent(parent);

        SpriteRenderer sr = go.AddComponent<SpriteRenderer>();
        sr.sprite = full;
        sr.sortingOrder = ResourceNode.BASE_SORTING_ORDER + Mathf.RoundToInt(-pos.y * 10f);

        BoxCollider2D col = go.AddComponent<BoxCollider2D>();
        col.size = new Vector2(0.60f, 0.30f);
        col.offset = new Vector2(0f, 0.15f);

        ResourceNode node = go.AddComponent<ResourceNode>();
        SetSerializedField(node, "resourceType", (int)ResourceType.Coconut);
        SetSerializedField(node, "requiredTool", (int)ToolType.None);
        SetSerializedField(node, "nodeCategory", (int)ResourceCategory.Palm);
        SetSerializedField(node, "nodeSize", (int)ResourceSize.Large);
        SetSerializedField(node, "nodeDisplayName", "Coconut Palm");
        SetSerializedField(node, "yieldAmount", 1);
        SetSerializedField(node, "interactionRange", 1.6f);
        SetSerializedField(node, "availableSprite", full);
        SetSerializedField(node, "depletedSprite", empty);
        SetSerializedField(node, "depleteOnHarvest", true);
        SetSerializedField(node, "destroyOnDeplete", false);
        SetSerializedField(node, "regrowthDuration", 60f);

        node.UpdateSortingOrder();
    }

    private static void CreateBoulder(Vector2 pos, Sprite boulder, Sprite smallPebble, Transform parent)
    {
        GameObject go = new GameObject($"Rock_Boulder_{pos.x:F0}_{pos.y:F0}");
        go.transform.position = new Vector3(pos.x, pos.y, 0f);
        go.transform.SetParent(parent);

        SpriteRenderer sr = go.AddComponent<SpriteRenderer>();
        sr.sprite = boulder;
        sr.sortingOrder = ResourceNode.BASE_SORTING_ORDER + Mathf.RoundToInt(-pos.y * 10f);

        BoxCollider2D col = go.AddComponent<BoxCollider2D>();
        col.size = new Vector2(1.30f, 0.65f);
        col.offset = new Vector2(0f, 0.32f);

        ResourceNode node = go.AddComponent<ResourceNode>();
        SetSerializedField(node, "resourceType", (int)ResourceType.Stone);
        SetSerializedField(node, "requiredTool", (int)ToolType.StonePickaxe);
        SetSerializedField(node, "nodeCategory", (int)ResourceCategory.Rock);
        SetSerializedField(node, "nodeSize", (int)ResourceSize.Large);
        SetSerializedField(node, "nodeDisplayName", "Large Boulder");
        SetSerializedField(node, "yieldAmount", 2);
        SetSerializedField(node, "interactionRange", 1.5f);
        SetSerializedField(node, "availableSprite", boulder);
        SetSerializedField(node, "depletedSprite", smallPebble);
        SetSerializedField(node, "depleteOnHarvest", true);
        SetSerializedField(node, "destroyOnDeplete", false);
        SetSerializedField(node, "regrowthDuration", 90f);

        node.UpdateSortingOrder();
    }

    private static void CreateMediumRock(Vector2 pos, Sprite rock, Transform parent)
    {
        GameObject go = new GameObject($"Rock_Slate_{pos.x:F0}_{pos.y:F0}");
        go.transform.position = new Vector3(pos.x, pos.y, 0f);
        go.transform.SetParent(parent);

        SpriteRenderer sr = go.AddComponent<SpriteRenderer>();
        sr.sprite = rock;
        sr.sortingOrder = ResourceNode.BASE_SORTING_ORDER + Mathf.RoundToInt(-pos.y * 10f);

        BoxCollider2D col = go.AddComponent<BoxCollider2D>();
        col.size = new Vector2(0.70f, 0.35f);
        col.offset = new Vector2(0f, 0.18f);

        ResourceNode node = go.AddComponent<ResourceNode>();
        SetSerializedField(node, "resourceType", (int)ResourceType.Stone);
        SetSerializedField(node, "requiredTool", (int)ToolType.StonePickaxe);
        SetSerializedField(node, "nodeCategory", (int)ResourceCategory.Rock);
        SetSerializedField(node, "nodeSize", (int)ResourceSize.Medium);
        SetSerializedField(node, "nodeDisplayName", "Slate Rock");
        SetSerializedField(node, "yieldAmount", 1);
        SetSerializedField(node, "interactionRange", 1.4f);
        SetSerializedField(node, "availableSprite", rock);
        SetSerializedField(node, "depleteOnHarvest", true);
        SetSerializedField(node, "destroyOnDeplete", true);
        SetSerializedField(node, "regrowthDuration", 60f);

        node.UpdateSortingOrder();
    }

    private static void CreateSmallRock(Vector2 pos, Sprite rock, Transform parent)
    {
        GameObject go = new GameObject($"Rock_Pebble_{pos.x:F0}_{pos.y:F0}");
        go.transform.position = new Vector3(pos.x, pos.y, 0f);
        go.transform.SetParent(parent);

        SpriteRenderer sr = go.AddComponent<SpriteRenderer>();
        sr.sprite = rock;
        sr.sortingOrder = ResourceNode.BASE_SORTING_ORDER + Mathf.RoundToInt(-pos.y * 10f);

        CircleCollider2D col = go.AddComponent<CircleCollider2D>();
        col.radius = 0.25f;
        col.offset = new Vector2(0f, 0.12f);

        ResourceNode node = go.AddComponent<ResourceNode>();
        SetSerializedField(node, "resourceType", (int)ResourceType.Stone);
        SetSerializedField(node, "requiredTool", (int)ToolType.StoneKnife);
        SetSerializedField(node, "nodeCategory", (int)ResourceCategory.Rock);
        SetSerializedField(node, "nodeSize", (int)ResourceSize.VerySmall);
        SetSerializedField(node, "nodeDisplayName", "Small Pebble");
        SetSerializedField(node, "yieldAmount", 1);
        SetSerializedField(node, "interactionRange", 1.3f);
        SetSerializedField(node, "availableSprite", rock);
        SetSerializedField(node, "depleteOnHarvest", true);
        SetSerializedField(node, "destroyOnDeplete", true);
        SetSerializedField(node, "regrowthDuration", 45f);

        node.UpdateSortingOrder();
    }

    private static void CreateBerryBush(Vector2 pos, Sprite full, Sprite empty, Transform parent)
    {
        GameObject go = new GameObject($"Bush_Berry_{pos.x:F0}_{pos.y:F0}");
        go.transform.position = new Vector3(pos.x, pos.y, 0f);
        go.transform.SetParent(parent);

        SpriteRenderer sr = go.AddComponent<SpriteRenderer>();
        sr.sprite = full;
        sr.sortingOrder = ResourceNode.BASE_SORTING_ORDER + Mathf.RoundToInt(-pos.y * 10f);

        BoxCollider2D col = go.AddComponent<BoxCollider2D>();
        col.size = new Vector2(0.65f, 0.35f);
        col.offset = new Vector2(0f, 0.16f);

        ResourceNode node = go.AddComponent<ResourceNode>();
        SetSerializedField(node, "resourceType", (int)ResourceType.Berries);
        SetSerializedField(node, "requiredTool", (int)ToolType.None);
        SetSerializedField(node, "nodeCategory", (int)ResourceCategory.Bush);
        SetSerializedField(node, "nodeSize", (int)ResourceSize.Medium);
        SetSerializedField(node, "nodeDisplayName", "Berry Bush");
        SetSerializedField(node, "yieldAmount", 2);
        SetSerializedField(node, "interactionRange", 1.4f);
        SetSerializedField(node, "availableSprite", full);
        SetSerializedField(node, "depletedSprite", empty);
        SetSerializedField(node, "depleteOnHarvest", true);
        SetSerializedField(node, "destroyOnDeplete", false);
        SetSerializedField(node, "regrowthDuration", 45f);

        node.UpdateSortingOrder();
    }

    private static void CreateFoliageBush(Vector2 pos, Sprite bushSprite, Transform parent, string name)
    {
        GameObject go = new GameObject($"Bush_{name.Replace(" ", "")}_{pos.x:F0}_{pos.y:F0}");
        go.transform.position = new Vector3(pos.x, pos.y, 0f);
        go.transform.SetParent(parent);

        SpriteRenderer sr = go.AddComponent<SpriteRenderer>();
        sr.sprite = bushSprite;
        sr.sortingOrder = ResourceNode.BASE_SORTING_ORDER + Mathf.RoundToInt(-pos.y * 10f);

        BoxCollider2D col = go.AddComponent<BoxCollider2D>();
        col.size = new Vector2(0.60f, 0.30f);
        col.offset = new Vector2(0f, 0.15f);

        ResourceNode node = go.AddComponent<ResourceNode>();
        SetSerializedField(node, "resourceType", (int)ResourceType.Fiber);
        SetSerializedField(node, "requiredTool", (int)ToolType.StoneAxe);
        SetSerializedField(node, "nodeCategory", (int)ResourceCategory.Bush);
        SetSerializedField(node, "nodeSize", (int)ResourceSize.Medium);
        SetSerializedField(node, "nodeDisplayName", name);
        SetSerializedField(node, "yieldAmount", 1);
        SetSerializedField(node, "interactionRange", 1.3f);
        SetSerializedField(node, "availableSprite", bushSprite);
        SetSerializedField(node, "depleteOnHarvest", true);
        SetSerializedField(node, "destroyOnDeplete", true);
        SetSerializedField(node, "regrowthDuration", 45f);

        node.UpdateSortingOrder();
    }

    private static void CreateFiberPlant(Vector2 pos, Sprite plantSprite, Transform parent, string name)
    {
        GameObject go = new GameObject($"Plant_Fiber_{pos.x:F0}_{pos.y:F0}");
        go.transform.position = new Vector3(pos.x, pos.y, 0f);
        go.transform.SetParent(parent);

        SpriteRenderer sr = go.AddComponent<SpriteRenderer>();
        sr.sprite = plantSprite;
        sr.sortingOrder = ResourceNode.BASE_SORTING_ORDER + Mathf.RoundToInt(-pos.y * 10f);

        // Small circle collider for approaching and harvesting (adjusted for shrunk size)
        CircleCollider2D col = go.AddComponent<CircleCollider2D>();
        col.radius = 0.22f;
        col.offset = new Vector2(0f, 0.10f);

        ResourceNode node = go.AddComponent<ResourceNode>();
        SetSerializedField(node, "resourceType", (int)ResourceType.Fiber);
        SetSerializedField(node, "requiredTool", (int)ToolType.StoneKnife);
        SetSerializedField(node, "nodeCategory", (int)ResourceCategory.Bush);
        SetSerializedField(node, "nodeSize", (int)ResourceSize.VerySmall);
        SetSerializedField(node, "nodeDisplayName", name);
        SetSerializedField(node, "yieldAmount", 1);
        SetSerializedField(node, "interactionRange", 1.2f);
        SetSerializedField(node, "availableSprite", plantSprite);
        SetSerializedField(node, "depleteOnHarvest", true);
        SetSerializedField(node, "destroyOnDeplete", true);
        SetSerializedField(node, "regrowthDuration", 45f);

        node.UpdateSortingOrder();
    }

    private static void CreateDriftwood(Vector2 pos, Sprite logSprite, Transform parent)
    {
        GameObject go = new GameObject($"Driftwood_{pos.x:F0}_{pos.y:F0}");
        go.transform.position = new Vector3(pos.x, pos.y, 0f);
        go.transform.SetParent(parent);

        SpriteRenderer sr = go.AddComponent<SpriteRenderer>();
        sr.sprite = logSprite;
        sr.sortingOrder = ResourceNode.BASE_SORTING_ORDER + Mathf.RoundToInt(-pos.y * 10f);

        BoxCollider2D col = go.AddComponent<BoxCollider2D>();
        col.size = new Vector2(0.70f, 0.28f);
        col.offset = new Vector2(0f, 0.14f);

        ResourceNode node = go.AddComponent<ResourceNode>();
        SetSerializedField(node, "resourceType", (int)ResourceType.Wood);
        SetSerializedField(node, "requiredTool", (int)ToolType.StoneAxe);
        SetSerializedField(node, "nodeCategory", (int)ResourceCategory.Log);
        SetSerializedField(node, "nodeSize", (int)ResourceSize.Medium);
        SetSerializedField(node, "nodeDisplayName", "Driftwood Log");
        SetSerializedField(node, "yieldAmount", 2);
        SetSerializedField(node, "interactionRange", 1.3f);
        SetSerializedField(node, "availableSprite", logSprite);
        SetSerializedField(node, "depleteOnHarvest", true);
        SetSerializedField(node, "destroyOnDeplete", true);
        SetSerializedField(node, "regrowthDuration", 60f);

        node.UpdateSortingOrder();
    }

    private static void CreateVerySmallLog(Vector2 pos, Sprite logSprite, Transform parent)
    {
        GameObject go = new GameObject($"Driftwood_Branch_{pos.x:F0}_{pos.y:F0}");
        go.transform.position = new Vector3(pos.x, pos.y, 0f);
        go.transform.SetParent(parent);

        SpriteRenderer sr = go.AddComponent<SpriteRenderer>();
        sr.sprite = logSprite;
        sr.sortingOrder = ResourceNode.BASE_SORTING_ORDER + Mathf.RoundToInt(-pos.y * 10f);

        BoxCollider2D col = go.AddComponent<BoxCollider2D>();
        col.size = new Vector2(0.50f, 0.22f);
        col.offset = new Vector2(0f, 0.11f);

        ResourceNode node = go.AddComponent<ResourceNode>();
        SetSerializedField(node, "resourceType", (int)ResourceType.Wood);
        SetSerializedField(node, "requiredTool", (int)ToolType.StoneKnife);
        SetSerializedField(node, "nodeCategory", (int)ResourceCategory.Log);
        SetSerializedField(node, "nodeSize", (int)ResourceSize.VerySmall);
        SetSerializedField(node, "nodeDisplayName", "Small Log");
        SetSerializedField(node, "yieldAmount", 1);
        SetSerializedField(node, "interactionRange", 1.3f);
        SetSerializedField(node, "availableSprite", logSprite);
        SetSerializedField(node, "depleteOnHarvest", true);
        SetSerializedField(node, "destroyOnDeplete", true);
        SetSerializedField(node, "regrowthDuration", 45f);

        node.UpdateSortingOrder();
    }

    private static MapData ParseMapData(string json)
    {
        MapData data = new MapData();
        var dict = IslandTilemapBuilder.MiniJsonParser.Deserialize(json) as Dictionary<string, object>;
        if (dict == null) return null;

        data.title = dict.ContainsKey("title") ? dict["title"].ToString() : "STRANDED";
        data.width = Convert.ToInt32(dict["width"]);
        data.height = Convert.ToInt32(dict["height"]);

        if (dict.ContainsKey("playerSpawn"))
        {
            var pdict = dict["playerSpawn"] as Dictionary<string, object>;
            data.playerSpawn = new PlayerSpawn
            {
                x = Convert.ToInt32(pdict["x"]),
                y = Convert.ToInt32(pdict["y"])
            };
        }

        if (dict.ContainsKey("tiles"))
        {
            var rowList = dict["tiles"] as List<object>;
            data.tiles = new List<List<int>>(rowList.Count);
            foreach (var r in rowList)
            {
                var colList = r as List<object>;
                List<int> row = new List<int>(colList.Count);
                foreach (var c in colList)
                {
                    row.Add(Convert.ToInt32(c));
                }
                data.tiles.Add(row);
            }
        }

        return data;
    }

    private static void SetSerializedField(Component target, string fieldName, object value)
    {
        SerializedObject so = new SerializedObject(target);
        SerializedProperty prop = so.FindProperty(fieldName);
        if (prop != null)
        {
            if (value is int iVal) prop.intValue = iVal;
            else if (value is float fVal) prop.floatValue = fVal;
            else if (value is bool bVal) prop.boolValue = bVal;
            else if (value is string sVal) prop.stringValue = sVal;
            else if (value is UnityEngine.Object oVal) prop.objectReferenceValue = oVal;
            so.ApplyModifiedPropertiesWithoutUndo();
        }
    }
}
