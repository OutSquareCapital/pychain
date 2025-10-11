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
    ).collect()


def _item_count(key: pc.Expr) -> pc.Expr:
    return key.itr_apply(lambda x: x.length()).alias("item_count")


def _is_active(key: pc.Expr) -> pc.Expr:
    is_active: pc.Expr = pc.key("user").field("status").eq("active")
    return key.and_(is_active)


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
        pc.key("is_vip").pipe(_is_active).alias("is_active_vip"),
    ).collect()


def main():
    record = pc.Record(_dummy_data())
    print("--- User Summary ---")
    record.pipe(_user_summary).pipe(print)
    print("\n--- Enriched Record ---")
    record.pipe(_enriched_record).pipe(print)


if __name__ == "__main__":
    main()
