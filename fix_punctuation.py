import re

with open('src/content/posts/arbeit-muss-sich-lohnen.md', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace Em Dash (—) with En Dash (–) everywhere
text = text.replace('—', '–')

# Replace closing double quote that matches a German opening quote „
# We look for „ followed by anything that is not a quote, up to a "
text = re.sub(r'„([^"]+)"', r'„\1“', text)

with open('src/content/posts/arbeit-muss-sich-lohnen.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Done.")
