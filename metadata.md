# Metadata

The nhentai metadata has the following structure:

```json
{
    "id": 0,
    "media_id": "0",
    "title": {
        "english": "english title",
        "japanese": "japanese title",
        "pretty": "pretty title"
    },
    "images": {
        "pages": [
            {
                "t": "w",
                "w": 1280,
                "h": 800
            }
        ],
        "cover": {
            "t": "w",
            "w": 350,
            "h": 494
        },
        "thumbnail": {
            "t": "w",
            "w": 250,
            "h": 353
        }
    },
    "scanlator": "",
    "upload_date": 0,
    "tags": [
        {
            "id": 0,
            "type": "tag",
            "name": "tag-name",
            "url": "/tag/tag-name/",
            "count": 0
        }
    ],
    "num_pages": 0,
    "num_favorites": 0
}
```

## Conversion table

| NHentai metadata | ComicInfo.xml | Description |
| ---------------- | ------------- | ----------- |
| id               |||
| media_id         |||
| english title    |||
| japanese title   |||
| pretty title     |||
| images           |||
| tags             |||
