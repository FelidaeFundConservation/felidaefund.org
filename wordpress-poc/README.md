# WordPress proof of concept

A block child theme that rebuilds the redesigned Felidae homepage in WordPress.

- Theme: `felidae-child` (version 1.0.3)
- Parent theme: Twenty Twenty-Five (ships with WordPress, not included here)
- Built and tested locally with LocalWP

## What's in here

Only the child theme. WordPress itself, the database, and site config
(`wp-config.php`) are not in this repo and should never be added.

## Install

1. Use any WordPress 6.x site with the Twenty Twenty-Five theme installed.
2. Copy `felidae-child/` into `wp-content/themes/`.
3. In WordPress admin, go to Appearance → Themes and activate **Felidae Child**.

The homepage comes from the theme's front-page template and the
`felidae-homepage` pattern, so it appears without importing any content.

## Known gaps

- Images load from felidaefund.org and Unsplash rather than from files in the theme.
