using System;
using System.IO;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Tilemaps;
using UnityEditor;
using UnityEditor.SceneManagement;

public class IslandTilemapBuilder : EditorWindow
{
    private const string JSON_PATH = "Assets/Art/Terrain/island_world_350.json";
    private const string TILES_FOLDER = "Assets/Art/Terrain/Tiles";

    private class MapData
    {
        public string title;
        public int width;
        public int height;
        public int tileSize;
        public PlayerSpawn playerSpawn;
        public List<List<int>> tiles;
        public Dictionary<string, string> cliffSprites;
    }

    private class PlayerSpawn
    {
        public int x;
        public int y;
    }

    [MenuItem("Tools/STRANDED/Build 350x350 Island & Camera")]
    public static void BuildIslandAndCamera()
    {
        if (!File.Exists(JSON_PATH))
        {
            Debug.LogError($"Map JSON file not found at {JSON_PATH}. Run finalize_island_data.py first!");
            return;
        }

        string scenePath = "Assets/Scenes/MainScene.unity";
        if (File.Exists(scenePath))
        {
            var activeScene = EditorSceneManager.GetActiveScene();
            if (activeScene.path != scenePath)
            {
                EditorSceneManager.OpenScene(scenePath);
            }
        }

        EditorUtility.DisplayProgressBar("STRANDED Island Builder", "Loading map data...", 0.05f);

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
        Debug.Log($"Building STRANDED Island Tilemap: {width}x{height} tiles...");

        // Ensure Tiles asset directory exists
        if (!AssetDatabase.IsValidFolder(TILES_FOLDER))
        {
            AssetDatabase.CreateFolder("Assets/Art/Terrain", "Tiles");
        }

        // 1. Prepare Tile Asset Dictionary
        EditorUtility.DisplayProgressBar("STRANDED Island Builder", "Creating Tile assets...", 0.15f);
        Dictionary<string, TileBase> tileCache = PreloadOrGenerateTiles();

        // 2. Prepare Grid & Tilemap Layers
        EditorUtility.DisplayProgressBar("STRANDED Island Builder", "Setting up Grid and Tilemaps...", 0.30f);
        GameObject gridObj = GameObject.Find("Grid");
        if (gridObj == null)
        {
            gridObj = new GameObject("Grid");
            gridObj.AddComponent<Grid>();
        }

        Tilemap tmDeep = GetOrCreateTilemap(gridObj, "Tilemap_DeepOcean", -20);
        Tilemap tmShallow = GetOrCreateTilemap(gridObj, "Tilemap_ShallowWater", -10);
        Tilemap tmGround = GetOrCreateTilemap(gridObj, "Tilemap_Ground", 0);
        Tilemap tmTransitions = GetOrCreateTilemap(gridObj, "Tilemap_Transitions", 10);
        Tilemap tmRiver = GetOrCreateTilemap(gridObj, "Tilemap_River", 15);
        Tilemap tmCliffs = GetOrCreateTilemap(gridObj, "Tilemap_Cliffs", 20);

        // Clear existing tiles
        tmDeep.ClearAllTiles();
        tmShallow.ClearAllTiles();
        tmGround.ClearAllTiles();
        tmTransitions.ClearAllTiles();
        tmRiver.ClearAllTiles();
        tmCliffs.ClearAllTiles();

        // 3. Batch Population Arrays
        EditorUtility.DisplayProgressBar("STRANDED Island Builder", "Populating Tilemaps (350x350)...", 0.50f);

        List<Vector3Int> posDeep = new List<Vector3Int>();
        List<TileBase> tilesDeep = new List<TileBase>();

        List<Vector3Int> posShallow = new List<Vector3Int>();
        List<TileBase> tilesShallow = new List<TileBase>();

        List<Vector3Int> posGround = new List<Vector3Int>();
        List<TileBase> tilesGround = new List<TileBase>();

        List<Vector3Int> posTrans = new List<Vector3Int>();
        List<TileBase> tilesTrans = new List<TileBase>();

        List<Vector3Int> posRiver = new List<Vector3Int>();
        List<TileBase> tilesRiver = new List<TileBase>();

        List<Vector3Int> posCliffs = new List<Vector3Int>();
        List<TileBase> tilesCliffs = new List<TileBase>();

        TileBase tDeep01 = GetCachedTile(tileCache, "Water/Sea/sea_deep_base_01.png");
        TileBase tDeep02 = GetCachedTile(tileCache, "Water/Sea/sea_deep_base_02.png");
        TileBase tDeepPebbles = GetCachedTile(tileCache, "Water/Sea/sea_deep_pebbles.png");

        TileBase tShallow01 = GetCachedTile(tileCache, "Water/Sea/sea_shallow_base_01.png");
        TileBase tShallow02 = GetCachedTile(tileCache, "Water/Sea/sea_shallow_base_02.png");
        TileBase tShallowStarfish = GetCachedTile(tileCache, "Water/Sea/sea_shallow_starfish.png");
        TileBase tShallowPebbles = GetCachedTile(tileCache, "Water/Sea/sea_shallow_pebbles.png");

        TileBase tShorelineFoam = GetCachedTile(tileCache, "Water/Sea/sea_shoreline_foam.png");

        TileBase tSand01 = GetCachedTile(tileCache, "Sand/sand_base_01.png");
        TileBase tSand02 = GetCachedTile(tileCache, "Sand/sand_base_02.png");
        TileBase tSandSeashell = GetCachedTile(tileCache, "Sand/sand_seashell.png");
        TileBase tSandStarfish = GetCachedTile(tileCache, "Sand/sand_starfish.png");
        TileBase tSandSlate = GetCachedTile(tileCache, "Sand/sand_pebble_slate.png");

        TileBase tGrass01 = GetCachedTile(tileCache, "Grass/grass_base_01.png");
        TileBase tGrass02 = GetCachedTile(tileCache, "Grass/grass_base_02.png");
        TileBase tGrassTuft = GetCachedTile(tileCache, "Grass/grass_tuft_lush.png");
        TileBase tGrassFlowerBlue = GetCachedTile(tileCache, "Grass/grass_wildflower_blue.png");
        TileBase tGrassFlowerPink = GetCachedTile(tileCache, "Grass/grass_wildflower_pink.png");

        TileBase tDirt01 = GetCachedTile(tileCache, "Dirt/mud_base_01.png");
        TileBase tDirt02 = GetCachedTile(tileCache, "Dirt/mud_base_02.png");
        TileBase tMudPebbles = GetCachedTile(tileCache, "Dirt/mud_pebbles.png");
        TileBase tMudCrater = GetCachedTile(tileCache, "Dirt/mud_crater.png");
        TileBase tMudTuft = GetCachedTile(tileCache, "Dirt/mud_tuft.png");

        TileBase tRiver01 = GetCachedTile(tileCache, "Water/River/river_water_base_01.png");
        TileBase tRiverLilypad = GetCachedTile(tileCache, "Water/River/river_lilypad_lotus.png");
        TileBase tRiverReeds = GetCachedTile(tileCache, "Water/River/river_reeds.png");
        TileBase tRiverPebbles = GetCachedTile(tileCache, "Water/River/river_pebbles.png");

        int countMudPebbles = 0, countMudCrater = 0, countMudTuft = 0;
        int countBlueFlowers = 0, countPinkFlowers = 0, countGrassTufts = 0;
        int countSandSeashell = 0, countSandStarfish = 0, countSandSlate = 0;
        int countRiverLilypad = 0, countRiverReeds = 0, countRiverPebbles = 0;
        int countShallowStarfish = 0, countShallowPebbles = 0, countDeepPebbles = 0;

        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                Vector3Int pos = new Vector3Int(x, y, 0);
                int c = mapData.tiles[y][x];

                // 0: Deep, 1: Shallow, 2: Sand, 3: Grass, 4: Dirt, 5: River, 6: Cliff Wall, 7: Cliff Top
                if (c == 0) // OCEAN_DEEP
                {
                    int val = GetTileHash(x, y, 808) % 1000;
                    TileBase deepT;
                    if (val < 5 && tDeepPebbles != null)
                    {
                        deepT = tDeepPebbles;
                        countDeepPebbles++;
                    }
                    else
                    {
                        deepT = (GetTileHash(x, y, 850) % 2 == 0) ? tDeep01 : tDeep02;
                    }
                    posDeep.Add(pos);
                    tilesDeep.Add(deepT);
                }
                else if (c == 1) // OCEAN_SHALLOW
                {
                    int val = GetTileHash(x, y, 707) % 1000;
                    TileBase shallowT;
                    if (val < 10 && tShallowStarfish != null)
                    {
                        shallowT = tShallowStarfish;
                        countShallowStarfish++;
                    }
                    else if (val < 22 && tShallowPebbles != null)
                    {
                        shallowT = tShallowPebbles;
                        countShallowPebbles++;
                    }
                    else
                    {
                        shallowT = (GetTileHash(x, y, 750) % 2 == 0) ? tShallow01 : tShallow02;
                    }
                    posShallow.Add(pos);
                    tilesShallow.Add(shallowT);
                }
                else if (c == 2) // BEACH_SAND
                {
                    int val = GetTileHash(x, y, 404) % 1000;
                    TileBase sandT;
                    if (val < 12 && tSandSeashell != null)
                    {
                        sandT = tSandSeashell;
                        countSandSeashell++;
                    }
                    else if (val < 18 && tSandStarfish != null)
                    {
                        sandT = tSandStarfish;
                        countSandStarfish++;
                    }
                    else if (val < 28 && tSandSlate != null)
                    {
                        sandT = tSandSlate;
                        countSandSlate++;
                    }
                    else
                    {
                        sandT = (GetTileHash(x, y, 450) % 2 == 0) ? tSand01 : tSand02;
                    }
                    posGround.Add(pos);
                    tilesGround.Add(sandT);

                    // Sand to Water transition (water is 0 or 1)
                    string swCode = SolveWang(mapData.tiles, x, y, (val) => val == 0 || val == 1);
                    if (!string.IsNullOrEmpty(swCode))
                    {
                        TileBase tTrans = GetCachedTile(tileCache, $"Transitions/Sand_Water/sand_water_{swCode}.png");
                        if (tTrans != null)
                        {
                            posTrans.Add(pos);
                            tilesTrans.Add(tTrans);
                        }
                    }
                }
                else if (c == 3 || c == 7) // GRASS_BASE or CLIFF_TOP
                {
                    int val = GetTileHash(x, y, 101) % 1000;
                    TileBase grassT;
                    if (val < 8 && tGrassFlowerBlue != null)
                    {
                        grassT = tGrassFlowerBlue;
                        countBlueFlowers++;
                    }
                    else if (val < 16 && tGrassFlowerPink != null)
                    {
                        grassT = tGrassFlowerPink;
                        countPinkFlowers++;
                    }
                    else if (val < 36 && tGrassTuft != null)
                    {
                        grassT = tGrassTuft;
                        countGrassTufts++;
                    }
                    else
                    {
                        grassT = (GetTileHash(x, y, 150) % 2 == 0) ? tGrass01 : tGrass02;
                    }
                    posGround.Add(pos);
                    tilesGround.Add(grassT);

                    // Priority: River > Sand > Dirt
                    string grCode = SolveWang(mapData.tiles, x, y, (val) => val == 5, true, true);
                    if (!string.IsNullOrEmpty(grCode))
                    {
                        TileBase tTrans = GetCachedTile(tileCache, $"Transitions/Grass_RiverWater/grass_riverwater_{grCode}.png");
                        if (tTrans != null)
                        {
                            posTrans.Add(pos);
                            tilesTrans.Add(tTrans);
                        }
                    }
                    else
                    {
                        string gsCode = SolveWang(mapData.tiles, x, y, (val) => val == 2, false);
                        if (!string.IsNullOrEmpty(gsCode))
                        {
                            TileBase tTrans = GetCachedTile(tileCache, $"Transitions/Grass_Sand/grass_sand_{gsCode}.png");
                            if (tTrans != null)
                            {
                                posTrans.Add(pos);
                                tilesTrans.Add(tTrans);
                            }
                        }
                        else
                        {
                            string gdCode = SolveWang(mapData.tiles, x, y, (val) => val == 4, true);
                            if (!string.IsNullOrEmpty(gdCode))
                            {
                                TileBase tTrans = GetCachedTile(tileCache, $"Transitions/Grass_Dirt/grass_dirt_{gdCode}.png");
                                if (tTrans != null)
                                {
                                    posTrans.Add(pos);
                                    tilesTrans.Add(tTrans);
                                }
                            }
                        }
                    }
                }
                else if (c == 4) // DIRT_PATH
                {
                    int val = GetTileHash(x, y, 303) % 1000;
                    TileBase dirtT;
                    if (val < 18 && tMudPebbles != null)
                    {
                        dirtT = tMudPebbles;
                        countMudPebbles++;
                    }
                    else if (val < 32 && tMudTuft != null)
                    {
                        dirtT = tMudTuft;
                        countMudTuft++;
                    }
                    else if (val < 42 && tMudCrater != null)
                    {
                        dirtT = tMudCrater;
                        countMudCrater++;
                    }
                    else
                    {
                        dirtT = (GetTileHash(x, y, 350) % 2 == 0) ? tDirt01 : tDirt02;
                    }
                    posGround.Add(pos);
                    tilesGround.Add(dirtT);

                    // Dirt to River (e.g. crossing ford)
                    string drCode = SolveWang(mapData.tiles, x, y, (val) => val == 5, true, true);
                    if (!string.IsNullOrEmpty(drCode))
                    {
                        TileBase tTrans = GetCachedTile(tileCache, $"Transitions/Dirt_RiverWater/dirt_riverwater_{drCode}.png");
                        if (tTrans != null)
                        {
                            posTrans.Add(pos);
                            tilesTrans.Add(tTrans);
                        }
                    }
                    else
                    {
                        // Dirt to Sand
                        string dsCode = SolveWang(mapData.tiles, x, y, (val) => val == 2, false);
                        if (!string.IsNullOrEmpty(dsCode))
                        {
                            TileBase tTrans = GetCachedTile(tileCache, $"Transitions/Dirt_Sand/dirt_sand_{dsCode}.png");
                            if (tTrans != null)
                            {
                                posTrans.Add(pos);
                                tilesTrans.Add(tTrans);
                            }
                        }
                    }
                }
                else if (c == 5) // RIVER_WATER
                {
                    int val = GetTileHash(x, y, 505) % 1000;
                    TileBase riverT;
                    if (val < 15 && tRiverLilypad != null)
                    {
                        riverT = tRiverLilypad;
                        countRiverLilypad++;
                    }
                    else if (val < 28 && tRiverReeds != null)
                    {
                        riverT = tRiverReeds;
                        countRiverReeds++;
                    }
                    else if (val < 42 && tRiverPebbles != null)
                    {
                        riverT = tRiverPebbles;
                        countRiverPebbles++;
                    }
                    else
                    {
                        riverT = tRiver01;
                    }
                    posRiver.Add(pos);
                    tilesRiver.Add(riverT);
                }
                else if (c == 6) // CLIFF_WALL
                {
                    // Ground underneath
                    posGround.Add(pos);
                    tilesGround.Add(tGrass01);
                }

                // Check for cliff sprite assignment
                string key = $"{x},{y}";
                if (mapData.cliffSprites != null && mapData.cliffSprites.ContainsKey(key))
                {
                    string spriteFile = mapData.cliffSprites[key];
                    TileBase tCliff = GetCachedTile(tileCache, $"Cliffs/{spriteFile}");
                    if (tCliff != null)
                    {
                        posCliffs.Add(pos);
                        tilesCliffs.Add(tCliff);
                    }
                }
            }
        }

        Debug.Log($"[IslandTilemapBuilder] Detail tiles placed:\n" +
            $"- Mud: {countMudPebbles} pebbles, {countMudCrater} craters, {countMudTuft} tufts\n" +
            $"- Grass: {countBlueFlowers} blue wildflowers, {countPinkFlowers} pink wildflowers, {countGrassTufts} grass tufts\n" +
            $"- Sand: {countSandSeashell} seashells, {countSandStarfish} starfish, {countSandSlate} slate pebbles\n" +
            $"- River: {countRiverLilypad} animated lilypads, {countRiverReeds} animated reeds, {countRiverPebbles} animated river pebbles\n" +
            $"- Ocean: {countShallowStarfish} animated shallow starfish, {countShallowPebbles} animated shallow pebbles, {countDeepPebbles} animated deep pebbles");

        // Apply tiles in bulk
        EditorUtility.DisplayProgressBar("STRANDED Island Builder", "Applying tiles to Unity Tilemaps...", 0.80f);
        tmDeep.SetTiles(posDeep.ToArray(), tilesDeep.ToArray());
        tmShallow.SetTiles(posShallow.ToArray(), tilesShallow.ToArray());
        tmGround.SetTiles(posGround.ToArray(), tilesGround.ToArray());
        tmTransitions.SetTiles(posTrans.ToArray(), tilesTrans.ToArray());
        tmRiver.SetTiles(posRiver.ToArray(), tilesRiver.ToArray());
        tmCliffs.SetTiles(posCliffs.ToArray(), tilesCliffs.ToArray());

        // 4. Setup Colliders
        EditorUtility.DisplayProgressBar("STRANDED Island Builder", "Configuring Colliders...", 0.88f);
        SetupTilemapCollider(tmDeep);
        SetupCliffCollider(tmCliffs);

        // 5. Setup Player Position at Starting Camp
        EditorUtility.DisplayProgressBar("STRANDED Island Builder", "Positioning Player & Camera...", 0.94f);
        GameObject player = GameObject.Find("Player");
        Vector3 spawnPos = new Vector3(mapData.playerSpawn.x + 0.5f, mapData.playerSpawn.y + 0.5f, 0f);
        if (player != null)
        {
            player.transform.position = spawnPos;
            SpriteRenderer sr = player.GetComponent<SpriteRenderer>();
            if (sr != null)
            {
                sr.sortingOrder = 100; // Above terrain
            }
        }

        // 6. Setup Exploration Camera
        Camera mainCam = Camera.main;
        if (mainCam != null)
        {
            mainCam.orthographic = true;
            mainCam.orthographicSize = 6.5f;

            ExplorationCamera expCam = mainCam.GetComponent<ExplorationCamera>();
            if (expCam == null)
            {
                expCam = mainCam.gameObject.AddComponent<ExplorationCamera>();
            }

            expCam.SetWorldBounds(new Vector2(0f, 0f), new Vector2(width, height));
            if (player != null)
            {
                expCam.SetTarget(player.transform);
            }

            // Immediately position camera on player spawn
            Vector3 camPos = expCam.CalculateClampedPosition(spawnPos);
            camPos.z = -10f;
            mainCam.transform.position = camPos;
        }

        EditorSceneManager.MarkSceneDirty(EditorSceneManager.GetActiveScene());
        EditorSceneManager.SaveOpenScenes();
        AssetDatabase.SaveAssets();

        EditorUtility.ClearProgressBar();
        Debug.Log($"Successfully built STRANDED 350x350 Island Tilemap with Exploration Camera! Player Spawn: {spawnPos}");
    }

    private static MapData ParseMapData(string json)
    {
        // Custom simple parser or JsonUtility wrapper
        MapData data = new MapData();
        // Since JsonUtility doesn't natively handle List<List<int>> without a wrapper,
        // we parse the JSON structure directly.
        var dict = MiniJsonParser.Deserialize(json) as Dictionary<string, object>;
        if (dict == null) return null;

        data.title = dict.ContainsKey("title") ? dict["title"].ToString() : "STRANDED";
        data.width = Convert.ToInt32(dict["width"]);
        data.height = Convert.ToInt32(dict["height"]);
        data.tileSize = Convert.ToInt32(dict["tileSize"]);

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

        if (dict.ContainsKey("cliffSprites"))
        {
            var csDict = dict["cliffSprites"] as Dictionary<string, object>;
            data.cliffSprites = new Dictionary<string, string>();
            foreach (var kvp in csDict)
            {
                data.cliffSprites[kvp.Key] = kvp.Value.ToString();
            }
        }

        return data;
    }

    private static Tilemap GetOrCreateTilemap(GameObject grid, string name, int sortingOrder)
    {
        Transform child = grid.transform.Find(name);
        GameObject obj;
        if (child == null)
        {
            obj = new GameObject(name);
            obj.transform.SetParent(grid.transform);
            obj.transform.localPosition = Vector3.zero;
        }
        else
        {
            obj = child.gameObject;
        }

        Tilemap tm = obj.GetComponent<Tilemap>();
        if (tm == null) tm = obj.AddComponent<Tilemap>();

        TilemapRenderer tr = obj.GetComponent<TilemapRenderer>();
        if (tr == null) tr = obj.AddComponent<TilemapRenderer>();
        tr.sortingOrder = sortingOrder;

        return tm;
    }

    private static void SetupTilemapCollider(Tilemap tm)
    {
        TilemapCollider2D tc = tm.GetComponent<TilemapCollider2D>();
        if (tc == null) tc = tm.gameObject.AddComponent<TilemapCollider2D>();
        tc.compositeOperation = Collider2D.CompositeOperation.Merge;

        CompositeCollider2D cc = tm.GetComponent<CompositeCollider2D>();
        if (cc == null) cc = tm.gameObject.AddComponent<CompositeCollider2D>();
        cc.geometryType = CompositeCollider2D.GeometryType.Polygons;

        Rigidbody2D rb = tm.GetComponent<Rigidbody2D>();
        if (rb != null)
        {
            rb.bodyType = RigidbodyType2D.Static;
        }
    }

    private static void SetupCliffCollider(Tilemap tm)
    {
        TilemapCollider2D tc = tm.GetComponent<TilemapCollider2D>();
        if (tc == null) tc = tm.gameObject.AddComponent<TilemapCollider2D>();
        tc.compositeOperation = Collider2D.CompositeOperation.Merge;

        CompositeCollider2D cc = tm.GetComponent<CompositeCollider2D>();
        if (cc == null) cc = tm.gameObject.AddComponent<CompositeCollider2D>();
        cc.geometryType = CompositeCollider2D.GeometryType.Polygons;

        Rigidbody2D rb = tm.GetComponent<Rigidbody2D>();
        if (rb != null)
        {
            rb.bodyType = RigidbodyType2D.Static;
        }
    }

    private static Dictionary<string, TileBase> PreloadOrGenerateTiles()
    {
        Dictionary<string, TileBase> cache = new Dictionary<string, TileBase>();
        string[] allPngs = Directory.GetFiles("Assets/Art/Terrain", "*.png", SearchOption.AllDirectories);

        // 1. Force reimport all PNGs so Unity decodes fresh pixels from disk into Library
        foreach (string pngPath in allPngs)
        {
            string cleanPath = pngPath.Replace("\\", "/");
            if (cleanPath.Contains("sheet")) continue;

            TextureImporter ti = AssetImporter.GetAtPath(cleanPath) as TextureImporter;
            if (ti != null)
            {
                bool dirty = false;
                if (ti.textureType != TextureImporterType.Sprite || ti.spriteImportMode != SpriteImportMode.Single ||
                    ti.spritePixelsPerUnit != 16 || ti.filterMode != FilterMode.Point ||
                    ti.textureCompression != TextureImporterCompression.Uncompressed)
                {
                    ti.textureType = TextureImporterType.Sprite;
                    ti.spriteImportMode = SpriteImportMode.Single;
                    ti.spritePixelsPerUnit = 16;
                    ti.filterMode = FilterMode.Point;
                    ti.textureCompression = TextureImporterCompression.Uncompressed;
                    dirty = true;
                }
                if (dirty)
                {
                    ti.SaveAndReimport();
                }
            }
            AssetDatabase.ImportAsset(cleanPath, ImportAssetOptions.ForceUpdate);
        }
        AssetDatabase.Refresh(ImportAssetOptions.ForceUpdate);

        // 2. Generate AnimatedTile assets for water
        // Shallow Sea 01
        AnimatedTile atShallow01 = CreateOrLoadAnimatedTile("sea_shallow_base_01", new string[]
        {
            "Assets/Art/Terrain/Water/Sea/sea_shallow_base_01_f0.png",
            "Assets/Art/Terrain/Water/Sea/sea_shallow_base_01_f1.png",
            "Assets/Art/Terrain/Water/Sea/sea_shallow_base_01_f2.png",
            "Assets/Art/Terrain/Water/Sea/sea_shallow_base_01_f3.png"
        }, Tile.ColliderType.None, 4f);
        cache["Water/Sea/sea_shallow_base_01.png"] = atShallow01;

        // Shallow Sea 02
        AnimatedTile atShallow02 = CreateOrLoadAnimatedTile("sea_shallow_base_02", new string[]
        {
            "Assets/Art/Terrain/Water/Sea/sea_shallow_base_02_f0.png",
            "Assets/Art/Terrain/Water/Sea/sea_shallow_base_02_f1.png",
            "Assets/Art/Terrain/Water/Sea/sea_shallow_base_02_f2.png",
            "Assets/Art/Terrain/Water/Sea/sea_shallow_base_02_f3.png"
        }, Tile.ColliderType.None, 4f);
        cache["Water/Sea/sea_shallow_base_02.png"] = atShallow02;

        // Deep Ocean 01
        AnimatedTile atDeep01 = CreateOrLoadAnimatedTile("sea_deep_base_01", new string[]
        {
            "Assets/Art/Terrain/Water/Sea/sea_deep_base_01_f0.png",
            "Assets/Art/Terrain/Water/Sea/sea_deep_base_01_f1.png",
            "Assets/Art/Terrain/Water/Sea/sea_deep_base_01_f2.png",
            "Assets/Art/Terrain/Water/Sea/sea_deep_base_01_f3.png"
        }, Tile.ColliderType.Grid, 4f);
        cache["Water/Sea/sea_deep_base_01.png"] = atDeep01;

        // Deep Ocean 02
        AnimatedTile atDeep02 = CreateOrLoadAnimatedTile("sea_deep_base_02", new string[]
        {
            "Assets/Art/Terrain/Water/Sea/sea_deep_base_02_f0.png",
            "Assets/Art/Terrain/Water/Sea/sea_deep_base_02_f1.png",
            "Assets/Art/Terrain/Water/Sea/sea_deep_base_02_f2.png",
            "Assets/Art/Terrain/Water/Sea/sea_deep_base_02_f3.png"
        }, Tile.ColliderType.Grid, 4f);
        cache["Water/Sea/sea_deep_base_02.png"] = atDeep02;

        // River Water 01
        AnimatedTile atRiver01 = CreateOrLoadAnimatedTile("river_water_base_01", new string[]
        {
            "Assets/Art/Terrain/Water/River/river_water_base_01_f0.png",
            "Assets/Art/Terrain/Water/River/river_water_base_01_f1.png",
            "Assets/Art/Terrain/Water/River/river_water_base_01_f2.png",
            "Assets/Art/Terrain/Water/River/river_water_base_01_f3.png"
        }, Tile.ColliderType.None, 4f);
        cache["Water/River/river_water_base_01.png"] = atRiver01;

        // Shoreline Foam 01 (Rolling white surf along beach water)
        AnimatedTile atShoreline = CreateOrLoadAnimatedTile("sea_shoreline_foam", new string[]
        {
            "Assets/Art/Terrain/Water/Sea/sea_shoreline_foam_f0.png",
            "Assets/Art/Terrain/Water/Sea/sea_shoreline_foam_f1.png",
            "Assets/Art/Terrain/Water/Sea/sea_shoreline_foam_f2.png",
            "Assets/Art/Terrain/Water/Sea/sea_shoreline_foam_f3.png"
        }, Tile.ColliderType.None, 4f);
        cache["Water/Sea/sea_shoreline_foam.png"] = atShoreline;

        // River Animated Variations: Lilypad Lotus, Reeds, Pebbles
        AnimatedTile atRiverLilypad = CreateOrLoadAnimatedTile("river_lilypad_lotus", new string[]
        {
            "Assets/Art/Terrain/Water/River/river_lilypad_lotus_f0.png",
            "Assets/Art/Terrain/Water/River/river_lilypad_lotus_f1.png",
            "Assets/Art/Terrain/Water/River/river_lilypad_lotus_f2.png",
            "Assets/Art/Terrain/Water/River/river_lilypad_lotus_f3.png"
        }, Tile.ColliderType.None, 4f);
        cache["Water/River/river_lilypad_lotus.png"] = atRiverLilypad;

        AnimatedTile atRiverReeds = CreateOrLoadAnimatedTile("river_reeds", new string[]
        {
            "Assets/Art/Terrain/Water/River/river_reeds_f0.png",
            "Assets/Art/Terrain/Water/River/river_reeds_f1.png",
            "Assets/Art/Terrain/Water/River/river_reeds_f2.png",
            "Assets/Art/Terrain/Water/River/river_reeds_f3.png"
        }, Tile.ColliderType.None, 4f);
        cache["Water/River/river_reeds.png"] = atRiverReeds;

        AnimatedTile atRiverPebbles = CreateOrLoadAnimatedTile("river_pebbles", new string[]
        {
            "Assets/Art/Terrain/Water/River/river_pebbles_f0.png",
            "Assets/Art/Terrain/Water/River/river_pebbles_f1.png",
            "Assets/Art/Terrain/Water/River/river_pebbles_f2.png",
            "Assets/Art/Terrain/Water/River/river_pebbles_f3.png"
        }, Tile.ColliderType.None, 4f);
        cache["Water/River/river_pebbles.png"] = atRiverPebbles;

        // Sea Shallow Animated Variations: Starfish, Pebbles
        AnimatedTile atShallowStarfish = CreateOrLoadAnimatedTile("sea_shallow_starfish", new string[]
        {
            "Assets/Art/Terrain/Water/Sea/sea_shallow_starfish_f0.png",
            "Assets/Art/Terrain/Water/Sea/sea_shallow_starfish_f1.png",
            "Assets/Art/Terrain/Water/Sea/sea_shallow_starfish_f2.png",
            "Assets/Art/Terrain/Water/Sea/sea_shallow_starfish_f3.png"
        }, Tile.ColliderType.None, 4f);
        cache["Water/Sea/sea_shallow_starfish.png"] = atShallowStarfish;

        AnimatedTile atShallowPebbles = CreateOrLoadAnimatedTile("sea_shallow_pebbles", new string[]
        {
            "Assets/Art/Terrain/Water/Sea/sea_shallow_pebbles_f0.png",
            "Assets/Art/Terrain/Water/Sea/sea_shallow_pebbles_f1.png",
            "Assets/Art/Terrain/Water/Sea/sea_shallow_pebbles_f2.png",
            "Assets/Art/Terrain/Water/Sea/sea_shallow_pebbles_f3.png"
        }, Tile.ColliderType.None, 4f);
        cache["Water/Sea/sea_shallow_pebbles.png"] = atShallowPebbles;

        // Sea Deep Animated Variations: Deep Pebbles
        AnimatedTile atDeepPebbles = CreateOrLoadAnimatedTile("sea_deep_pebbles", new string[]
        {
            "Assets/Art/Terrain/Water/Sea/sea_deep_pebbles_f0.png",
            "Assets/Art/Terrain/Water/Sea/sea_deep_pebbles_f1.png",
            "Assets/Art/Terrain/Water/Sea/sea_deep_pebbles_f2.png",
            "Assets/Art/Terrain/Water/Sea/sea_deep_pebbles_f3.png"
        }, Tile.ColliderType.Grid, 4f);
        cache["Water/Sea/sea_deep_pebbles.png"] = atDeepPebbles;

        // Sand-Water Animated Transitions (Lapping foam wave edges on sand boundary)
        string[] swPieces = new string[]
        {
            "edge_n_01", "edge_n_02", "edge_s_01", "edge_s_02", "edge_e", "edge_w",
            "inner_bl", "inner_br", "inner_tl", "inner_tr",
            "outer_bl", "outer_br", "outer_tl", "outer_tr"
        };
        foreach (string piece in swPieces)
        {
            string f0 = $"Assets/Art/Terrain/Transitions/Sand_Water/sand_water_{piece}_f0.png";
            string f1 = $"Assets/Art/Terrain/Transitions/Sand_Water/sand_water_{piece}_f1.png";
            string f2 = $"Assets/Art/Terrain/Transitions/Sand_Water/sand_water_{piece}_f2.png";
            string f3 = $"Assets/Art/Terrain/Transitions/Sand_Water/sand_water_{piece}_f3.png";
            if (File.Exists(f0) && File.Exists(f1) && File.Exists(f2) && File.Exists(f3))
            {
                AnimatedTile atSW = CreateOrLoadAnimatedTile($"sand_water_{piece}", new string[] { f0, f1, f2, f3 }, Tile.ColliderType.None, 4f);
                cache[$"Transitions/Sand_Water/sand_water_{piece}.png"] = atSW;
            }
        }

        // 3. Regular static tiles for terrain, transitions, and cliffs
        foreach (string pngPath in allPngs)
        {
            string cleanPath = pngPath.Replace("\\", "/");
            if (cleanPath.Contains("sheet") || cleanPath.Contains("_f1.") || cleanPath.Contains("_f2.") || cleanPath.Contains("_f3."))
                continue;

            string relKey = cleanPath.Replace("Assets/Art/Terrain/", "");
            if (cache.ContainsKey(relKey))
                continue; // Already assigned as AnimatedTile

            Sprite spr = AssetDatabase.LoadAssetAtPath<Sprite>(cleanPath);
            if (spr == null)
            {
                UnityEngine.Object[] subAssets = AssetDatabase.LoadAllAssetsAtPath(cleanPath);
                foreach (var obj in subAssets)
                {
                    if (obj is Sprite s)
                    {
                        spr = s;
                        break;
                    }
                }
            }

            if (spr == null)
            {
                Debug.LogWarning($"[PreloadOrGenerateTiles] Could not load sprite at {cleanPath}");
                continue;
            }

            string tileAssetName = relKey.Replace("/", "_").Replace(".png", ".asset");
            string tileAssetPath = $"{TILES_FOLDER}/{tileAssetName}";

            Tile tile = AssetDatabase.LoadAssetAtPath<Tile>(tileAssetPath);
            if (tile == null)
            {
                tile = ScriptableObject.CreateInstance<Tile>();
                tile.sprite = spr;
                
                // Mud steps or ramps should be passable (ColliderType.None)
                if (cleanPath.Contains("steps") || cleanPath.Contains("ramp"))
                {
                    tile.colliderType = Tile.ColliderType.None;
                }
                else if (cleanPath.Contains("Cliffs"))
                {
                    tile.colliderType = Tile.ColliderType.Grid;
                }
                else if (cleanPath.Contains("sea_deep"))
                {
                    tile.colliderType = Tile.ColliderType.Grid;
                }
                else
                {
                    tile.colliderType = Tile.ColliderType.None;
                }

                AssetDatabase.CreateAsset(tile, tileAssetPath);
            }
            else
            {
                tile.sprite = spr;
                EditorUtility.SetDirty(tile);
            }

            cache[relKey] = tile;
        }

        AssetDatabase.SaveAssets();
        return cache;
    }

    private static AnimatedTile CreateOrLoadAnimatedTile(string baseName, string[] framePaths, Tile.ColliderType colType, float speed = 4f)
    {
        string tileAssetName = $"Animated_{baseName}.asset";
        string tileAssetPath = $"{TILES_FOLDER}/{tileAssetName}";

        AnimatedTile animTile = AssetDatabase.LoadAssetAtPath<AnimatedTile>(tileAssetPath);
        if (animTile == null)
        {
            animTile = ScriptableObject.CreateInstance<AnimatedTile>();
            AssetDatabase.CreateAsset(animTile, tileAssetPath);
        }

        List<Sprite> sprites = new List<Sprite>();
        foreach (var fp in framePaths)
        {
            Sprite s = AssetDatabase.LoadAssetAtPath<Sprite>(fp);
            if (s != null)
            {
                sprites.Add(s);
            }
        }

        animTile.m_AnimatedSprites = sprites.ToArray();
        animTile.m_MinSpeed = speed;
        animTile.m_MaxSpeed = speed;
        animTile.m_AnimationStartTime = 0f;
        animTile.m_TileColliderType = colType;

        EditorUtility.SetDirty(animTile);
        return animTile;
    }

    private static TileBase GetCachedTile(Dictionary<string, TileBase> cache, string relPath)
    {
        if (cache.TryGetValue(relPath, out TileBase t))
        {
            return t;
        }
        return null;
    }

    private static int GetTileHash(int x, int y, int seed = 1337)
    {
        unchecked
        {
            uint h = ((uint)x * 0x1f1f1f1fu) ^ ((uint)y * 0x5b5b5b5bu) ^ (uint)seed;
            h = ((h >> 16) ^ h) * 0x45d9f3bu;
            h = ((h >> 16) ^ h) * 0x45d9f3bu;
            h = (h >> 16) ^ h;
            return (int)(h & 0x7fffffffu);
        }
    }

    private static string SolveWang(List<List<int>> grid, int x, int y, Func<int, bool> isMatch, bool allowOuter = true, bool isRiverTransition = false)
    {
        int h = grid.Count;
        int w = grid[0].Count;

        bool IsType(int tx, int ty)
        {
            if (tx >= 0 && tx < w && ty >= 0 && ty < h)
            {
                return isMatch(grid[ty][tx]);
            }
            return false;
        }

        bool n = IsType(x, y + 1);
        bool s = IsType(x, y - 1);
        bool wt = IsType(x - 1, y);
        bool e = IsType(x + 1, y);
        bool nw = IsType(x - 1, y + 1);
        bool ne = IsType(x + 1, y + 1);
        bool sw = IsType(x - 1, y - 1);
        bool se = IsType(x + 1, y - 1);

        // 1. Convex corners (neighbor on TWO adjacent cardinal sides)
        if (s && e) return "inner_tl";
        if (s && wt) return "inner_tr";
        if (n && e) return "inner_bl";
        if (n && wt) return "inner_br";

        // 2. Straight edges (neighbor on ONE cardinal side)
        if (isRiverTransition)
        {
            if (s) return (x + y) % 2 == 0 ? "edge_s_01" : "edge_s_02";
            if (n) return (x + y) % 2 == 0 ? "edge_n_01" : "edge_n_02";
            if (e) return "edge_e";
            if (wt) return "edge_w";
        }
        else
        {
            if (s) return (x + y) % 2 == 0 ? "edge_n_01" : "edge_n_02";
            if (n) return (x + y) % 2 == 0 ? "edge_s_01" : "edge_s_02";
            if (e) return "edge_w";
            if (wt) return "edge_e";
        }

        // 3. Concave corners (neighbor ONLY on one diagonal corner)
        if (allowOuter)
        {
            if (sw && !s && !wt) return "outer_tr";
            if (se && !s && !e) return "outer_tl";
            if (nw && !n && !wt) return "outer_br";
            if (ne && !n && !e) return "outer_bl";
        }

        return null;
    }

    #region Simple MiniJSON Parser
    public static class MiniJsonParser
    {
        public static object Deserialize(string json)
        {
            if (json == null) return null;
            return Parser.Parse(json);
        }

        sealed class Parser : IDisposable
        {
            const string WHITE_SPACE = " \t\n\r";
            const string WORD_BREAK = " \t\n\r{}[],:\"";

            StringReader json;

            Parser(string jsonString)
            {
                json = new StringReader(jsonString);
            }

            public static object Parse(string jsonString)
            {
                using (var instance = new Parser(jsonString))
                {
                    return instance.ParseValue();
                }
            }

            public void Dispose()
            {
                json.Dispose();
                json = null;
            }

            Dictionary<string, object> ParseObject()
            {
                Dictionary<string, object> table = new Dictionary<string, object>();
                json.Read(); // {

                while (true)
                {
                    switch (NextToken)
                    {
                        case TOKEN.NONE:
                            return null;
                        case TOKEN.CURLY_CLOSE:
                            return table;
                        case TOKEN.COMMA:
                            continue;
                        default:
                            string name = ParseString();
                            if (name == null) return null;
                            if (NextToken != TOKEN.COLON) return null;
                            json.Read(); // :
                            table[name] = ParseValue();
                            break;
                    }
                }
            }

            List<object> ParseArray()
            {
                List<object> array = new List<object>();
                json.Read(); // [
                var parsing = true;
                while (parsing)
                {
                    TOKEN nextToken = NextToken;
                    switch (nextToken)
                    {
                        case TOKEN.NONE:
                            return null;
                        case TOKEN.SQUARED_CLOSE:
                            parsing = false;
                            break;
                        case TOKEN.COMMA:
                            continue;
                        default:
                            object val = ParseByToken(nextToken);
                            array.Add(val);
                            break;
                    }
                }
                return array;
            }

            object ParseValue()
            {
                TOKEN nextToken = NextToken;
                return ParseByToken(nextToken);
            }

            object ParseByToken(TOKEN token)
            {
                switch (token)
                {
                    case TOKEN.STRING:
                        return ParseString();
                    case TOKEN.NUMBER:
                        return ParseNumber();
                    case TOKEN.CURLY_OPEN:
                        return ParseObject();
                    case TOKEN.SQUARED_OPEN:
                        return ParseArray();
                    case TOKEN.TRUE:
                        return true;
                    case TOKEN.FALSE:
                        return false;
                    case TOKEN.NULL:
                        return null;
                    default:
                        return null;
                }
            }

            string ParseString()
            {
                var s = new System.Text.StringBuilder();
                char c;
                json.Read(); // "
                bool parsing = true;
                while (parsing)
                {
                    if (json.Peek() == -1) break;
                    c = NextChar;
                    switch (c)
                    {
                        case '"':
                            parsing = false;
                            break;
                        case '\\':
                            if (json.Peek() == -1) { parsing = false; break; }
                            c = NextChar;
                            switch (c)
                            {
                                case '"':
                                case '\\':
                                case '/':
                                    s.Append(c);
                                    break;
                                case 'b': s.Append('\b'); break;
                                case 'f': s.Append('\f'); break;
                                case 'n': s.Append('\n'); break;
                                case 'r': s.Append('\r'); break;
                                case 't': s.Append('\t'); break;
                                case 'u':
                                    var hex = new char[4];
                                    for (int i = 0; i < 4; i++) hex[i] = NextChar;
                                    s.Append((char)Convert.ToInt32(new string(hex), 16));
                                    break;
                            }
                            break;
                        default:
                            s.Append(c);
                            break;
                    }
                }
                return s.ToString();
            }

            object ParseNumber()
            {
                string number = NextWord;
                if (number.IndexOf('.') == -1)
                {
                    long.TryParse(number, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out long parsedInt);
                    return parsedInt;
                }
                double.TryParse(number, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out double parsedDouble);
                return parsedDouble;
            }

            void EatWhitespace()
            {
                while (WHITE_SPACE.IndexOf(PeekChar) != -1)
                {
                    json.Read();
                    if (json.Peek() == -1) break;
                }
            }

            char PeekChar => Convert.ToChar(json.Peek());
            char NextChar => Convert.ToChar(json.Read());

            string NextWord
            {
                get
                {
                    var word = new System.Text.StringBuilder();
                    while (WORD_BREAK.IndexOf(PeekChar) == -1)
                    {
                        word.Append(NextChar);
                        if (json.Peek() == -1) break;
                    }
                    return word.ToString();
                }
            }

            TOKEN NextToken
            {
                get
                {
                    EatWhitespace();
                    if (json.Peek() == -1) return TOKEN.NONE;
                    switch (PeekChar)
                    {
                        case '{': return TOKEN.CURLY_OPEN;
                        case '}': json.Read(); return TOKEN.CURLY_CLOSE;
                        case '[': return TOKEN.SQUARED_OPEN;
                        case ']': json.Read(); return TOKEN.SQUARED_CLOSE;
                        case ',': json.Read(); return TOKEN.COMMA;
                        case '"': return TOKEN.STRING;
                        case ':': return TOKEN.COLON;
                        case '0':
                        case '1':
                        case '2':
                        case '3':
                        case '4':
                        case '5':
                        case '6':
                        case '7':
                        case '8':
                        case '9':
                        case '-': return TOKEN.NUMBER;
                    }
                    switch (NextWord)
                    {
                        case "false": return TOKEN.FALSE;
                        case "true": return TOKEN.TRUE;
                        case "null": return TOKEN.NULL;
                    }
                    return TOKEN.NONE;
                }
            }

            enum TOKEN
            {
                NONE,
                CURLY_OPEN,
                CURLY_CLOSE,
                SQUARED_OPEN,
                SQUARED_CLOSE,
                COLON,
                COMMA,
                STRING,
                NUMBER,
                TRUE,
                FALSE,
                NULL
            }
        }
    }
    #endregion
}

[InitializeOnLoad]
public static class IslandBuildTrigger
{
    private const string TRIGGER_FILE = "Assets/Editor/run_build_island.flag";

    static IslandBuildTrigger()
    {
        EditorApplication.delayCall += CheckAndRun;
    }

    private static void CheckAndRun()
    {
        if (File.Exists(TRIGGER_FILE))
        {
            try
            {
                File.Delete(TRIGGER_FILE);
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Could not delete trigger file: {ex.Message}");
            }

            Debug.Log("[IslandBuildTrigger] Trigger flag detected! Executing IslandTilemapBuilder.BuildIslandAndCamera()...");
            IslandTilemapBuilder.BuildIslandAndCamera();
        }
    }
}
