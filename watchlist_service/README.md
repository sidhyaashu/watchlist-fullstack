Here is a detailed breakdown of the exact responsibilities of the `market` and `watchlist` folders within your `watchlist_service`, explaining how they work together to power your application.

---

### 1. The `market` Folder
**Core Responsibility:** To act as the "Discovery Engine" and read-only interface to the Accord Fintech financial data (`public` schema). It does not know anything about users, authentication, or watchlists.

#### A. Data Discovery (Search)
*   **The Feature:** Powers the "Add Stock" search bar in the Next.js UI (`InstrumentSearch` component).
*   **The Logic:** When a user types "TATA", the `MarketRepository` queries the `Company_master` table using an `ILIKE` condition on the `SYMBOL` and `COMPNAME` columns.
*   **Enrichment:** It performs a JOIN with the `Nse_Monthprice` table to grab the latest `Close` price so the dropdown can immediately show the user the current price before they even add it to their list.

#### B. Instrument Validation
*   **The Feature:** Prevents users from adding fake or invalid stocks to their watchlist.
*   **The Logic:** When a user clicks "Add" in the UI, the `WatchlistItemService` asks the `MarketService` (via `get_instrument_by_id`) to verify if the `FINCODE` actually exists in the Azure `Company_master` table. If it doesn't, it throws a `BadRequestException`.

#### C. API Boundaries
*   **Endpoints Exposed:** `GET /api/v1/market/search?q={query}`.
*   **Data Returned:** Returns an array of `InstrumentResponse` objects (ID, Symbol, Name, Exchange, Last Price).

---

### 2. The `watchlist` Folder
**Core Responsibility:** To act as the "User State Engine". It manages the creation, deletion, and organization of lists, and is responsible for bridging user data (`app` schema) with the financial data (`public` schema) to deliver a complete dashboard view.

#### A. Watchlist Lifecycle Management (CRUD)
*   **The Feature:** Allows users to create, view, and delete named watchlists (e.g., "Core Bluechips").
*   **The Logic (`WatchlistRepository`):**
    *   Inserts new records into `app.watchlists` using the authenticated `user_id`.
    *   Uses PostgreSQL `pg_advisory_xact_lock` to ensure a user cannot create duplicate lists simultaneously.
    *   Enforces a limit of 10 watchlists per user.
    *   **First-Run Seeding:** If a new user logs in and requests their lists, it detects they have zero lists, automatically creates a default list, and seeds it with real Azure `FINCODEs`.

#### B. Item Management & Ordering
*   **The Feature:** Allows users to add stocks to a list, remove them, and drag-and-drop to reorder them.
*   **The Logic (`WatchlistItemRepository`):**
    *   Inserts mapping records into `app.watchlist_items` (`watchlist_id` + `instrument_id`).
    *   Enforces a unique constraint so a stock cannot be added twice to the same list.
    *   Handles bulk `UPDATE` statements to modify the `position` column when a user drags a stock in the UI.

#### C. The "Heavy-Lifting" Data Aggregation
*   **The Feature:** Delivers the fully populated Watchlist Table to the UI (Price, Day Change, 52W Range, Market Cap, P/E).
*   **The Logic (`WatchlistItemRepository.get_items`):**
    *   This is the most complex function in the service. It starts with the user's saved items in `app.watchlist_items`.
    *   It executes an Outer Join with `public.Company_master` to get the Name, Symbol, and Sector.
    *   It executes a Subquery Join with `public.Nse_Monthprice` to find the exact latest `Open` and `Close` price to calculate the "Day Change %".
    *   It executes an Aggregation Subquery on `public.Nse_Monthprice` to calculate `MAX(high)` and `MIN(low)` for the 52W Range Band.
    *   It executes an Outer Join with `public.company_equity` to get `MCAP` and `TTMPE`.
*   **Formatting:** The `WatchlistItemService` receives this raw SQL data, calculates the percentages in Python, formats the fields, and prepares the final `WatchlistItemResponse`.

#### D. Caching & Performance
*   **The Feature:** Ensures the database is not overwhelmed and the UI remains lightning fast.
*   **The Logic (`WatchlistCache` & `WatchlistItemCache`):**
    *   Every time the `watchlist` folder reads data, it checks Redis first.
    *   Every time the `watchlist` folder writes data (Add/Delete/Reorder), it deletes the specific Redis keys to invalidate the cache.

### Summary
*   The **`market`** folder is a **lightweight, read-only search tool** mapping straight to Accord's data.
*   The **`watchlist`** folder is the **heavy-duty application core**, managing user state, enforcing business rules, performing massive data joins, and handling cache invalidation.