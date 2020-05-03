export interface Command {
    name: string
    help: string
    signature: string
}

export interface CogCommands {
    name: string
    description: string
    commands: Command[]
}
