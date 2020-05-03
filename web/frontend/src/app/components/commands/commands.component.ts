import {Component, OnInit} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {MatTableDataSource} from "@angular/material/table";
import {PageEvent} from "@angular/material/paginator";

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


@Component({
    selector: 'app-commands',
    templateUrl: './commands.component.html',
    styleUrls: ['./commands.component.scss']
})
export class CommandsComponent implements OnInit {
    displayedColumns: string[] = ['name', 'help', 'signature'];
    cogs = []
    dataSources: { [key: string]: MatTableDataSource<Command> } = {};
    cog: CogCommands

    constructor(private httpClient: HttpClient) {
    }

    ngOnInit(): void {
        this.httpClient.get<CogCommands[]>('/api/commands/').toPromise().then(data => {
            data.forEach(it => {
                this.cogs.push(it)
                this.dataSources[it.name] = new MatTableDataSource(it.commands)
            })

            this.cogs = this.cogs.sort((n1, n2) => {
                if (n1.name > n2.name) {
                    return 1
                }

                if (n1.name < n2.name) {
                    return -1
                }

                return 0
            });
            this.cog = this.cogs[0]
            // this.dataSources[data[0].name] = new MatTableDataSource(data[0].commands)
            console.log(this.cogs)
        })

    }

    shortHelp(help: string): string {
        if (help == null) return 'Help for this command is not available, join our support server for help'
        return help.split('\n')[0]
    }

    pageChange(event: PageEvent) {
        this.cog = this.cogs[event.pageIndex]
    }

    onCommandRowClick(row: Command) {
        console.log(row)
    }
}
