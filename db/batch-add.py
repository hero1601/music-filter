import pandas as pd
import re

def thumbnail_to_link(thumbnail_url):
    
    match = re.search(r'/vi/([^/]+)/', thumbnail_url)
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/watch?v={video_id}"
    return None

df = pd.read_csv("./data/bollywood-songs.csv")

# Extract unique songs with their info and assign IDs
songs = df[['music_name', 'singer', 'thumbnail']].drop_duplicates().reset_index(drop=True)
songs.rename(columns={'thumbnail': 'external_link','music_name':'title', 'singer':'artist'}, inplace=True)
songs['song_id'] = songs.index + 1  # 1-based IDs
songs['external_link'] = songs['external_link'].apply(thumbnail_to_link)

# Create a lookup dict to get song_id by (title, artist, external_link)
song_key_to_id = {
    (row.title, row.artist): row.song_id
    for _, row in songs.iterrows()
}

lyrics_rows = []
for _, row in df.iterrows():
    if pd.isna(row['lyrics']):
        continue

    key = (row['music_name'], row['singer'])
    song_id = song_key_to_id.get(key)
    if not song_id:
        continue

    # Split on two or more spaces
    lines = re.split(r'\s{2,}', row['lyrics'])
    lines = [line.strip() for line in lines if line.strip()]

    for line_number, line in enumerate(lines, start=1):
        lyrics_rows.append({
            'song_id': song_id,
            'line_number': line_number,
            'lyric_line': line
        })

lyrics_df = pd.DataFrame(lyrics_rows)

songs.to_csv('./data/songs.csv', index=False)
lyrics_df.to_csv('./data/lyrics.csv', index=False)


# Command to add
# \copy songs(title, artist, external_link) FROM '/local/path/songs.csv' CSV HEADER
# \copy lyrics(song_id, line_number, lyric_line) FROM '/local/path/lyrics.csv' CSV HEADER





