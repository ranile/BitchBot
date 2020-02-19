import { Guild } from "./Guild";

export class User {
  constructor(
    public avatar: string,
    public discriminator: string,
    public id: string,
    public name: string,
    public guilds: Guild[]
  ) {}
}
