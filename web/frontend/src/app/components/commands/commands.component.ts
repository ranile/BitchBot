import { Component, OnInit } from '@angular/core';
import { HttpClient } from "@angular/common/http";
import { MatTableDataSource } from "@angular/material/table";
import { PageEvent } from "@angular/material/paginator";
import { MatDialog } from "@angular/material/dialog";
import { ShowCommandComponent } from "./show-command/show-command.component";
import { CogCommands, Command } from "../../models/Command";


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

    constructor(private httpClient: HttpClient, public dialog: MatDialog) {
    }

    ngOnInit(): void {
        this.httpClient.get<CogCommands[]>('/api/commands/').toPromise().then(data => {
            data.forEach(it => {
                this.cogs.push(it)
                it.commands.forEach(command => command.help = command.help ? command.help : 'Help for this command is not available, join our support server for help')
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
        })

    }

    shortHelp(help: string): string {
        return help.split('\n')[0]
    }

    pageChange(event: PageEvent) {
        this.cog = this.cogs[event.pageIndex]
    }

    onCommandRowClick(row: Command) {
        this.dialog.open(ShowCommandComponent, {
            data: row
        });
    }
}
