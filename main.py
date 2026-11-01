import argparse
from dataclasses import dataclass
from pathlib import Path
import time

from lupa.lua54 import LuaRuntime, lua_type


DEFAULT_EXTENSION = Path(__file__).resolve().parent / "extensions" / "discount.lua"
CART = (
    {"name": "Клавиатура", "price": 250000, "quantity": 1},
    {"name": "Мышь", "price": 100000, "quantity": 1},
    {"name": "Коврик", "price": 25000, "quantity": 2},
)
SUBTOTAL = sum(item["price"] * item["quantity"] for item in CART)


@dataclass(frozen=True)
class Receipt:
    discount: int
    message: str


def calculate(source: str) -> Receipt:
    """Каждый вариант скрипта выполняется в новом интерпретаторе."""
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(source)
    function = lua.globals().calculate
    if lua_type(function) != "function":
        raise ValueError("Расширение должно объявлять функцию calculate(cart)")
    cart = lua.table_from([dict(item) for item in CART], recursive=True)
    result = function(cart)
    if lua_type(result) != "table":
        raise ValueError("calculate должна вернуть таблицу")
    discount, message = result["discount"], result["message"]
    if type(discount) is not int or not 0 <= discount <= SUBTOTAL:
        raise ValueError("discount должна быть целым числом от 0 до суммы корзины")
    if not isinstance(message, str):
        raise ValueError("message должна быть строкой")
    return Receipt(discount, message)


class ExtensionWatcher:
    def __init__(self, path: Path):
        self.path = path
        self.last_source = None
        self.last_error = None
        self.receipt = Receipt(0, "Расширение ещё не загружено: скидки нет")
        self.has_success = False

    def refresh(self) -> bool:
        """Возвращает True, когда появился новый корректный результат."""
        try:
            source = self.path.read_text(encoding="utf-8-sig")
            if source == self.last_source:
                self.last_error = None
                return False
            candidate = calculate(source)
        except Exception as error:
            message = str(error)
            if message != self.last_error:
                print(f"\nОшибка расширения: {message}", flush=True)
                status = "Сохранён последний успешный результат" if self.has_success else "Пока применяется цена без скидки"
                print(f"{status}: {money(SUBTOTAL - self.receipt.discount)}", flush=True)
            self.last_error = message
            return False
        self.last_source = source
        self.last_error = None
        self.receipt = candidate
        self.has_success = True
        return True


def money(kopecks: int) -> str:
    return f"{kopecks // 100}.{kopecks % 100:02d} руб."


def show_receipt(receipt: Receipt) -> None:
    print(f"\nПравила применены: {receipt.message}")
    print(f"Сумма: {money(SUBTOTAL)}")
    print(f"Скидка: {money(receipt.discount)}")
    print(f"К оплате: {money(SUBTOTAL - receipt.discount)}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extension", type=Path, default=DEFAULT_EXTENSION)
    parser.add_argument("--once", action="store_true", help="Один расчёт без наблюдения")
    args = parser.parse_args()
    print("Корзина интернет-магазина", flush=True)
    for item in CART:
        print(f"  {item['name']}: {money(item['price'])} x {item['quantity']}")
    watcher = ExtensionWatcher(args.extension)
    if args.once:
        if watcher.refresh():
            show_receipt(watcher.receipt)
            return 0
        return 1
    print(f"Расширение: {args.extension.resolve()}")
    print("Сохраните Lua-файл для пересчёта. Выход: Ctrl+C.", flush=True)
    try:
        while True:
            if watcher.refresh():
                show_receipt(watcher.receipt)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nПрограмма завершена.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
