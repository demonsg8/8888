from telethon import TelegramClient, events
import logging
from telethon.tl import types
from telethon.tl.types import DocumentAttributeAnimated
import random
from telethon.tl.functions.channels import GetParticipantsRequest
import requests
from telethon.sync import TelegramClient, events
from telethon.tl.types import ChannelParticipantsSearch
from time import sleep
import asyncio
from telethon.tl.types import MessageEntityEmail, MessageEntityPhone, MessageEntityUrl, MessageEntityCashtag
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import User
from telethon.tl.functions.messages import GetCommonChatsRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon import TelegramClient, events
from telethon.tl.types import InputPeerEmpty
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import Channel, InputPeerChannel, ChannelParticipantsAdmins, User
from telethon.tl.functions.channels import GetFullChannelRequest
from pprint import pprint
from telethon.tl.types import Channel, ChatPhoto
from telethon.tl.functions.messages import CheckChatInviteRequest
from telethon.tl.types import InputPeerChannel, Channel
import os
import io
import json
import random
import re
from asyncio import sleep
from collections import Counter
import aiohttp
import datetime

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram API credentials
api_id = '28499234'
api_hash = '38788141e6344875b10d3b39937ec5fe'
client = TelegramClient('lootstacker', api_id, api_hash)

CONFIG_FILE = 'config.json'

# Default config structure
default_config = {
    "log_channel": -1002611788106,
    "specific_user_logs": [],
    "whitelist": [6018548705, 6672038435, 5972356225],
    "USER_LOG_CHANNELS": {
        "6018548705": -1002570801078
    },
    "TOGGLES": {
        "bot_enabled": True,
        "forward_metadata": True,
        "enabled_commands": ["/help", "/dox", "/count", "/snus"]
    }
}

# Ensure config file exists and load it
def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=4)
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# Load config and extract values
config = load_config()
WHITE_LIST = config.get("whitelist", [])
GROUP_ID = int(config.get("log_channel", -1001234567890))
USER_LOG_CHANNELS = {int(uid): int(gid) for uid, gid in config.get("USER_LOG_CHANNELS", {}).items()}
TOGGLES = config.get("TOGGLES", {
    "bot_enabled": True,
    "forward_metadata": True,
    "enabled_commands": []
})

def filter_sensitive_information(message_text):
    keywords = ["stevo", "kush", "email", "phone", "name", "ssn", "💯", "sinister", "credit card", "threatsec", "tlo", "ddos", "com", "bfc", "717", "weep", "smith", "name", "yuri", "steven", "jews", "kike","groom", "weed", "coke", "meth", "shrooms", "mushrooms", "i am", "I am", "years", "year old", "snuff", "vile", "KT" "new gen", "admin", "simswap", "up2nogood", "Up2NoGood", "sim",  "telegram", "cupcake", "swap", "wayne", "rabid", "@elder", "@doxinglegend", "@hateful", "newfag", "fullz", "newgen", "nigger", "bot", "og", "dox", "doxbin", "based", "opsec", "schizo", "swat", "nft", "fed", "porn", "masturbate", "jerk off", "paedo", "mimi", "eva14" "eva 14", "poor", "emi", "skid", "xav", "esex", "extort", "rape", "cp", "spam", "warned", "/ban", "john", "John Smith", "vz", "Daddy", "cunny", "esex", "dick", "pussy", "cock", "penis", "cunt", "rapist", "doxbin", "Max", "764", "Matt", 'Nikita', 'fraud', 'att', 'at&t', 'tmo', "hodl", 'swap', 'stalkers','pedo']  # add keywords to filter sensitive information
    message_text_lower = message_text.lower()
    for keyword in keywords:
        if keyword in message_text_lower:
            return True
    return False

SPECIFIC_USER_IDS = [""]  # add specific user ids

GROUP_ID = -1002611788106  # your group ID



pool_of_messages = [
    
    ]  # predefined text messages to reply


@client.on(events.NewMessage)
async def handle_messages(event):
    if not TOGGLES.get("bot_enabled", True):  # Check if bot is enabled
        return

    message = event.message
    user = await event.get_sender()
    user_id = user.id
    username = f"@{user.username}" if user.username else "None"
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    message_text = message.text or ""
    timestamp = message.date
    chat_title = event.chat.title if event.chat else "Private Chat"

    # Extract message entities (like mentions, hashtags, etc.)
    entities_list = []
    if message.entities:
        for entity in message.entities:
            entity_text = message.text[entity.offset: entity.offset + entity.length]
            entities_list.append(f"{entity.__class__.__name__}: {entity_text}")

    entities_info = ", ".join(entities_list) if entities_list else "No entities"

    # Generate message link
    message_link = f"https://t.me/c/{abs(event.chat_id) % 10000000000}/{message.id}"

    # Forward message to the main log channel
    await client.forward_messages(GROUP_ID, message)

    # Forward to user's specific log channel if configured
    if user_id in USER_LOG_CHANNELS:
        await client.forward_messages(USER_LOG_CHANNELS[user_id], message)

    # Send metadata if enabled
    if TOGGLES.get("forward_metadata", True):
        metadata = (
            f"📩 Message Metadata\n"
            f"User ID: #id{user_id}\n"
            f"Username: {username}\n"
            f"Name: {full_name}\n"
            f"Chat: {chat_title}\n"
            f"Timestamp: {timestamp}\n"
            f"Message: {message_text}\n"
            f"Message Link: {message_link}\n"
            f"Message Entities: {entities_info}"
        )
        await client.send_message(GROUP_ID, metadata)
        if user_id in USER_LOG_CHANNELS:
            await client.send_message(USER_LOG_CHANNELS[user_id], metadata)

    # Check for sensitive information in messages from all users
    if filter_sensitive_information(message_text):
        info = f"⚠️ Flagged Key Word Message:\n"
        info += f"User ID: #id{user_id}\n"
        info += f"Username: {username}\n"
        info += f"Name: {full_name}\n"
        info += f"Chat: {chat_title}\n"
        info += f"Timestamp: {timestamp}\n"
        info += f"Message: {message_text}\n"
        info += f"Message Link: {message_link}\n"
        info += f"Message Entities: {entities_info}\n"
        
        logger.info(f"Flagged message: {info}")

        # Forward the flagged message to the destination users
        await client.forward_messages(GROUP_ID, message)

        # Send the info about the flagged message to the destination users
        await client.send_message(GROUP_ID, info)

    else:
        logger.info(f"Non-flagged message: User ID: {user_id}, Username: {username}, Name: {full_name}, Timestamp: {timestamp}, Message: {message_text}, Message Entities: {entities_info}")


# This function updates the set of group members
async def update_group_members():
    global group_members
    offset = 0
    limit = 100
    while True:
        participants = await client(GetParticipantsRequest(
            GROUP_ID, ChannelParticipantsSearch(''), offset, limit, hash=0
        ))
        if not participants.users:
            break
        for user in participants.users:
            group_members.add(user.id)
        offset += len(participants.users)

# Run this function once to initialize the set of group members
    await update_group_members()

# This function checks for users leaving the group
async def check_for_leavers():
    while True:
        old_group_members = group_members.copy()
        await update_group_members()
        leavers = old_group_members - group_members
        for user_id in leavers:
            # Get user details
            user = await client.get_entity(user_id)
            username = user.username if user.username else "None"
            first_name = user.first_name if user.first_name else "None"
            last_name = user.last_name if user.last_name else "None"

            info = f"User Left:\n"
            info += f"Chat Title: {group_id}\n"
            info += f"User ID: #id{user_id}\n"
            info += f"Username: {username}\n"
            info += f"First Name: {first_name}\n"
            info += f"Last Name: {last_name}\n"
            info += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S%z')}\n"  # Get the current time
            logger.info(info)
            await client.send_message(GROUP_ID, info)
        # Wait for a while before checking again
        sleep(60)

# Run this function in the background
client.loop.create_task(check_for_leavers())

@client.on(events.ChatAction)
async def handle_user_joins(event):
    # Get user info
    user = await client.get_entity(event.user_id)
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    timestamp = event.action_message.date.strftime("%Y-%m-%d %H:%M:%S%z")  # Corrected here

    user_info = f"Chat Title: {event.chat.title}\nChannel / Group ID: #-{abs(event.chat_id)}\nUser ID: #id{event.user_id}\nUsername: {username}\nFirst Name: {first_name}\nLast Name: {last_name}\nTimestamp: {timestamp}"

    # User was added
    if event.user_added or event.user_joined:
        invited_by_id = event.action_message.action.inviter_id
        # ...
        user_info = f"""
User invited by #{invited_by_id}:
Chat Title: {event.chat.title}
Channel / Group ID: #{event.chat.id}
User ID: #id{event.user_id}
Username: @{event.user.username}
First Name: {event.user.first_name}
Last Name: {event.user.last_name}
Timestamp: {event.date.strftime("%Y-%m-%d %H:%M:%S%z")}
        """

    # User joined by themselves
    elif event.user_joined:
        message = f"User Joined:\n{user_info}"
        logger.info(message)
        await client.send_message(GROUP_ID, message)

    # User left the group
    elif event.user_left or event.user_kicked:
        message = f"User Left:\n{user_info}"
        logger.info(message)
        await client.send_message(GROUP_ID, message)
        if event.user_id in leave_counter:
            leave_counter[event.user_id] += 1
        else:
            leave_counter[event.user_id] = 1
        message = f"{user_info} has left groups {leave_counter[event.user_id]} times"
        logger.info(message)
        await client.send_message(GROUP_ID, message)


#	client.on(events.NewMessage(pattern='@client.on(events.NewMessage(pattern=r'(?i).*	tunnel.*'))tunnel'))
#@client.on(events.NewMessage(pattern=r'(?i)tunnel'))
@client.on(events.NewMessage(pattern=r'(?i).*tunnel.*'))
async def tunnel(event):
    user_id = event.message.sender_id
    if user_id:
        await client.send_file(event.chat_id, 'tunnel.gif', caption='tunnel time.')
    else:
        await event.respond('Sorry, you are not allowed to use this command.')

@client.on(events.NewMessage(pattern='/help'))
async def help(event):
    user_id = event.message.sender_id
    if user_id in WHITE_LIST:
        dialogs = await client.get_dialogs()
        count = len(dialogs)
        await event.respond(f'Current commands: /help, /dox, /count, /mutuals, /snus')
    else:
        await event.respond('Sorry, you are not allowed to use this command.')


@client.on(events.NewMessage(pattern='/snus'))
async def snus_search(event):
    user_id = event.message.sender_id
    if user_id not in WHITE_LIST:
        await event.reply("")
        return

    search_term = event.message.raw_text.split("/snus ", 1)[1]

    if not search_term:  # check if the search term is provided
        await event.reply("Please provide a search term.")
        return

    # Inform the user about the usage of Combo List API for Snus Base
    info_message = "Searching using the combo list API..."
    await event.reply(info_message)

    async with aiohttp.ClientSession() as session:
        url = f"https://beta.snusbase.com/v2/combo/{search_term}"
        async with session.get(url) as resp:
            if resp.status == 200:
                response = await resp.json()
                # now format the response and send it back to the user
                response_message = json.dumps(response, indent=4)
                
                # check if the message exceeds Telegram's limit
                if len(response_message) > 4096:
                    # write to a file and send it
                    file_name = f"{search_term}.txt"
                    with open(file_name, 'w') as f:
                        f.write(response_message)
                    await event.respond(file=file_name)
                    os.remove(file_name)  # delete the file after sending
                else:
                    # if the message is short enough, send as text
                    await event.reply(response_message)
            else:
                await event.reply(f"An error occurred: {resp.status}")



@client.on(events.NewMessage(pattern='/tunnel'))
async def tunnel(event):
    user_id = event.message.sender_id
    if user_id in WHITE_LIST:
        await client.send_file(event.chat_id, '~/tunnel.gif', caption='tunnel time.')
    else:
        await event.respond('Sorry, you are not allowed to use this command.')

@client.on(events.NewMessage(pattern='/help'))
async def help(event):
    user_id = event.message.sender_id
    if user_id in WHITE_LIST:
        dialogs = await client.get_dialogs()
        count = len(dialogs)
        await event.respond(f'Current commands: /help, /dox, /count, /mutuals, /snus')
    else:
        await event.respond('Sorry, you are not allowed to use this command.')


@client.on(events.NewMessage(pattern='/mason_foxworth2'))
async def count_chats(event):
    user_id = event.message.sender_id
    if user_id in WHITE_LIST:
        dialogs = await client.get_dialogs()
        count = len(dialogs)
        await event.respond(f'I am in {count} chats.')
    else:
        await event.respond('Sorry, you are not allowed to use this command.')

@client.on(events.NewMessage)
async def email_phone_url_forwarder(event):
    message = event.message

    # Set message.entities to an empty list if it's None
    entities = message.entities or []

    for entity in entities:
        if isinstance(entity, (MessageEntityEmail, MessageEntityPhone, MessageEntityUrl, MessageEntityCashtag)):
            user = message.sender
            user_info = f"""
Message contains {entity.__class__.__name__.replace('MessageEntity', '').lower()}:
Chat Title: {message.chat.title}
User ID: #id{user.id}
Username: @{user.username}
First Name: {user.first_name}
Last Name: {user.last_name}
Timestamp: {message.date.strftime("%Y-%m-%d %H:%M:%S%z")}
Message: {message.text}
Message Link: https://t.me/c/{message.chat.id}/{message.id}
Message Entities: {entity.__class__.__name__}: {message.text[entity.offset:entity.offset+entity.length]}
            """
            await client.send_message(GROUP_ID, user_info)

# Your existing event handler
@client.on(events.NewMessage(pattern="/mutualgroups"))
async def mutual_groups(event):
    user_id = event.sender_id
    if user_id not in WHITE_LIST:
        return  # Ignore non-whitelisted users

    args = event.message.text.split()
    if len(args) < 2:
        await event.reply("Please provide the target user ID.")
        return

    try:
        target_user_id = int(args[1])  # Assumes the command is /mutualgroups USER_ID
        target_user = await client.get_entity(target_user_id)
    except ValueError:
        await event.reply("Invalid user ID provided.")
        return
    except Exception as e:
        await event.reply(f"An error occurred: {str(e)}")
        return

    try:
        mutual_groups = await client(GetCommonChatsRequest(user_id=target_user_id, max_id=0, limit=100))
        # Format and send the list of mutual groups
        response = f"User ID: #id{target_user_id}\n"
        response += f"Username: @{target_user.username}\n"

        if not isinstance(target_user, types.Channel):  # Check if the target user is not a channel
            response += f"First Name: {target_user.first_name}\n"
            response += f"Last Name: {target_user.last_name or 'None'}\n"

        response += f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S%z')}\n"
        response += f"Mutual Groups ({len(mutual_groups.chats)} shared):\n"  # Display the number of shared groups
        
        for group in mutual_groups.chats:
            try:
                invite_link = await client(ExportChatInviteRequest(group.id))
                response += f'- <a href="{invite_link.link}">{group.title}</a>\n'
            except:
                response += f"- {group.title} (No invite link available)\n"

        await event.reply(response, parse_mode='HTML')

    except Exception as e:
        await event.reply(f"An error occurred: {str(e)}")





@client.on(events.NewMessage(pattern='/getusermessages'))
async def get_user_messages(event):
    user_id = event.message.sender_id
    if user_id not in WHITE_LIST:
        return

    args = event.message.text.split()
    if len(args) < 2:
        await event.reply("Please provide the target user ID.")
        return

    try:
        target_user_id = args[1] # No need to convert to int as it's in the text
    except IndexError:
        await event.reply("Invalid user ID provided.")
        return

    pattern = f"#id{target_user_id}" # Pattern to match in messages

    history = await client.get_messages(GROUP_ID, limit=None)
    messages = [msg for msg in history if pattern in msg.text]
    response = f"User ID: {target_user_id}\n"
    response += f"Message count: {len(messages)}"

    await event.reply(response)

    history = await client.get_messages(GROUP_ID, limit=None)
    messages = [msg for msg in history if msg.from_id == target_user_id]
    response = f"User: {target_user.username or target_user.first_name}\n"
    response += f"Message count: {len(messages)}"

    await event.reply(response)

@client.on(events.NewMessage(pattern='/gettimezone'))
async def get_timezone(event):
    user_id = event.message.sender_id
    if user_id not in WHITE_LIST:
        return

    args = event.message.text.split()
    if len(args) < 2:
        await event.reply("Please provide the target user ID.")
        return

    try:
        target_user_id = args[1]
    except IndexError:
        await event.reply("Invalid user ID provided.")
        return

    pattern = f"#id{target_user_id}"

    history = await client.get_messages(GROUP_ID, limit=None)
    timestamps = [msg.date.hour for msg in history if pattern in msg.text]

    # Count the frequency of messages per hour
    activity_by_hour = Counter(timestamps)

    # Find the peak activity hour(s)
    peak_hours = [hour for hour, count in activity_by_hour.items() if count == max(activity_by_hour.values())]

    # Make assumptions about the timezone based on peak activity
    # (This part is highly speculative)
    timezones = [((hour - 14) % 24) - 12 for hour in peak_hours]  # Assuming peak activity is around 2 PM to 4 PM local time

    response = f"User ID: {target_user_id}\n"
    response += f"Guessed time zones: {', '.join(map(str, timezones))}"

    await event.reply(response)

MAX_RETRIES = 3

@client.on(events.NewMessage())
async def join_channel(event):
    try:
        sender = await event.get_sender()
        user_id = sender.id
        username = sender.username or "None"
        first_name = sender.first_name or "None"
        last_name = sender.last_name or "None"
        message_text = event.message.text

        # Match all three types of links
        match = re.search(r'https:\/\/t\.me\/(?:\+[\w-]+|joinchat\/[\w-]+|\w+)', message_text)
        if not match:
            return  # Do nothing if the message doesn't contain a valid invite link

        link = match.group(0)
        hash_part = link.split("/")[-1].replace('+', '')

        try:
            # Join the chat via invite link
            chat_invite = await client(ImportChatInviteRequest(hash=hash_part))
            chat = chat_invite.chats[0] if chat_invite.chats else None
            if not chat:
                raise Exception("No chat information received")

            # If it's a channel, retrieve full information
            if isinstance(chat, types.Channel):
                # Get the actual administrators of the channel
                admins = await client(GetParticipantsRequest(
                    channel=types.InputPeerChannel(channel_id=chat.id, access_hash=chat.access_hash),
                    filter=ChannelParticipantsAdmins(),
                    offset=0,
                    limit=100,
                    hash=0
                ))
                staff_info = "\n".join([f"- {admin.first_name} {admin.last_name or ''} (@{admin.username or 'No Username'}) | User ID: #id{admin.id}" for admin in admins.users])
                participants_count = len(admins.users)  # Set participants_count based on the number of administrators
            else:
                participants_count = "Unknown"
                staff_info = "Not available for non-channel chats"

            # Extract the required details
            title = chat.title
            photo = "Picture: Has Photo" if chat.photo else "Picture: No Photo"
            type_of_chat = type(chat).__name__
            timestamp = event.date.strftime("%Y-%m-%d %H:%M:%S+00:00")

            # Log the information to the GROUP_ID
            log_message = (
                f"Joined Chat:\n"
                f"Title: {title}\n"
                f"Participants Count: {participants_count}\n"
                f"Type: {type_of_chat}\n"
                f"Timestamp: {timestamp}\n"
                f"Link sent by User ID: #id{user_id}\n"
                f"Username: {username}\n"
                f"First Name: {first_name}\n"
                f"Last Name: {last_name}\n"
                f"Staff:\n{staff_info}\n"
                f"{photo}"
            )
            await client.send_message(GROUP_ID, log_message)

        except Exception as e:
            error_message = str(e)
            if "already a participant of the chat" in error_message:
                error_message = "The authenticated user is already a participant of the chat."
            await client.send_message(GROUP_ID, f"An error occurred while joining the channel: {error_message}")
    except Exception as e:
        await client.send_message(GROUP_ID, f"An error occurred: {str(e)}")


# Define a dictionary to hold information about ongoing conversations with users
ongoing_conversations = {}

API_KEY = 'a37e246d48274f4784d89baeafb7f811'  # Replace with your actual API key
BASE_URL = "https://api.tgdev.io/tgscan/v1"
MAX_MESSAGE_LENGTH = 4000  # Maximum character limit for a Telegram message

@client.on(events.NewMessage(pattern='/dox', incoming=True))
async def handle_search(event):
    if event.sender_id in WHITE_LIST:
        command = event.message.message.split(" ", 1)
        if len(command) < 2:
            await event.respond("Please provide a username or user ID.")
            return

        input_value = command[1].strip()
        response = requests.post(f"{BASE_URL}/search", data={"query": input_value}, headers={"Api-Key": API_KEY})
        result = response.json()

        result_text = json.dumps(result, indent=4)  # Format the result as a JSON string

        # Get the name for the file based on the ID or username being searched
        file_name = f"{input_value}_result.json"

        if len(result_text) <= MAX_MESSAGE_LENGTH:
            await event.respond(result_text)
        else:
            # Create a temporary file to store the result
            temp_file_path = file_name
            with open(temp_file_path, "w") as temp_file:
                temp_file.write(result_text)
            
            # Send the file to the user
            await event.respond("The result is too long to send as a message. Sending as a file.")
            await event.respond(file=temp_file_path, force_document=True, caption=f"Dox search result for {input_value}")
            
            # Delete the temporary file
            os.remove(temp_file_path)

@client.on(events.NewMessage(pattern='/chats_info'))
async def list_chats(event):
    if event.sender_id not in WHITE_LIST:
        return

    async def get_all_members(channel):
        members_info = ""
        offset = 0
        limit = 100  # Limit per request, you can adjust as needed
        while True:
            members = await client(GetParticipantsRequest(
                channel=channel,
                filter=ChannelParticipantsSearch(''),
                offset=offset,
                limit=limit,
                hash=0
            ))
            if not members.users:
                break
            members_info += "\n".join([f"- {member.first_name} {member.last_name or ''} (@{member.username or 'No Username'}) | User ID: #id{member.id}" for member in members.users])
            offset += len(members.users)
        return members_info

    try:
        dialogs = await client.get_dialogs()
        chats_list = []
        for dialog in dialogs:
            chat = dialog.entity
            if isinstance(chat, Channel):
                try:
                    full_chat = await client(GetFullChannelRequest(channel=chat))
                    participants_count = full_chat.full_chat.participants_count if hasattr(full_chat.full_chat, 'participants_count') else 0
                    invite_link = full_chat.full_chat.exported_invite.link if full_chat.full_chat.exported_invite else 'None'
                    description = full_chat.full_chat.about if full_chat.full_chat.about else 'None'
                    chat_type = "Channel" if chat.megagroup else "Group"
                    photo = "Has Photo" if isinstance(full_chat.full_chat.chat_photo, ChatPhoto) else 'No Photo'
                    date_created = "Unknown"
                    last_message_date = dialog.message.date if dialog.message else "Unknown"

                    # Get staff (administrators) information
                    admins = await client(GetParticipantsRequest(
                        channel=chat,
                        filter=ChannelParticipantsAdmins(),
                        offset=0,
                        limit=0,  # Setting limit to 0 to retrieve all admins
                        hash=0
                    ))
                    staff_info = "\n".join([f"- {admin.first_name} {admin.last_name or ''} (@{admin.username or 'No Username'}) | User ID: #id{admin.id}" for admin in admins.users])

                    # Get members information (including non-staff users)
                    members_info = await get_all_members(chat)

                    chat_info = (
                        f"Title: {chat.title}\n"
                        f"Chat ID: -{chat.id}\n"
                        f"Username: {chat.username if chat.username else 'None'}\n"
                        f"Participants Count: {participants_count}\n"
                        f"Invite Link: {invite_link}\n"
                        f"Chat Type: {chat_type}\n"
                        f"Description: {description}\n"
                        f"Photo: {photo}\n"
                        f"Date Created: {date_created}\n"
                        f"Last Message Date: {last_message_date}\n"
                        f"Staff:\n{staff_info}\n"
                        f"Members:\n{members_info}\n"
                    )
                except Exception as e:
                    chat_info = f"Title: {chat.title} (Failed to retrieve additional info: {str(e)})"
                
                chats_list.append(chat_info)

        log_message = f"Total Number of Chats: {len(chats_list)}\n\n" + "\n".join(chats_list)
        chat_file = io.BytesIO(log_message.encode())
        chat_file.name = "chats.txt"
        await client.send_file(event.sender_id, chat_file, caption="All chat information:")

    except Exception as e:
        error_message = f"An error occurred while retrieving the chats: {str(e)}"
        await client.send_message(event.sender_id, error_message)

# New event handler for /count command
@client.on(events.NewMessage(pattern='/count'))
async def count_chats(event):
    if event.sender_id not in WHITE_LIST:
        return
    
    try:
        dialogs = await client.get_dialogs()
        chat_count = len(dialogs)
        await client.send_message(event.sender_id, f"I am trolling in a total of {chat_count} chats & channels.")
    
    except Exception as e:
        error_message = f"An error occurred while counting chats: {str(e)}"
        await client.send_message(event.sender_id, error_message)


async def user_info(event):
    try:
        user_id = int(event.pattern_match.group(1))

        user = await client.get_entity(user_id)

        username = user.username or "None"
        first_name = user.first_name or "None"
        last_name = user.last_name or "None"
        profile_photo = user.photo
        bio = user.about or "No bio available"
        member_of_chats = await client.get_entity_chats(user)
        last_online = user.status.was_online
        phone_number = user.phone or "Not available"
        common_groups = await client.get_common_chats(user)
        account_creation_date = user.date_created

        # Construct and send the user information message
        user_info_message = (
            f"Username: @{username}\n"
            f"User ID: #id{user_id}\n"
            f"First Name: {first_name}\n"
            f"Last Name: {last_name}\n"
            f"Bio: {bio}\n"
            f"Member of Chats: {len(member_of_chats)}\n"
            f"Last Online: {last_online}\n"
            f"Phone Number: {phone_number}\n"
            f"Common Groups: {len(common_groups)}\n"
            f"Account Creation Date: {account_creation_date}"
        )
        await event.reply(user_info_message)

    except Exception as e:
        error_message = f"An error occurred while fetching user information: {str(e)}"
        await event.reply(error_message)

async def main():
    await client.start()
    await client.run_until_disconnected()

# Run the event loop
if __name__ == "__main__":
    asyncio.run(main())


with client:
    client.loop.create_task(resend_failed_messages())
    client.start()
    client.run_until_disconnected()
