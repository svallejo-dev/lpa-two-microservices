/**
 * PUERTO hacia el Servicio de Usuarios.
 *
 * Esta interfaz es la frontera entre los dos microservicios expresada en
 * lenguaje de negocio. El dominio dice "necesito saber si este usuario
 * existe"; que la respuesta llegue por REST, gRPC, una cache local o una copia
 * replicada es una decision de infraestructura, intercambiable sin tocar los
 * casos de uso.
 *
 * El CONTRATO tiene tres resultados posibles, y los tres importan:
 *   - devuelve un `KnownUser`  -> el usuario existe
 *   - devuelve `null`          -> el usuario NO existe (respuesta confirmada)
 *   - lanza `UserDirectoryUnavailableError` -> no se pudo averiguar
 */

export interface KnownUser {
  id: string;
  name: string;
  email: string;
}

export interface UserDirectory {
  findById(userId: string): Promise<KnownUser | null>;
}
