-- ---------------------------------------------------------------------------
-- Esquema PRIVADO del Servicio de Usuarios.
--
-- Ningun otro servicio se conecta a esta base. Pedidos no tiene credenciales
-- ni ruta de red hacia aqui: solo puede preguntar por la API REST.
-- Docker lo ejecuta una unica vez, al inicializar el volumen de la base.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS users (
    id         UUID        PRIMARY KEY,
    name       TEXT        NOT NULL CHECK (length(trim(name)) > 0),
    -- El correo se guarda siempre en minusculas. Quien lo garantiza es la
    -- entidad `User.register()`, no la base de datos: el CHECK es solo una
    -- red de seguridad que documenta la invariante del dominio.
    email      TEXT        NOT NULL UNIQUE CHECK (email = lower(email)),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS users_created_at_idx ON users (created_at DESC);
