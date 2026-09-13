export interface KnownUser {
  id: string;
  name: string;
  email: string;
}

export interface UserDirectory {
  findById(userId: string): Promise<KnownUser | null>;
}
