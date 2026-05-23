# PROJECT_MEMORY.md

## Project Purpose

This is an async Telegram cargo bot for AK/Akbarshoy cargo workflows. It helps users register, receive a client code, track parcels from China to Tajikistan, view warehouse/pickup information, and request local delivery after a parcel arrives.

Current branding defaults are mixed:
- Runtime settings default `cargo_name` to `Akbarshoy bot`.
- `CLIENT_CODE_PREFIX` defaults to `AK` in `config.py`.
- `.env.example` currently shows a `WS` prefix and a `wasit_cargo` database name.

Verify branding and client-code prefix with the owner before changing user-facing names.

## Architecture

- Python Telegram bot using `aiogram`.
- Entry point: `main.py`.
- Runs with long polling via `Bot.delete_webhook(drop_pending_updates=True)` and `Dispatcher.start_polling`.
- SQLAlchemy async ORM with `asyncpg`; database URL comes from `DATABASE_URL`.
- `database/init_db.py` creates tables with `Base.metadata.create_all` and applies a small warehouse media-column migration.
- No frontend or mini app is present in this repo.
- No OpenAI/AI provider integration is present in the active code.
- No payment or subscription system is present in the active schema or handlers.

## Key Files

- `main.py` - bot startup, router registration, startup DB/settings initialization.
- `config.py` - loads `.env`, reads `BOT_TOKEN`, `DATABASE_URL`, `ADMIN_IDS`, `CLIENT_CODE_PREFIX`, and delivery/price defaults.
- `database/models.py` - SQLAlchemy models.
- `database/db.py` - async engine/session factory.
- `database/init_db.py` - table creation and warehouse media migration.
- `services/settings.py` - DB-backed runtime settings and default seeded settings.
- `services/users.py` - user lookup, registration, login attachment, client code generation.
- `services/parcels.py` - parcel lookup, creation, status updates, notification markers.
- `services/delivery.py` - delivery request creation, admin notification, admin status updates.
- `services/warehouses.py` - warehouse and pickup-location lookup/admin save logic.
- `middlewares/channel_required.py` - optional channel-join gate.
- `handlers/` - aiogram routers for user and admin flows.
- `texts/` - Tajik/Russian UI text.
- `.env.example` - example environment variables only; never put real secrets in it.

## Database Schema Summary

### `users`

Stores Telegram users and cargo client identity.

Important fields:
- `telegram_id`, `username`
- `language`
- `full_name`, `normalized_full_name`
- `phone`
- `city`
- `client_code`
- `status`
- `created_at`, `last_seen`

### `parcels`

Stores parcel tracking records.

Important fields:
- `track_code`, `normalized_track_code`
- `client_code`, `user_id`
- `destination_city`, `destination_warehouse_id`
- `status_code`
- `received_china_at`, `batch_date`
- `china_received_notified_at`, `arrival_notified_at`
- `created_by_admin_id`

### `warehouses`

Stores branch/warehouse media and pickup information.

Important fields:
- `city_key`, `city_name_tj`, `city_name_ru`
- `address_caption`
- `media_type`, `media_file_id`, legacy `image_file_id`
- Tajik pickup fields: `tj_pickup_caption`, `tj_pickup_media_type`, `tj_pickup_media_file_id`
- `is_active`

### `delivery_requests`

Stores local delivery requests created by users after parcel arrival.

Important fields:
- `parcel_id`, `user_id`
- `track_code`, `destination_city`
- `delivery_address`, `delivery_phone`
- `status`
- `handled_by_admin_id`

### `settings`

Stores runtime-configurable bot text and feature flags.

Important keys include:
- `cargo_name`, `cargo_region`, `client_code_prefix`
- price/delivery-day display settings
- `delivery_enabled`
- delivery terms text
- `require_channel_join`, `channel_username`
- operator contact fields
- welcome/prices/status media and text fields

## User Flows

### Start and Auth

- `/start` checks `telegram_id`.
- Existing users go directly to the user main menu.
- New users choose language, then register or log in.
- Registration collects full name and Tajikistan phone number, then assigns a pickup city from active Tajik pickup warehouses.
- Login finds a user by phone, verifies normalized full name, and attaches the current Telegram account.
- Client codes are generated from the DB setting `client_code_prefix`; fallback is `CLIENT_CODE_PREFIX` from env, then `AK`.

### Parcel Tracking

- Users search by track code.
- Track codes are normalized before lookup.
- Status text is formatted through `texts/status.py`.
- Optional per-status media comes from settings via `services/status_media.py`.

### Warehouse/Pickup

- Admins can manage warehouse media/address blocks.
- User-side warehouse display only shows active warehouses that have caption or media content.
- Registration pickup city choices come from active warehouses with Tajik pickup blocks.

### Delivery

- Delivery requests require `delivery_enabled=true`.
- Users can request delivery only for their own parcel with status `arrived_destination`.
- The user submits a delivery address; the bot creates a `delivery_requests` row.
- Admins are notified and can update delivery request status.

### Admin Parcel Management

- Admin access is controlled by `ADMIN_IDS`.
- Admins can add parcels by client code and track code.
- Duplicate normalized track codes are blocked.
- New admin-created parcels start with `china_received` status and can notify the user.
- Bulk status update changes parcels by destination city, batch date, and old status.
- Bulk update to `arrived_destination` sends arrival notifications and marks successful notifications.

### Channel Gate

- `ChannelRequiredMiddleware` can require users to join a configured Telegram channel.
- Feature flag: `require_channel_join`.
- Channel setting: `channel_username`.
- Admins bypass the channel gate.

## Business Logic Notes

- Parcel status constants live in `utils/constants.py`: `china_received`, `on_the_way`, `arrived_destination`, `received`.
- Delivery status constants live in `utils/constants.py`: `new`, `accepted`, `on_delivery`, `delivered`, `cancelled`.
- `destination_city` currently stores a display city name from registration, not always a raw `city_key`; status/bulk logic depends on matching this value.
- Phone normalization stores the last 9 digits and registration validates Tajikistan mobile prefixes.
- Airtable code exists in `services/airtable_sync.py`, but it is currently a placeholder and explicitly must not become the source of truth.

## Required Environment Variables

Never store real values here.

Required:
- `BOT_TOKEN`
- `DATABASE_URL`
- `ADMIN_IDS`

Optional/configurable:
- `CLIENT_CODE_PREFIX`
- `DEFAULT_KG_PRICE_TJS`
- `DEFAULT_CUBE_PRICE_TJS`
- `DEFAULT_DELIVERY_DAYS_TJ`
- `DEFAULT_DELIVERY_DAYS_RU`
- `AIRTABLE_ENABLED`
- `AIRTABLE_API_KEY`
- `AIRTABLE_BASE_ID`

## Known Problems / Risks

- `.env.example` uses `DEFAULT_PRICE_PER_KG_TJS` and `DEFAULT_PRICE_PER_CUBE_TJS`, but `config.py` reads `DEFAULT_KG_PRICE_TJS` and `DEFAULT_CUBE_PRICE_TJS`.
- `services/settings.DEFAULT_SETTINGS` contains duplicate `operator_phone` and `operator_whatsapp` keys.
- `handlers/auth.py` still has debug `print(...)` calls in registration flow.
- `handlers/auth.py` appears to reference `lang` before assignment in `register_phone_command` for slash commands other than `/start` and `/admin` during registration.
- There are no automated tests in the repo at the time of this memory update.

## AI Assistant Rules

- Read `AGENTS.md`, `PROJECT_MEMORY.md`, and `AI_RULES.md` before code changes.
- Make minimal safe changes and preserve existing working logic.
- Do not redesign architecture unless explicitly requested.
- Do not invent payment/subscription/access rules; inspect the current code first.
- Never commit real secrets, bot tokens, database URLs, payment credentials, or private admin data.
- Update this memory only for important architecture, schema, access, payment/subscription, business logic, deployment, or major bug-fix context.
