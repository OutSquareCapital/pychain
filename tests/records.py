import pychain as pc


def _dummy_data():
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


def _total_cost(key: pc.Expr) -> pc.Expr:
    return key.field("items").apply(
        lambda items: sum(item["price"] * item["quantity"] for item in items)
    )


def _user_summary(record: pc.Record) -> pc.Record:
    """
    --- EXEMPLE 1: Sélection simple et transformation ---

    On veut le nom de l'utilisateur et le coût total de la commande.
    """
    order = pc.key("order")
    return record.select(
        pc.key("user").field("name").alias("customer_name"),
        order.pipe(_total_cost).alias("total_cost"),
        order.field("currency").alias("currency"),
    )


def _item_count(key: pc.Expr) -> pc.Expr:
    return key.apply(len).alias("item_count")


def _is_active() -> pc.Expr:
    return pc.key("user").field("status").eq("active")


def _enriched_record(record: pc.Record) -> pc.Record:
    """
    --- EXEMPLE 2: Ajout de champs calculés (with_fields) ---

    On garde le dict original et on ajoute des infos.
    """
    return record.with_fields(
        pc.key("order").field("items").pipe(_item_count),
        pc.key("user")
        .field("roles")
        .apply(lambda roles: roles[0])
        .alias("primary_role"),
        pc.key("is_vip").and_(_is_active()).alias("is_active_vip"),
    ).drop("user", "order")


def main():
    record = pc.Record(_dummy_data())

    assert record.pipe(_user_summary).equals_to(
        {
            "customer_name": "Alice",
            "total_cost": 4.5,
            "currency": "USD",
        }
    )
    assert record.pipe(_enriched_record).equals_to(
        {
            "is_vip": False,
            "item_count": 2,
            "primary_role": "customer",
            "is_active_vip": False,
        }
    )


if __name__ == "__main__":
    main()
