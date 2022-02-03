from Yukki import BOT_USERNAME, LOG_GROUP_ID, app
from Yukki.Database import blacklisted_chats, is_gbanned_user, is_on_off


def checker(mystic):
    async def wrapper(_, message):
        if message.sender_chat:
            return await message.reply_text(
                "Bạn là __Quản trị viên ẩn danh__ trong Nhóm trò chuyện này!\nHoàn nguyên về Tài khoản Người dùng Từ Quyền của Quản trị viên."
            )
        blacklisted_chats_list = await blacklisted_chats()
        if message.chat.id in blacklisted_chats_list:
            await message.reply_text(
                f"**Trò chuyện trong danh sách đen**\n\nCuộc trò chuyện của bạn đã bị Người dùng Sudo đưa vào danh sách đen. Hỏi bất kỳ __SUDO USER__ to whitelist.\nCheck Sudo Users List [From Here](https://t.me/{BOT_USERNAME}?start=sudolist)"
            )
            return await app.leave_chat(message.chat.id)
        if await is_on_off(1):
            if int(message.chat.id) != int(LOG_GROUP_ID):
                return await message.reply_text(
                    f"Bot đang được Bảo trì. Xin lỗi vì sự bất tiện!"
                )
        if await is_gbanned_user(message.from_user.id):
            return await message.reply_text(
                f"**Gbanned User**\n\nYou're gbanned from using Bot.Ask any __SUDO USER__ to ungban.\nCheck Sudo Users List [From Here](https://t.me/{BOT_USERNAME}?start=sudolist)"
            )
        return await mystic(_, message)

    return wrapper


def checkerCB(mystic):
    async def wrapper(_, CallbackQuery):
        blacklisted_chats_list = await blacklisted_chats()
        if CallbackQuery.message.chat.id in blacklisted_chats_list:
            return await CallbackQuery.answer(
                "Trò chuyện trong danh sách đen", show_alert=True
            )
        if await is_on_off(1):
            if int(CallbackQuery.message.chat.id) != int(LOG_GROUP_ID):
                return await CallbackQuery.answer(
                    "Bot đang được Bảo trì. Xin lỗi vì sự bất tiện!",
                    show_alert=True,
                )
        if await is_gbanned_user(CallbackQuery.from_user.id):
            return await CallbackQuery.answer(
                "Bạn bị cấm", show_alert=True
            )
        return await mystic(_, CallbackQuery)

    return wrapper
