# Before and after

Full-page captures of the homepage, for the case study and for anyone who
asks what changed.

Take them from the same browser at the same widths, so the pair is a fair
comparison rather than two pictures from different machines weeks apart.

## Naming

```
before-desktop.png     felidaefund.org, full page, desktop width
before-mobile.png      felidaefund.org, full page, 430 x 932
after-desktop.png      the new homepage, same widths
after-mobile.png
```

## How to capture a full page

Chrome: open the page, open devtools, press Cmd+Shift+P, type `screenshot`,
choose **Capture full size screenshot**. That grabs the whole page top to
bottom, not just the visible part.

For the mobile pair, turn on the device toolbar and set 430 x 932 first.

## Timing

The "before" has to be taken **while the old homepage is still live**, which
means before the Phase 2 switch in `joomla-homepage/README.md`. Once the
menu item is repointed, the only way back to that view is a rollback.

The old homepage itself is not lost either way: it stays in the database as
article 1, and `joomla-homepage/BACKUP-home-rendered.html` holds a rendered
copy taken on 12 October.
