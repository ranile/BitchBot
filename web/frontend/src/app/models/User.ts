export class User {
  constructor(
    public avatar: string,
    public discriminator: string,
    public id: string,
    public name: string,
  ) {}
}
