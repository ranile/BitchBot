export class Warn {
  constructor(
    public guild_id: string,
    public id: number,
    public reason: string,
    public warned_at: number,
    public warned_by_id: string,
    public warned_user_id: string,
  ) {
  }
}
