from typing import TypedDict

import pychain as pc


class User(TypedDict):
    id: int
    name: str
    roles: list[str]
    status: str


class OrderItem(TypedDict):
    name: str
    price: float
    quantity: int


class Order(TypedDict):
    items: list[OrderItem]
    currency: str


class DataSchema(TypedDict):
    user: User
    order: Order
    is_vip: bool


class SummarySchema(TypedDict):
    customer_name: str
    total_cost: float
    currency: str


class EnrichedSchema(TypedDict):
    is_vip: bool
    item_count: int
    primary_role: str | None
    is_active_vip: bool


def _dummy_data() -> DataSchema:
    return {
        "user": {
            "id": 101,
            "name": "Alice",
            "roles": ["customer", "beta-tester"],
            "status": "active",
        },
        "order": {
            "items": [
                {"name": "Apple", "price": 0.50, "quantity": 4},
                {"name": "Orange", "price": 1.25, "quantity": 2},
            ],
            "currency": "USD",
        },
        "is_vip": False,
    }


def _total_cost(expr: pc.Expr) -> pc.Expr:
    return expr.field("items").map(lambda item: item["price"] * item["quantity"]).sum()


def _user_summary(record: pc.Record) -> pc.Record:
    order = pc.key("order")
    return record.select(
        pc.key("user").field("name").alias("customer_name"),
        order.pipe(_total_cost).alias("total_cost"),
        order.field("currency").alias("currency"),
    )


def _enriched_record(record: pc.Record) -> pc.Record:
    user = pc.key("user")
    return record.with_fields(
        pc.key("order").field("items").length().alias("item_count"),
        user.field("roles").first().alias("primary_role"),
        pc.key("is_vip")
        .eq(True)
        .and_(user.field("status").eq("active"))
        .alias("is_active_vip"),
    ).drop("user", "order")


def main():
    record = pc.Record(dict(_dummy_data()))

    assert record.pipe(_user_summary).equals_to(
        SummarySchema(
            customer_name="Alice",
            total_cost=4.5,
            currency="USD",
        )
    )
    assert record.pipe(_enriched_record).equals_to(
        EnrichedSchema(
            is_vip=False,
            item_count=2,
            primary_role="customer",
            is_active_vip=False,
        )
    )


if __name__ == "__main__":
    main()
