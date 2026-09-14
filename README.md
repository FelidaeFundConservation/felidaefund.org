# felidaefund.org redesign

Working repo for the redesigned felidaefund.org.
The live site runs on Joomla and is not affected by anything in here.

## What's in here

- `prototype/` is the homepage prototype, shown at felidae-redesign.vercel.app
- `wordpress-poc/` is for the WordPress proof of concept

## Current status

- `prototype/index.html` matches the deployed page from 12 Sept 2026. All images are stored locally in `prototype/assets/`; the page no longer loads images from the live felidaefund.org site (its links still point there).
- Not connected to Vercel yet. When it is, set the Vercel root directory to `prototype`.
- `wordpress-poc/` holds the `felidae-child` block theme (see `wordpress-poc/README.md`). WordPress core, the database, and `wp-config.php` are not in the repo.

## Please don't commit

- `wp-config.php` or anything with passwords, keys, or database credentials
