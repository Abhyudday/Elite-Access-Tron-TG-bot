"""
Background worker that periodically checks all tracked deposit addresses
for new incoming USDT transfers, credits balances, processes referral
commissions, and notifies users via Telegram.
"""

import asyncio
import logging

from aiogram import Bot

from blockchain.base import BlockchainProvider
from config import Config
from services.wallet_service import WalletService
from services.deposit_service import DepositService
from services.user_service import UserService
from services.referral_service import ReferralService

logger = logging.getLogger(__name__)


class DepositMonitor:
    """
    Async background loop. Instantiate with a Bot and BlockchainProvider,
    then call `start()` to begin scanning.
    """

    def __init__(self, bot: Bot, provider: BlockchainProvider) -> None:
        self._bot = bot
        self._provider = provider
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """Launch the monitoring loop as a background task."""
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("Deposit monitor started (interval=%ss)", Config.DEPOSIT_CHECK_INTERVAL)

    async def stop(self) -> None:
        """Gracefully stop the monitoring loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Deposit monitor stopped")

    async def _loop(self) -> None:
        """Main scan loop."""
        while self._running:
            try:
                await self._scan_all()
            except Exception:
                logger.exception("Error during deposit scan cycle")
            await asyncio.sleep(Config.DEPOSIT_CHECK_INTERVAL)

    async def _scan_all(self) -> None:
        """Iterate over all deposit addresses and check for new transfers."""
        deposits = await WalletService.get_all_addresses()
        if not deposits:
            return

        logger.debug("Scanning %d deposit addresses", len(deposits))

        for dep in deposits:
            try:
                new_txs = await self._provider.get_deposits(dep.address)
                for tx_info in new_txs:
                    await self._process_deposit(dep.user_telegram_id, tx_info)
            except Exception:
                logger.exception("Error scanning address %s", dep.address)

    async def _process_deposit(self, telegram_id: int, tx_info) -> None:
        """
        Handle a single detected deposit:
        1. Deduplicate by tx_hash
        2. Record transaction
        3. Credit balance
        4. Process referral commission
        5. Notify user
        """
        # 1. Deduplicate
        if await DepositService.tx_exists(tx_info.tx_hash):
            return

        logger.info(
            "New deposit detected: user=%s tx=%s amount=%.4f",
            telegram_id, tx_info.tx_hash, tx_info.amount,
        )

        # 2. Record
        await DepositService.record_deposit(
            telegram_id=telegram_id,
            tx_hash=tx_info.tx_hash,
            amount=tx_info.amount,
        )

        # 3. Credit balance
        new_balance = await UserService.update_balance(telegram_id, tx_info.amount)

        # 4. Referral commission (tiered)
        user = await UserService.get_user(telegram_id)
        if user and user.referred_by:
            commission = await ReferralService.process_commission(
                referrer_id=user.referred_by,
                referee_id=telegram_id,
                deposit_tx_hash=tx_info.tx_hash,
                deposit_amount=tx_info.amount,
            )
            if commission:
                # Attempt on-chain auto-payout
                referrer = await UserService.get_user(user.referred_by)
                payout_tx = None
                if referrer and referrer.payout_address:
                    payout_tx = await self._provider.transfer_usdt(
                        from_user_identifier=telegram_id,
                        to_address=referrer.payout_address,
                        amount=commission.amount,
                    )
                    if payout_tx:
                        # Record the payout tx hash
                        await ReferralService.set_payout_tx(commission.id, payout_tx)
                        logger.info(
                            "Auto-payout OK: commission=%s payout_tx=%s",
                            commission.id, payout_tx,
                        )
                    else:
                        logger.warning(
                            "Auto-payout FAILED for commission %s — will need manual payout",
                            commission.id,
                        )
                elif referrer and not referrer.payout_address:
                    logger.warning(
                        "Referrer %s has no payout_address — commission %s pending",
                        user.referred_by, commission.id,
                    )

                # Notify referrer
                try:
                    payout_note = ""
                    if payout_tx:
                        payout_note = f"\n✅ Sent to your payout wallet!"
                    elif referrer and not referrer.payout_address:
                        payout_note = f"\n⚠️ Set your payout wallet to receive funds on-chain."
                    await self._bot.send_message(
                        user.referred_by,
                        f"💸 <b>Referral commission earned!</b>\n"
                        f"Amount: <b>{commission.amount:.4f} USDT</b> ({commission.commission_pct:.1f}%)\n"
                        f"From a deposit by your referral."
                        f"{payout_note}",
                        parse_mode="HTML",
                    )
                except Exception:
                    logger.warning("Could not notify referrer %s", user.referred_by)

        # 5. Notify depositor
        try:
            await self._bot.send_message(
                telegram_id,
                f"✅ <b>Deposit Confirmed!</b>\n\n"
                f"Amount: <b>{tx_info.amount:.4f} USDT</b>\n"
                f"TX: <code>{tx_info.tx_hash[:24]}…</code>\n"
                f"New balance: <b>{new_balance:.4f} USDT</b>",
                parse_mode="HTML",
            )
        except Exception:
            logger.warning("Could not notify user %s of deposit", telegram_id)
