import {Component, Input, OnInit} from '@angular/core';
import {Warn} from "../../models/Warn";

@Component({
    selector: 'app-show-warn',
    templateUrl: './show-warn.component.html',
    styleUrls: ['./show-warn.component.scss']
})
export class ShowWarnComponent implements OnInit {
    @Input() warn: Warn;
    user = {avatarUrl: 'https://cdn.discordapp.com/avatars/595363392886145046/6346f94881fd9672ea07b76b30c3b819.webp?size=256'};

    constructor() {
    }

    ngOnInit(): void {
        console.log(this.warn)
    }

}
