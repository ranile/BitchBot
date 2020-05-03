import { Component, OnInit } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {MatTableDataSource} from "@angular/material/table";

export interface Command {
    name: string
    help: string
    signature: string
}

export interface CogCommands {
    name:  string
    description:  string
    commands:  Command[]
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

    constructor(private httpClient: HttpClient) {
    }

    ngOnInit(): void {
        this.httpClient.get<CogCommands[]>('/api/commands/').toPromise().then(data => {
            data.forEach(it => {
                this.cogs.push(it)
                this.dataSources[it.name] = new MatTableDataSource(it.commands)
            })
            // this.dataSources[data[0].name] = new MatTableDataSource(data[0].commands)
            console.log(data)
        })

    }

}
