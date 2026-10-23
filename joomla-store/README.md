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

Joomla can only render a module where a position exists, and the nearest one
to the cart is `after-content`, which sits well below the Store Checkout
button and lays its modules out as a flex row. The notice ended up as a
narrow third column that people scrolled straight past.

So the module carries four lines of script that move it up next to the Store
Checkout button, inside the totals panel, which is where someone is standing
when checkout fails. If the button is not on the page, or eShop's markup ever
changes, the script does nothing and the notice stays where Joomla put it.
It cannot break the page either way.

## What it does not fix

The underlying fault. Checkout returns a normal page to a plain HTTP request
with items in the cart, but every browser is redirected back to the shopping
cart. Same machine, same address, logged out, clean profile. That still needs
someone with eShop access.
