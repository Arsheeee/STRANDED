using System;
using UnityEngine;
using UnityEngine.Tilemaps;

[CreateAssetMenu(fileName = "New Animated Tile", menuName = "2D/Tiles/Animated Tile")]
public class AnimatedTile : TileBase
{
    [SerializeField]
    public Sprite[] m_AnimatedSprites;

    [SerializeField]
    public float m_MinSpeed = 4f;

    [SerializeField]
    public float m_MaxSpeed = 4f;

    [SerializeField]
    public float m_AnimationStartTime = 0f;

    [SerializeField]
    public Tile.ColliderType m_TileColliderType = Tile.ColliderType.None;

    public override void GetTileData(Vector3Int location, ITilemap tilemap, ref TileData tileData)
    {
        tileData.transform = Matrix4x4.identity;
        tileData.color = Color.white;
        if (m_AnimatedSprites != null && m_AnimatedSprites.Length > 0)
        {
            tileData.sprite = m_AnimatedSprites[0];
            tileData.colliderType = m_TileColliderType;
        }
        else
        {
            tileData.sprite = null;
            tileData.colliderType = Tile.ColliderType.None;
        }
    }

    public override bool GetTileAnimationData(Vector3Int location, ITilemap tilemap, ref TileAnimationData tileAnimationData)
    {
        if (m_AnimatedSprites != null && m_AnimatedSprites.Length > 0)
        {
            tileAnimationData.animatedSprites = m_AnimatedSprites;
            tileAnimationData.animationSpeed = m_MinSpeed;
            tileAnimationData.animationStartTime = m_AnimationStartTime;
            return true;
        }
        return false;
    }
}
