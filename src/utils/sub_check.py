import logging
from typing import List
from aiogram import Bot

from db.helper import db_helper
from db.crud import subscription_crud
from .request import RequestUtils

log = logging.getLogger(__name__)


async def get_unsubscribed_chat_links(user_id: int, bot: Bot) -> List[str]:
    """
    Returns a list of chat links that the user is not subscribed to.

    - For open subscriptions, simply check membership.
    - For closed subscriptions, check membership and create a join request link if needed.
    """
    unsubscribed_chat_links: List[str] = []

    async with db_helper.session_factory() as session:
        # Make sure to await the async CRUD methods
        open_links = await subscription_crud.read_all_by_status(
            session=session, status=True
        )
        closed_links = await subscription_crud.read_all_by_status(
            session=session, status=False
        )

    # -------------------------------
    # Handle open subscriptions
    # -------------------------------
    for subscription in open_links:
        chat_id = subscription.chat_id
        try:
            member = await bot.get_chat_member(chat_id, user_id)
            if member.status not in ("member", "administrator", "creator"):
                unsubscribed_chat_links.append(subscription.link)
        except Exception as e:
            log.error(f"Error checking open channel {chat_id}: {e}")
            unsubscribed_chat_links.append(subscription.link)

    # -------------------------------
    # Handle closed subscriptions
    # -------------------------------
    for subscription in closed_links:
        chat_id = subscription.chat_id
        try:
            member = await bot.get_chat_member(chat_id, user_id)
            has_request = RequestUtils.has_request(user_id, chat_id)

            if (
                member.status not in ("member", "administrator", "creator")
                and not has_request
            ):
                # Create a join request link
                link = await bot.create_chat_invite_link(
                    chat_id=chat_id,
                    name="Join via bot approval",
                    creates_join_request=True,
                )
                unsubscribed_chat_links.append(link.invite_link)
        except Exception as e:
            log.error(f"Error checking closed channel {chat_id}: {e}")
            # Try to create the join request link even if membership check fails
            try:
                link = await bot.create_chat_invite_link(
                    chat_id=chat_id,
                    name="Join via bot approval",
                    creates_join_request=True,
                )
                unsubscribed_chat_links.append(link.invite_link)
            except Exception as ex:
                log.error(f"Failed to create link for {chat_id}: {ex}")

    return unsubscribed_chat_links
