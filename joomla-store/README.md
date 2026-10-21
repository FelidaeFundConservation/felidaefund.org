# Shopping cart notice

Checkout fails silently: the button sends shoppers back to the cart with no
message. Andrea Bowers emailed to ask why; most people will just leave. This
tells them what to do instead.

`cart-notice.html` goes in a **Custom HTML module**.

## Placing it

1. **Content → Site Modules → New → Custom**
2. **Title:** `Store — checkout notice`
3. **Position:** `after-content`
4. Paste `cart-notice.html` into the editor, in code view
5. **Menu Assignment** → `Only on the pages selected` → tick the **Store** and
   **Shopping Cart** items, nothing else
6. Save

To remove it, unpublish the module. Nothing else is affected: a Custom HTML
module is content on a page and cannot touch the cart, payments or settings.

## Two things to confirm before it goes live

- **The email address.** It is set to `info@felidaefund.org`, taken from the
  contact-form notifications. If the store has its own inbox, change the
  `mailto:` and use that instead.
- **The wording.** Zara owns how this sounds to a customer.

## Placement

`after-content` renders below the cart, under the Store Checkout button, not
above it. The cart page is short so it should still be seen, but if it needs
to sit above the button that is a different position or a CSS change, and
worth checking once it is live.

## What it does not fix

The underlying fault. Checkout returns a normal page to a plain HTTP request
with items in the cart, but every browser is redirected back to the shopping
cart. Same machine, same address, logged out, clean profile. That still needs
someone with eShop access.
