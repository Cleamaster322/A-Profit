from urllib.parse import urljoin, urlparse
import os
import urllib.request

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from db.generation_crud import add_generation, update_generation_image_path
from utils.logger import setup_logger
from parsers.error_writer import write_parser_error

BASE_URL = "https://www.drom.ru"
TARGET_REGION_IDS = ["japan", "south-korea", "china"]

logger = setup_logger(__name__)


def _parse_name_and_dates(text: str) -> tuple[str, str, str]:
    parts = [part.strip() for part in text.split("\n") if part.strip()]

    if not parts:
        return "", "", ""

    name = parts[0]
    date_start = ""
    date_end = ""

    if len(parts) > 1 and " - " in parts[1]:
        date_parts = [part.strip() for part in parts[1].split(" - ", 1)]
        date_start = date_parts[0] if len(date_parts) > 0 else ""
        date_end = date_parts[1] if len(date_parts) > 1 else ""

    return name, date_start, date_end


def _parse_generation_numbers(generation_raw: str) -> tuple[int | None, int]:
    generation_num = None
    restyling_num = 0

    if not generation_raw:
        return generation_num, restyling_num

    raw_lower = generation_raw.lower()

    first_token = generation_raw.split()[0]
    try:
        generation_num = int(first_token)
    except (ValueError, TypeError):
        generation_num = None

    if "рестайлинг" in raw_lower:
        restyling_num = 1

    return generation_num, restyling_num


def get_media_generations_path() -> str:
    parser_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    project_root = os.path.abspath(os.path.join(parser_dir, ".."))
    media_path = os.path.join(project_root, "main", "media", "generations")

    os.makedirs(media_path, exist_ok=True)
    return media_path


def _get_project_root() -> str:
    parser_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.abspath(os.path.join(parser_dir, ".."))


def _get_relative_image_path(filename: str) -> str:
    return f"generations/{filename}"


def _get_absolute_path_from_relative(relative_path: str) -> str:
    project_root = _get_project_root()
    media_root = os.path.join(project_root, "main", "media")

    normalized_path = str(relative_path).replace("\\", "/")

    if normalized_path.startswith("main/media/"):
        normalized_path = normalized_path.replace("main/media/", "", 1)

    return os.path.join(media_root, normalized_path)


def _get_file_extension_from_url(image_url: str) -> str:
    parsed = urlparse(image_url)
    _, ext = os.path.splitext(parsed.path)

    if ext:
        return ext.lower()

    return ".jpg"


def generation_image_exists(generation_record: dict) -> bool:
    """
    Проверяет, что у поколения уже есть image_path и файл реально существует на диске.
    """
    image_path = generation_record.get("image_path")
    if not image_path:
        return False

    absolute_path = _get_absolute_path_from_relative(image_path)
    return os.path.exists(absolute_path)


def download_generation_image(model: dict, generation_record: dict, image_url: str) -> str | None:
    """
    Скачивает изображение поколения и возвращает относительный путь для записи в БД.
    Если файл уже существует, повторно не скачивает.
    """
    if not image_url:
        return None

    if generation_image_exists(generation_record):
        existing_path = generation_record.get("image_path")
        logger.info(
            "Изображение уже существует: generation_id=%s, image_path=%s",
            generation_record["id"],
            existing_path,
        )
        return existing_path

    media_path = get_media_generations_path()

    brand_id = model["brand_id"]
    model_id = model["id"]
    generation_id = generation_record["id"]

    ext = _get_file_extension_from_url(image_url)
    file_name = f"{brand_id}_{model_id}_{generation_id}{ext}"
    absolute_file_path = os.path.join(media_path, file_name)
    relative_file_path = _get_relative_image_path(file_name)

    try:
        urllib.request.urlretrieve(image_url, absolute_file_path)
        logger.info(
            "Изображение поколения скачано: generation_id=%s, path=%s",
            generation_id,
            absolute_file_path,
        )
        return relative_file_path
    except Exception as e:
        logger.error(
            "Ошибка при скачивании изображения поколения: generation_id=%s, image_url=%s, error=%s",
            generation_id,
            image_url,
            e,
            exc_info=True,
        )

        write_parser_error(
            error_type="IMAGE_DOWNLOAD_ERROR",
            data={
                "generation_id": generation_id,
                "model_id": model.get("id"),
                "model_name": model.get("name"),
                "brand_id": model.get("brand_id"),
                "image_url": image_url,
                "error": str(e),
            }
        )
        return None


def _wait_model_page_ready(browser):
    """
    Один раз ждем, пока страница модели загрузится.
    """
    WebDriverWait(browser.driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.css-10ib5jr"))
    )


def _collect_generation_elements_by_regions(browser, model_id, model_name):
    """
    Собирает карточки поколений только из нужных регионов.
    Здесь нет ожидания по 3 секунды на каждый регион.
    """
    collected = []

    try:
        _wait_model_page_ready(browser)
    except TimeoutException:
        logger.warning(
            "Не дождались загрузки страницы модели: id=%s, name=%s",
            model_id,
            model_name,
        )

        write_parser_error(
            error_type="MODEL_PAGE_TIMEOUT",
            data={
                "model_id": model_id,
                "model_name": model_name,
                "error": "Не дождались загрузки страницы модели",
            }
        )
        return collected

    outlet_titles = browser.driver.find_elements(
        By.CSS_SELECTOR,
        "div[data-ga-stats-name='generations_outlet_title'][id]"
    )

    existing_region_blocks = {
        element.get_attribute("id"): element
        for element in outlet_titles
        if element.get_attribute("id")
    }

    for region_id in TARGET_REGION_IDS:
        region_block = existing_region_blocks.get(region_id)

        if not region_block:
            logger.info(
                'Нет блока с ID="%s" для модели: id=%s, name=%s',
                region_id,
                model_id,
                model_name,
            )
            continue

        try:
            generations_block = region_block.find_element(
                By.XPATH,
                "following-sibling::div[1]"
            )
        except Exception as e:
            logger.error(
                "Не удалось найти блок поколений после #%s для модели id=%s, name=%s: %s",
                region_id,
                model_id,
                model_name,
                e,
                exc_info=True,
            )

            write_parser_error(
                error_type="REGION_BLOCK_PARSE_ERROR",
                data={
                    "model_id": model_id,
                    "model_name": model_name,
                    "region": region_id,
                    "error": str(e),
                }
            )
            continue

        generation_elements = generations_block.find_elements(
            By.XPATH,
            ".//a[@data-ftid='component_article']"
        )

        if not generation_elements:
            logger.info(
                'В блоке "%s" не найдено поколений для модели id=%s, name=%s',
                region_id,
                model_id,
                model_name,
            )
            continue

        logger.info(
            'Найдено поколений в регионе "%s" для модели id=%s, name=%s: %s',
            region_id,
            model_id,
            model_name,
            len(generation_elements),
        )

        for el in generation_elements:
            collected.append((region_id, el))

    return collected


def _extract_generation_data_from_element(el, model_id, model_name, region_id):
    """
    Извлекает данные поколения из карточки с минимальным числом Selenium-вызовов.
    """
    href = el.get_attribute("href") or ""
    link = urljoin(BASE_URL, href) if href else ""

    img_elems = el.find_elements(By.TAG_NAME, "img")
    image_url = img_elems[0].get_attribute("src") if img_elems else ""

    caption_elems = el.find_elements(
        By.XPATH,
        './/span[@data-ftid="component_article_caption"]'
    )
    raw_caption = caption_elems[0].text.strip() if caption_elems else ""
    name, date_start, date_end = _parse_name_and_dates(raw_caption)

    info_divs = el.find_elements(
        By.XPATH,
        './/div[@data-ftid="component_article_extended-info"]/div'
    )

    generation_raw = info_divs[0].text.strip() if len(info_divs) > 0 else ""
    body_code = info_divs[1].text.strip() if len(info_divs) > 1 else ""
    body_type = info_divs[2].text.strip() if len(info_divs) > 2 else ""

    generation_num, restyling_num = _parse_generation_numbers(generation_raw)

    is_hybrid = "гибрид" in body_type.lower()
    body_type = (
        body_type
        .replace(", Гибрид", "")
        .replace(", гибрид", "")
        .strip()
    )

    if not image_url:
        logger.warning(
            "Не найдено изображение в карточке поколения: model_id=%s, model_name=%s, region=%s, link=%s",
            model_id,
            model_name,
            region_id,
            link,
        )

    generation = {
        "name": name,
        "date_start": date_start,
        "date_end": date_end,
        "link": link,
        "body_code": body_code,
        "body_type": body_type,
        "region": region_id,
        "image_path": None,
        "is_hybrid": is_hybrid,
        "generation_num": generation_num,
        "restyling_num": restyling_num,
    }

    return generation, image_url


def parse_generation(models, browser):
    logger.info("Старт parse_generation")

    for model in models:
        model_id = model.get("id")
        model_name = model.get("name")
        model_link = model.get("link")
        brand_id = model.get("brand_id")

        if not model_link:
            logger.warning(
                "У модели отсутствует link: id=%s, name=%s",
                model_id,
                model_name,
            )

            write_parser_error(
                error_type="MODEL_LINK_MISSING",
                data={
                    "model_id": model_id,
                    "model_name": model_name,
                    "brand_id": brand_id,
                }
            )
            continue

        if brand_id is None:
            logger.warning(
                "У модели отсутствует brand_id: id=%s, name=%s",
                model_id,
                model_name,
            )

            write_parser_error(
                error_type="MODEL_BRAND_ID_MISSING",
                data={
                    "model_id": model_id,
                    "model_name": model_name,
                    "model_link": model_link,
                }
            )
            continue

        try:
            logger.info(
                "Обработка модели: id=%s, name=%s, link=%s",
                model_id,
                model_name,
                model_link,
            )
            browser.get(model_link)

            generation_items = _collect_generation_elements_by_regions(
                browser=browser,
                model_id=model_id,
                model_name=model_name,
            )

            if not generation_items:
                logger.warning(
                    "Для модели id=%s, name=%s поколения не найдены в регионах %s",
                    model_id,
                    model_name,
                    TARGET_REGION_IDS,
                )
                continue

            logger.info(
                "Всего найдено поколений для модели id=%s, name=%s: %s",
                model_id,
                model_name,
                len(generation_items),
            )

            for region_id, el in generation_items:
                generation = None
                image_url = None

                try:
                    generation, image_url = _extract_generation_data_from_element(
                        el=el,
                        model_id=model_id,
                        model_name=model_name,
                        region_id=region_id,
                    )

                    logger.info(
                        "Добавление поколения для модели id=%s, name=%s, region=%s: %s",
                        model_id,
                        model_name,
                        region_id,
                        generation,
                    )

                    generation_record = add_generation(model, generation)

                    if not generation_record:
                        logger.warning(
                            "Не удалось получить запись поколения после сохранения: "
                            "model_id=%s, model_name=%s, generation_name=%s, region=%s",
                            model_id,
                            model_name,
                            generation["name"],
                            region_id,
                        )

                        write_parser_error(
                            error_type="GENERATION_RECORD_EMPTY",
                            data={
                                "model_id": model_id,
                                "model_name": model_name,
                                "model_link": model_link,
                                "region": region_id,
                                "generation_name": generation.get("name") if generation else None,
                            }
                        )
                        continue

                    image_path = download_generation_image(
                        model=model,
                        generation_record=generation_record,
                        image_url=image_url,
                    )

                    if image_path and generation_record.get("image_path") != image_path:
                        update_generation_image_path(
                            generation_id=generation_record["id"],
                            image_path=image_path,
                        )
                        generation_record["image_path"] = image_path

                except Exception as gen_err:
                    logger.error(
                        "Ошибка при разборе поколения для модели id=%s, name=%s, region=%s: %s",
                        model_id,
                        model_name,
                        region_id,
                        gen_err,
                        exc_info=True
                    )

                    write_parser_error(
                        error_type="GENERATION_PARSE_ERROR",
                        data={
                            "model_id": model_id,
                            "model_name": model_name,
                            "model_link": model_link,
                            "brand_id": brand_id,
                            "region": region_id,
                            "generation_name": generation.get("name") if generation else None,
                            "generation_link": generation.get("link") if generation else None,
                            "image_url": image_url,
                            "error": str(gen_err),
                        }
                    )
                    continue

        except Exception as e:
            logger.error(
                "Ошибка при обработке модели id=%s, name=%s: %s",
                model_id,
                model_name,
                e,
                exc_info=True
            )

            write_parser_error(
                error_type="MODEL_PARSE_ERROR",
                data={
                    "model_id": model_id,
                    "model_name": model_name,
                    "model_link": model_link,
                    "brand_id": brand_id,
                    "error": str(e),
                }
            )
            continue

    logger.info("Завершение parse_generation")