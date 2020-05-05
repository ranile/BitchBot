import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from "@angular/material/dialog";
import { Command } from "../../../models/Command";

@Component({
    selector: 'app-show-command',
    templateUrl: './show-command.component.html',
    styleUrls: ['./show-command.component.scss']
})
export class ShowCommandComponent implements OnInit {
    command;
    constructor(@Inject(MAT_DIALOG_DATA) private data: Command) {
        const split = this.data.help.split('Args')
        this.command = {
            name: this.data.name,
            signature: this.data.signature,
            help: split[0].trim(),
            args: split[1] ? split[1].substr(3).trim() : undefined,
        };
    }


    ngOnInit(): void {
    }
}
