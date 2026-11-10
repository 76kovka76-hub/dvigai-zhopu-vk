import hashlib
import json
import os
import random
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

API_VERSION = "5.199"
HISTORY_PATH = Path("post_history.json")
MSK = timezone(timedelta(hours=3))

# Safe, equipment-free movements suitable for a home or office.
TASKS = [
    ("Сделай", "10 спокойных приседаний до комфортной глубины"),
    ("Выполни", "12 подъёмов на носки, держась за устойчивую опору"),
    ("Сделай", "8 отжиманий от стены"),
    ("Поднимись", "10 раз со стула и снова спокойно сядь"),
    ("Разомни", "плечи 12 кругами назад"),
    ("Сделай", "10 мягких подъёмов коленей на месте"),
    ("Выполни", "8 отведений каждой ноги в сторону, держась за опору"),
    ("Сожми", "ягодицы на 5 секунд и повтори это 8 раз"),
    ("Сделай", "10 медленных сведений лопаток стоя"),
    ("Подними", "руки вверх 8 раз и потянись без рывков"),
    ("Выполни", "10 разгибаний каждой ноги сидя на стуле"),
    ("Сделай", "8 неглубоких приседаний, держась за устойчивую опору"),
    ("Постой", "20 секунд на носках рядом с опорой"),
    ("Сделай", "10 шагов на месте с мягким перекатом стопы"),
    ("Разомни", "кисти 15 круговыми движениями в каждую сторону"),
    ("Выполни", "10 наклонов головы совсем небольшой амплитуды"),
    ("Сделай", "8 отжиманий от стены с ровной спиной"),
    ("Поднимай", "пятки 15 раз, не торопясь"),
    ("Сделай", "10 попеременных подъёмов колена сидя"),
    ("Отведи", "каждую ногу назад по 8 раз, держась за опору"),
    ("Сделай", "10 мягких поворотов корпуса в комфортную сторону"),
    ("Выполни", "8 медленных вставаний со стула"),
    ("Разведи", "руки в стороны и сведи лопатки 10 раз"),
    ("Сделай", "12 шагов на месте, активно работая руками"),
    ("Потяни", "руки вверх на 5 секунд и повтори 3 раза"),
    ("Выполни", "10 подъёмов на носки с опорой"),
    ("Сделай", "8 неглубоких выпадов назад попеременно, держась за опору"),
    ("Сожми", "лопатки на 3 секунды и повтори 10 раз"),
    ("Сделай", "10 попеременных разгибаний ног сидя"),
    ("Выполни", "12 спокойных шагов на месте"),
    ("Покрути", "плечами 10 раз вперёд и 10 раз назад"),
    ("Сделай", "8 отжиманий от стены в удобном темпе"),
    ("Поднимай", "колени по очереди 12 раз, стоя рядом с опорой"),
    ("Выполни", "10 лёгких приседаний до комфортной глубины"),
    ("Сделай", "10 сведений и разведений лопаток"),
    ("Постой", "15 секунд на одной ноге, держась за опору, затем смени ногу"),
    ("Разомни", "голеностоп кругами по 8 раз в каждую сторону"),
    ("Сделай", "10 подъёмов рук через стороны без веса"),
    ("Выполни", "8 медленных подъёмов со стула"),
    ("Пройдись", "20 шагов на месте в бодром, но комфортном темпе"),
    ("Сделай", "10 мягких наклонов таза стоя"),
    ("Подними", "каждую пятку по очереди 12 раз"),
    ("Выполни", "8 отведений каждой ноги в сторону у устойчивой опоры"),
    ("Сделай", "10 попеременных подъёмов коленей сидя"),
    ("Разомни", "пальцы и кисти в течение 20 секунд"),
    ("Сделай", "8 неглубоких приседаний без спешки"),
    ("Потяни", "бок корпуса по 5 секунд в каждую сторону"),
    ("Выполни", "10 кругов плечами назад и расправь грудь"),
    ("Сделай", "12 подъёмов на носки рядом со стеной"),
    ("Встань", "и пройдись на месте 30 секунд"),
    ("Выполни", "8 отжиманий от стены, сохраняя корпус ровным"),
]

OPENERS = [
    "Ну-ка, оторвись от стула и",
    "Хватит залипать —",
    "Эй, чемпион дивана,",
    "Подними задницу и",
    "Пора размяться, боец:",
    "Давай без отмазок:",
    "Встряхнись уже и",
    "Рабочий режим на паузу —",
    "Соберись, боец, и",
    "А ну-ка,",
    "Не кисни, а",
    "Пятьдесят оттенков прокрастинации отменяются:",
]

ENDINGS = [
    ", блядь!",
    ", и не халтурь!",
    ", спокойно, но честно!",
    ", давай, шевелись!",
    ", без геройства и рывков!",
    ", вот прямо сейчас!",
    ", не откладывай на потом!",
    ", красавчик, погнали!",
    ", и возвращайся к делам бодрее!",
    ", хватит кормить стул своей задницей!",
]

HASHTAGS = [
    "#ДвигайЖопой", "#Разминка", "#ДвижениеЭтоЖизнь", "#ОфиснаяЗарядка",
    "#БезОтмазок", "#ВстаньИДвигайся", "#МинуткаДвижения", "#ЗдороваяСпина",
    "#МаленькийШаг", "#Шевелись", "#ПерерывСПользой", "#ДвигайсяДома",
    "#ЗарядБодрости", "#РабочаяРазминка", "#ТелоСкажетСпасибо",
    "#ПораВстать", "#ДвижениеКаждыйДень", "#ЛёгкаяЗарядка", "#НеСиди",
    "#БодрыйДень", "#Разомнись", "#АктивнаяПауза", "#ПростыеУпражнения",
    "#ДвигайсяБезЗала", "#МинуткаДляСебя", "#ВперёдБезЛени",
]

SLOTS = {
    "0 5 * * *": "08:00",
    "30 6 * * *": "09:30",
    "0 8 * * *": "11:00",
    "30 9 * * *": "12:30",
    "0 11 * * *": "14:00",
    "30 12 * * *": "15:30",
    "0 14 * * *": "17:00",
    "30 15 * * *": "18:30",
    "0 17 * * *": "20:00",
    "30 18 * * *": "21:30",
}


def load_history():
    if not HISTORY_PATH.exists():
        return []
    try:
        data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("История публикаций должна быть списком")
        return data
    except Exception as exc:
        raise RuntimeError(f"Не удалось прочитать историю; публикация остановлена: {exc}")


def choose_post(history, date_text, slot):
    used = {str(item.get("text", "")).casefold().strip() for item in history}
    seed = int(hashlib.sha256(f"{date_text}|{slot}".encode()).hexdigest(), 16)
    rng = random.Random(seed)
    tasks = TASKS[:]
    openers = OPENERS[:]
    endings = ENDINGS[:]
    tags = HASHTAGS[:]
    rng.shuffle(tasks)
    rng.shuffle(openers)
    rng.shuffle(endings)

    # Explore a large combination space; history prevents exact sentence reuse.
    for task in tasks:
        for opener in openers:
            for ending in endings:
                sentence = f"{opener} {task[0].lower()} {task[1]}{ending}"
                if sentence.casefold().strip() in used:
                    continue
                chosen_tags = rng.sample(tags, 3)
                return sentence + "\n" + " ".join(chosen_tags)
    raise RuntimeError("Закончились уникальные варианты. Новую публикацию не отправляю.")


def get_slot():
    event = os.getenv("GITHUB_EVENT_NAME", "")
    if event == "schedule":
        cron = os.getenv("GITHUB_EVENT_SCHEDULE", "")
        if cron not in SLOTS:
            raise RuntimeError(f"Неизвестное расписание: {cron}")
        return SLOTS[cron]
    return "ручной запуск"


def publish(text):
    token = os.getenv("VK_ACCESS_TOKEN", "").strip()
    group_id = os.getenv("VK_GROUP_ID", "74712378").strip()
    if not token:
        raise RuntimeError("Не задан GitHub Secret VK_ACCESS_TOKEN")
    if not group_id.isdigit():
        raise RuntimeError("VK_GROUP_ID должен содержать только цифры")

    response = requests.post(
        "https://api.vk.com/method/wall.post",
        data={
            "access_token": token,
            "v": API_VERSION,
            "owner_id": f"-{group_id}",
            "from_group": 1,
            "message": text,
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        error = payload["error"]
        raise RuntimeError(f"Ошибка VK API {error.get('error_code')}: {error.get('error_msg')}")
    return payload["response"]["post_id"]


def main():
    now = datetime.now(MSK)
    date_text = now.date().isoformat()
    slot = get_slot()
    history = load_history()

    if any(item.get("date") == date_text and item.get("slot") == slot for item in history):
        print(f"Публикация за {date_text}, слот {slot}, уже есть. Пропускаю.")
        return

    post_text = choose_post(history, date_text, slot)
    print("Подготовлен текст:")
    print(post_text)
    post_id = publish(post_text)
    history.append({
        "date": date_text,
        "slot": slot,
        "text": post_text,
        "vk_post_id": post_id,
        "published_at": now.isoformat(),
    })
    HISTORY_PATH.write_text(
        json.dumps(history, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Успешно опубликовано. VK post_id={post_id}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ОШИБКА: {exc}", file=sys.stderr)
        raise
