-- ---------------------------------------------------------------------------
-- Esquema PRIVADO del Servicio de Pedidos.
--
-- Observacion central del taller: `user_id` NO tiene FOREIGN KEY.
-- No puede tenerla: la tabla `users` vive en otra base de datos, en otro
-- contenedor, gobernada por otro servicio. La integridad referencial que un
-- monolito obtiene gratis del motor aqui hay que sostenerla por protocolo,
-- llamando al Servicio de Usuarios antes de insertar.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS orders (
    id         UUID        PRIMARY KEY,
    user_id    UUID        NOT NULL,   -- <-- sin FK: frontera entre servicios
    total      BIGINT      NOT NULL CHECK (total >= 0),
    status     TEXT        NOT NULL CHECK (status IN ('PENDIENTE', 'CONFIRMADO', 'CANCELADO')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id   UUID     NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    position   INTEGER  NOT NULL,
    sku        TEXT     NOT NULL CHECK (length(trim(sku)) > 0),
    quantity   INTEGER  NOT NULL CHECK (quantity > 0),
    unit_price BIGINT   NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (order_id, position)
);

CREATE INDEX IF NOT EXISTS orders_user_id_idx     ON orders (user_id);
CREATE INDEX IF NOT EXISTS orders_created_at_idx  ON orders (created_at DESC);
