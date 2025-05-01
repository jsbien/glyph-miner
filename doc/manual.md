# Glyph Miner: Adding Collections and Documents

This guide explains the fields required when adding new collections and documents in the Glyph Miner web interface, accessible via `http://localhost:9090/#/overview`.

## Add New Collection

To create a new collection, go to the **Overview** page and use the **Add new collection** form. Only the **Title** field is mandatory.

| Field         | Required | Description                                                                 |
|---------------|----------|-----------------------------------------------------------------------------|
| **Title**     | Yes      | The main title of the collection. Must be filled in to enable form submit. |
| Subtitle      | No       | An optional subtitle providing further context or clarification.            |
| Author        | No       | Name(s) of the person(s) or institution responsible for the collection.     |
| Year          | No       | The year the collection was created or published.                          |
| Signature     | No       | An optional unique identifier or catalog signature for the collection.      |

## Add New Document

When adding a document, several fields and image uploads are involved. The form requires the following:

| Field                | Required | Description                                                                 |
|----------------------|----------|-----------------------------------------------------------------------------|
| **Title**            | Yes      | Title of the document.                                                      |
| Subtitle             | No       | Optional subtitle for the document.                                         |
| Author               | No       | Name of the author or source.                                               |
| Year                 | No       | Year of publication.                                                        |
| Signature            | No       | Optional identifier for the document.                                       |
| Collection           | No       | A collection this document belongs to (selectable from existing ones).      |
| **Image (Color)**    | Yes      | Color image file of the document.                                           |
| **Image (B/W)**      | Yes      | Binarized (black & white) image file of the document.                      |

The submit button is disabled unless the title is filled and both image files are selected.

---

*Generated using source analysis of `document-crud.controller.js` and `document-crud.html`.*
