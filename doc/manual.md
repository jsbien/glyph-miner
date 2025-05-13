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

When adding a new document, you will need to fill out several metadata fields and upload image files. The form will only allow submission once the required fields are completed.

| Field                | Required | Description                                                                 |
|----------------------|----------|-----------------------------------------------------------------------------|
| **Title**            | Yes      | Title of the document.                                                      |
| Subtitle             | No       | Optional subtitle for the document.                                         |
| Author               | No       | Name of the author or source.                                               |
| Year                 | No       | Year of publication.                                                        |
| Signature            | No       | Optional identifier for the document.                                       |
| Collection           | Optional | Select the collection this document belongs to from existing ones. While not enforced as mandatory by the form, associating documents with a collection is recommended for proper organization and downstream processing. |
| **Image (Color)**    | Yes      | Color image file of the document.                                           |
| **Image (B/W)**      | Yes      | Binarized (black & white) image file of the document.                      |

> The **submit button** remains disabled until the **Title**, **Image (Color)**, and **Image (B/W)** fields are provided.

---

*Generated using source analysis of `document-crud.controller.js` and `document-crud.html`. Validation behavior may be subject to future changes in the implementation.*
