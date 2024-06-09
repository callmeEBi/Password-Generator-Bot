import logging
from random import randrange
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)

#! log
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
num_check, alpha_check, sym_check = [list("✅"), list("✅"), list("✅")]
length = [15]

history = {}


def password_generator():
    numbers = [i for i in range(10)]
    alphbets = [chr(i) for i in range(65, 91)]
    alphbets2 = [chr(i) for i in range(97, 123)]
    alphbets.extend(alphbets2)
    symbols = [
        "!",
        "@",
        "#",
        "$",
        "&",
        "*",
        "+",
        "-",
        "_",
    ]
    selection_source = []
    password = ""
    if num_check[0] == "✅":
        selection_source.extend(numbers)
    if alpha_check[0] == "✅":
        selection_source.extend(alphbets)
    if sym_check[0] == "✅":
        selection_source.extend(symbols)
    if not selection_source:
        return "Please select at least one character type."
    i = 0
    while i < length[0]:
        j = randrange(len(selection_source))
        password += str(selection_source[j])
        i += 1
    return password


def status_changer(chk):
    if chk[0] == "✅":
        chk[0] = "❌"
    else:
        chk[0] = "✅"


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    query=None,
    not_first_time=False,
):
    start_buttons = [
        [
            InlineKeyboardButton("🔐 Generate Password", callback_data="gen"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
        ],
        [
            InlineKeyboardButton("🗒 History", callback_data="history"),
            InlineKeyboardButton("👋 Close", callback_data="close"),
        ],
    ]
    start_markup = InlineKeyboardMarkup(start_buttons)
    start_text = """
Welcome to the password generator bot!

This bot can generate strong and unique passwords for you.

you can start working with bot through buttons below.
"""
    if not_first_time:
        await query.edit_message_text(text=start_text, reply_markup=start_markup)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.effective_message.id,
            text=start_text,
            reply_markup=start_markup,
        )


async def length_function(update: Update, context: ContextTypes):
    try:
        args = int(context.args[0])
        if 5 <= int(args) <= 40:
            length[0] = args
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Length of password has been set to {length[0]} characters✅",
                reply_to_message_id=update.effective_message.id,
            )
            await context.bot.delete_messages(
                chat_id=update.effective_chat.id,
                message_ids=[
                    update.effective_message.id,
                    update.effective_message.id + 1,
                ],
            )
            return
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ The length must be bigger than 5 and smaller than 40 characters.",
                reply_to_message_id=update.effective_message.id,
            )
    except:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="""
        ❌ The length must be a number!
    """,
            reply_to_message_id=update.effective_message.id,
        )


async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #! texts:
    settings_text = """
    Here are the settings:
for changing password length you can use /len command.

example : /len 10
"""
    #! buttons:
    gen_buttons = [[InlineKeyboardButton("↩️ Back", callback_data="back")]]
    settings_buttons = [
        [
            InlineKeyboardButton(f"⛓ Length : {length[0]}", callback_data="length"),
            InlineKeyboardButton(f" Numbers : {num_check[0]}", callback_data="numbers"),
        ],
        [
            InlineKeyboardButton(
                f" Alphabets : {alpha_check[0]}", callback_data="alphabets"
            ),
            InlineKeyboardButton(f" Symbols : {sym_check[0]}", callback_data="symbols"),
        ],
        [InlineKeyboardButton("↩️ Back", callback_data="back")],
    ]
    history_buttons = [[InlineKeyboardButton("↩️ Back", callback_data="back")]]
    #! markups
    gen_markup = InlineKeyboardMarkup(gen_buttons)
    settings_markup = InlineKeyboardMarkup(settings_buttons)
    history_markup = InlineKeyboardMarkup(history_buttons)
    query = update.callback_query
    await query.answer()
    qd = query.data
    userID = update.effective_user.id
    if qd == "gen":
        password = password_generator()
        if password.startswith("Please"):
            await query.message.edit_text(
                text=password,
                reply_markup=gen_markup,
            )
            return

        if userID not in history:
            history[userID] = []
        history[userID].append(password)
        await query.message.edit_text(
            text=f"Generated Password: <blockquote><code>{password}</code></blockquote>",
            parse_mode="HTML",
            reply_markup=gen_markup,
        )
    elif qd == "settings":
        await query.message.edit_text(text=settings_text, reply_markup=settings_markup)
    elif qd == "close":
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=update.effective_message.id
        )
    elif qd == "history":
        if userID not in history or not history[userID]:
            await query.edit_message_text(
                text="❗️ you don't have any generated passwords yet.",
                reply_markup=history_markup,
            )
            return
        temp_history = history[userID]
        temp_history = [
            f"{index+1} - <blockquote><code>{value}</code></blockquote>"
            for index, value in enumerate(temp_history)
        ]
        temp_history = "\n\n".join(temp_history)
        await query.edit_message_text(
            text=f"your last generated passwords are here:\n\n{temp_history}",
            reply_markup=history_markup,
            parse_mode="HTML",
        )
    elif qd == "numbers":
        status_changer(num_check)
        settings_buttons = [
            [
                InlineKeyboardButton(f"⛓ Length : {length[0]}", callback_data="length"),
                InlineKeyboardButton(
                    f" Numbers : {num_check[0]}", callback_data="numbers"
                ),
            ],
            [
                InlineKeyboardButton(
                    f" Alphabets : {alpha_check[0]}", callback_data="alphabets"
                ),
                InlineKeyboardButton(
                    f" Symbols : {sym_check[0]}", callback_data="symbols"
                ),
            ],
            [InlineKeyboardButton("↩️ Back", callback_data="back")],
        ]
        settings_markup = InlineKeyboardMarkup(settings_buttons)
        await query.message.edit_text(text=settings_text, reply_markup=settings_markup)
    elif qd == "alphabets":
        status_changer(alpha_check)
        settings_buttons = [
            [
                InlineKeyboardButton(f"⛓ Length : {length[0]}", callback_data="length"),
                InlineKeyboardButton(
                    f" Numbers : {num_check[0]}", callback_data="numbers"
                ),
            ],
            [
                InlineKeyboardButton(
                    f" Alphabets : {alpha_check[0]}", callback_data="alphabets"
                ),
                InlineKeyboardButton(
                    f" Symbols : {sym_check[0]}", callback_data="symbols"
                ),
            ],
            [InlineKeyboardButton("↩️ Back", callback_data="back")],
        ]
        settings_markup = InlineKeyboardMarkup(settings_buttons)
        await query.message.edit_text(text=settings_text, reply_markup=settings_markup)
    elif qd == "symbols":
        status_changer(sym_check)
        settings_buttons = [
            [
                InlineKeyboardButton(f"⛓ Length : {length[0]}", callback_data="length"),
                InlineKeyboardButton(
                    f" Numbers : {num_check[0]}", callback_data="numbers"
                ),
            ],
            [
                InlineKeyboardButton(
                    f" Alphabets : {alpha_check[0]}", callback_data="alphabets"
                ),
                InlineKeyboardButton(
                    f" Symbols : {sym_check[0]}", callback_data="symbols"
                ),
            ],
            [InlineKeyboardButton("↩️ Back", callback_data="back")],
        ]
        settings_markup = InlineKeyboardMarkup(settings_buttons)
        await query.message.edit_text(text=settings_text, reply_markup=settings_markup)
    elif qd == "length":
        settings_buttons = [
            [
                InlineKeyboardButton(f"⛓ Length : {length[0]}", callback_data="length"),
                InlineKeyboardButton(
                    f" Numbers : {num_check[0]}", callback_data="numbers"
                ),
            ],
            [
                InlineKeyboardButton(
                    f" Alphabets : {alpha_check[0]}", callback_data="alphabets"
                ),
                InlineKeyboardButton(
                    f" Symbols : {sym_check[0]}", callback_data="symbols"
                ),
            ],
            [InlineKeyboardButton("↩️ Back", callback_data="back")],
        ]
        settings_markup = InlineKeyboardMarkup(settings_buttons)
        await query.message.edit_text(text=settings_text, reply_markup=settings_markup)
    elif qd == "back":
        await start(update, context, query=query, not_first_time=True)


if __name__ == "__main__":
    app = (
        ApplicationBuilder()
        .token("6797614179:AAGRgW8dfj1wGmK1YXpH28-bLn_9ASIWCCo")
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("len", length_function))
    app.add_handler(CallbackQueryHandler(handle_query))
    app.run_polling()
