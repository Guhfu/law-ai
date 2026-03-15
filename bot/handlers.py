from aiogram import F, Router
from aiogram.types import Message

from .client import ask_backend


router = Router()


@router.message(F.text == "/start")
async def cmd_start(message: Message) -> None:
    text = (
        "Привіт! Я бот-помічник з українського законодавства.\n"
        "Надішліть мені ваше запитання українською мовою, "
        "і я спробую знайти відповідні норми законів та пояснити їх.\n\n"
        "⚠️ Відповіді не є офіційною юридичною консультацією."
    )
    await message.answer(text)


@router.message(F.text == "/help")
async def cmd_help(message: Message) -> None:
    text = (
        "Я використовую відкриті дані законодавства України та LLM-модель, "
        "щоб шукати релевантні норми і пояснювати їх простою мовою.\n\n"
        "Просто надішліть мені запитання, наприклад:\n"
        "• \"Які умови розірвання трудового договору?\"\n"
        "• \"Відповідальність за крадіжку за КК України\"\n\n"
        "⚠️ Не надаю персоналізованих юридичних порад, лише загальну інформацію."
    )
    await message.answer(text)


@router.message(F.text)
async def handle_question(message: Message) -> None:
    question = message.text or ""
    if not question.strip():
        return

    await message.answer("Шукаю релевантні норми законодавства, зачекайте...")

    try:
        data = await ask_backend(question, language="uk")
    except Exception as exc:  # noqa: BLE001
        await message.answer(
            "Сталася помилка під час звернення до сервера. "
            "Переконайтеся, що backend запущено, і спробуйте ще раз."
        )
        return

    answer = data.get("answer", "")
    sources = data.get("sources", [])

    text_lines = [answer.strip() or "Немає згенерованої відповіді."]

    if sources:
        text_lines.append("\nВикористані джерела:")
        for src in sources[:5]:
            title = src.get("title", "")
            act_type = src.get("act_type", "")
            article = src.get("article_number") or "-"
            part = src.get("part_number") or "-"
            text_lines.append(
                f"- {title} ({act_type}), стаття {article}, частина {part}"
            )

    await message.answer("\n".join(text_lines))

