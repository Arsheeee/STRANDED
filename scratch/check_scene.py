import re

current_tag = None
current_lines = 0
largest_blocks = []

with open('Assets/Scenes/MainScene.unity', 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('--- !u!'):
            if current_tag:
                largest_blocks.append((current_lines, current_tag))
            current_tag = line.strip()
            current_lines = 1
        else:
            current_lines += 1

if current_tag:
    largest_blocks.append((current_lines, current_tag))

largest_blocks.sort(key=lambda x: x[0], reverse=True)
print("Top 10 largest blocks in MainScene.unity:")
for lines, tag in largest_blocks[:10]:
    print(f"  {lines} lines: {tag}")
