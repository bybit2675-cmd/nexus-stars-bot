# Nexus Stars — Railway deployment

This is a starter Telegram bot project for managing customer sell orders and manually verified USDT payouts.

## Important limitation
Telegram Stars invoices charge a customer Stars to pay the bot; they do not transfer the customer's existing Stars balance to the bot in the way this buying workflow requires. This bot therefore does not fake a transfer or create an invoice for that purpose. The admin must verify Stars receipt through a genuinely supported method before confirming payout. `/stars_total` is only the bot's recorded verified total, not a live Telegram balance.

## Deploy
1. Upload these files to a GitHub repository.
2. In Railway, create a project from that repository.
3. Add Railway Variables:
   - `TELEGRAM_BOT_TOKEN` =8947792850:AAG8Q2FN0FUn5spHoGCXy8RuRzTKr4pQf9Q
   - `ADMIN_TELEGRAM_ID` =5291943945
   - `SUPPORT_CONTACT` = optional, defaults to `@os3ma`
   - `DATABASE_PATH` = optional; for persistence set this to a file path on a mounted Railway volume, e.g. `/data/nexus_stars.sqlite3`
4. Attach a persistent volume mounted at `/data` if using the path above.
5. Deploy. `Procfile` starts a worker with Telegram long polling.

## Features
- Arabic default, English toggle, language saved in SQLite.
- Main menu, manual quantity input (minimum 10), price 0.011 USDT per Star.
- 5% discount for quantities below 50; no discount at 50+.
- BNB Smart Chain address format validation.
- Order creation, admin notification, manual Stars receipt verification, manual payout confirmation.
- Admin-only `/stars_total`.
- Best-effort deletion of temporary user text and edits the bot interface message.

## Safety and production notes
- A valid-looking address is not proof of ownership or network compatibility.
- Never commit tokens or wallet secrets.
- SQLite needs persistent storage or data may be lost after redeployment.
- Review and test the bot before production. Telegram may prevent deletion/editing in some situations.
