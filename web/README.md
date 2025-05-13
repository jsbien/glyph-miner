# Web Frontend Notes

This application uses the following UI framework versions:

- **Bootstrap**: 3.3.6 (via CDN)
- **jQuery**: 2.1.4
- **AngularJS**: 1.3.13

Bootstrap tooltips are initialized globally via:

```js
(function () {
  ('[title]').tooltip();
});

(document).ready(function () {
  ('[data-toggle="tooltip"]').tooltip();
});
```

> Tooltip support for disabled buttons is achieved by placing them inside a wrapper with `title` and `data-toggle="tooltip"`.
