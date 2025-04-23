# Site Audit

## Corotos.com.do
- **Base URL:** https://www.corotos.com.do/inmuebles
- **Captcha / Cloudflare:** Yes ― geo-blocking (the catalog opens only via VPN / proxy)
- **Status:** Blocked. Waiting for client-provided VPN / proxy credentials.

---

## SuperCasas.com
- **Base URL:** https://www.supercasas.com/buscar/
- **Filters (URL parameters):**

  | Parameter                | Example | Meaning / where it is set in UI |
  |--------------------------|---------|----------------------------------|
  | `ObjectType`             | 123     | Property type (123 = Apartment, dropdown **“Tipo de propiedad”**) |
  | `RoomsFrom` / `RoomsTo`  | 1 / 1   | Min / max bedrooms (**“Habitaciones”**) |
  | `BathsFrom` / `BathsTo`  | 1 / 99  | Min / max bathrooms (**“Baños”**) |
  | `PriceType`              | 400     | Currency / price mode (400 = US $) |
  | `PriceFrom` / `PriceTo`  | 0 / 500000000 | Price range (**“Precio desde / hasta”**) |
  | `PagingPageSkip`         | 0, 1, 2…| Pagination offset (0 = first page) |

- **Listing-page CSS selectors:**

  ```css
  #bigsearch-results-inner-results li            /* whole listing card */
  #bigsearch-results-inner-results li a          /* link to detail page */
  #bigsearch-results-inner-results li .title1    /* neighbourhood / area title */
  #bigsearch-results-inner-results li .title2    /* price line e.g. "Venta: US$ …" */
