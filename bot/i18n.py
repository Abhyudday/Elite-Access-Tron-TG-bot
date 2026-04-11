"""
Internationalisation – English / German translations.
Add new keys here; access via  t(lang, "key")  anywhere.
"""

_TEXTS: dict[str, dict[str, str]] = {
    # ── Language selection ────────────────────────────────────────────
    "choose_language": {
        "en": "🌐 <b>Please choose your language:</b>",
        "de": "🌐 <b>Bitte wählen Sie Ihre Sprache:</b>",
    },
    "language_set": {
        "en": "✅ Language set to English.",
        "de": "✅ Sprache auf Deutsch gesetzt.",
    },

    # ── Welcome ──────────────────────────────────────────────────────
    "welcome_new": {
        "en": (
            "🎉 <b>Welcome to Elite Access!</b>\n\n"
            "Here's how it works:\n"
            "1️⃣ Deposit USDT (TRC20) to your personal deposit address\n"
            "2️⃣ Your balance is credited automatically\n"
            "3️⃣ Invite friends with your referral link and earn commissions on every deposit they make\n\n"
            "To receive referral payouts, make sure to set your <b>TRC20 payout wallet</b> in the 👛 Wallet section.\n\n"
            "Your referral code: <code>{referral_code}</code>\n"
            "Balance: <b>{balance} USDT</b>"
        ),
        "de": (
            "🎉 <b>Willkommen bei Elite Access!</b>\n\n"
            "So funktioniert es:\n"
            "1️⃣ Zahlen Sie USDT (TRC20) auf Ihre persönliche Einzahlungsadresse ein\n"
            "2️⃣ Ihr Guthaben wird automatisch gutgeschrieben\n"
            "3️⃣ Laden Sie Freunde über Ihren Empfehlungslink ein und verdienen Sie Provisionen bei jeder Einzahlung\n\n"
            "Um Empfehlungsprämien zu erhalten, hinterlegen Sie bitte Ihre <b>TRC20-Auszahlungsadresse</b> unter 👛 Wallet.\n\n"
            "Ihr Empfehlungscode: <code>{referral_code}</code>\n"
            "Guthaben: <b>{balance} USDT</b>"
        ),
    },
    "welcome_back": {
        "en": (
            "👋 <b>Welcome back!</b>\n\n"
            "Your referral code: <code>{referral_code}</code>\n"
            "Balance: <b>{balance} USDT</b>"
        ),
        "de": (
            "👋 <b>Willkommen zurück!</b>\n\n"
            "Ihr Empfehlungscode: <code>{referral_code}</code>\n"
            "Guthaben: <b>{balance} USDT</b>"
        ),
    },

    # ── Main menu ────────────────────────────────────────────────────
    "main_menu": {
        "en": "📋 <b>Main Menu</b>\n\nBalance: <b>{balance} USDT</b>",
        "de": "📋 <b>Hauptmenü</b>\n\nGuthaben: <b>{balance} USDT</b>",
    },

    # ── Balance ──────────────────────────────────────────────────────
    "balance": {
        "en": "💰 <b>Your Balance</b>\n\n<b>{balance} USDT</b>",
        "de": "💰 <b>Ihr Guthaben</b>\n\n<b>{balance} USDT</b>",
    },

    # ── Deposit ──────────────────────────────────────────────────────
    "deposit": {
        "en": (
            "📥 <b>Deposit USDT (TRC20)</b>\n\n"
            "Send TRC20 USDT to the address below:\n\n"
            "<code>{address}</code>\n\n"
            "⚠️ <b>Important:</b>\n"
            "• Only send <b>USDT</b> on the <b>TRC20</b> network\n"
            "• Deposits are detected automatically\n"
            "• Minimum deposit: <b>1 USDT</b>\n"
            "• You'll receive a confirmation message once credited"
        ),
        "de": (
            "📥 <b>USDT einzahlen (TRC20)</b>\n\n"
            "Senden Sie TRC20 USDT an die folgende Adresse:\n\n"
            "<code>{address}</code>\n\n"
            "⚠️ <b>Wichtig:</b>\n"
            "• Senden Sie nur <b>USDT</b> im <b>TRC20</b>-Netzwerk\n"
            "• Einzahlungen werden automatisch erkannt\n"
            "• Mindesteinzahlung: <b>1 USDT</b>\n"
            "• Sie erhalten eine Bestätigung, sobald gutgeschrieben"
        ),
    },

    # ── Referral ─────────────────────────────────────────────────────
    "referral": {
        "en": (
            "👥 <b>Referral Program</b>\n\n"
            "Your referral link:\n<code>{ref_link}</code>\n\n"
            "Referral code: <code>{referral_code}</code>\n"
            "Invited: <b>{ref_count}</b> users\n"
            "Total earned: <b>{total_earned} USDT</b>\n\n"
            "Share your link — earn commission on every deposit your referrals make!"
        ),
        "de": (
            "👥 <b>Empfehlungsprogramm</b>\n\n"
            "Ihr Empfehlungslink:\n<code>{ref_link}</code>\n\n"
            "Empfehlungscode: <code>{referral_code}</code>\n"
            "Eingeladen: <b>{ref_count}</b> Nutzer\n"
            "Gesamt verdient: <b>{total_earned} USDT</b>\n\n"
            "Teilen Sie Ihren Link — verdienen Sie Provision bei jeder Einzahlung Ihrer Empfehlungen!"
        ),
    },

    # ── Wallet ───────────────────────────────────────────────────────
    "wallet": {
        "en": (
            "👛 <b>Wallet Settings</b>\n\n"
            "Payout address (TRC20):\n"
            "{payout_display}\n\n"
            "Referral commissions will be sent to this address."
        ),
        "de": (
            "👛 <b>Wallet-Einstellungen</b>\n\n"
            "Auszahlungsadresse (TRC20):\n"
            "{payout_display}\n\n"
            "Empfehlungsprovisionen werden an diese Adresse gesendet."
        ),
    },
    "wallet_prompt": {
        "en": "📝 Please send your <b>TRC20 wallet address</b> for payouts:",
        "de": "📝 Bitte senden Sie Ihre <b>TRC20-Wallet-Adresse</b> für Auszahlungen:",
    },
    "wallet_saved": {
        "en": "✅ Payout wallet saved:\n<code>{address}</code>",
        "de": "✅ Auszahlungs-Wallet gespeichert:\n<code>{address}</code>",
    },
    "wallet_invalid": {
        "en": "❌ Invalid TRC20 address. It should start with <b>T</b> and be 34 characters.",
        "de": "❌ Ungültige TRC20-Adresse. Sie sollte mit <b>T</b> beginnen und 34 Zeichen lang sein.",
    },
    "wallet_not_set": {
        "en": "<i>Not set — tap below to add one</i>",
        "de": "<i>Nicht gesetzt — tippen Sie unten, um eine hinzuzufügen</i>",
    },

    # ── Transactions ─────────────────────────────────────────────────
    "no_transactions": {
        "en": "📋 <b>Transactions</b>\n\nNo transactions yet.",
        "de": "📋 <b>Transaktionen</b>\n\nNoch keine Transaktionen.",
    },
    "transactions_header": {
        "en": "📋 <b>Recent Transactions</b>\n\n",
        "de": "📋 <b>Letzte Transaktionen</b>\n\n",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    """Return localised text. Falls back to English if key/lang missing."""
    entry = _TEXTS.get(key, {})
    text = entry.get(lang, entry.get("en", f"[{key}]"))
    if kwargs:
        text = text.format(**kwargs)
    return text
